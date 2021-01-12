import abc
import functools
import os
import time
from typing import Dict
import bpemb
import corenlp
import torch
import torchtext
import datetime
from ratsql.resources import corenlp
from ratsql.utils import registry
from fairseq.data.encoders.fastbpe import fastBPE
from fairseq.models.roberta import RobertaModel
from vncorenlp import VNCoreNLP

class Embedder(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def tokenize(self, sentence):
        '''Given a string, return a list of tokens suitable for lookup.'''
        pass

    @abc.abstractmethod
    def untokenize(self, tokens):
        '''Undo tokenize.'''
        pass

    @abc.abstractmethod
    def lookup(self, token):
        '''Given a token, return a vector embedding if token is in vocabulary.

        If token is not in the vocabulary, then return None.'''
        pass

    @abc.abstractmethod
    def contains(self, token):
        pass

    @abc.abstractmethod
    def to(self, device):
        '''Transfer the pretrained embeddings to the given device.'''
        pass


@registry.register('word_emb', 'glove')
class GloVe(Embedder):

    def __init__(self, kind, lemmatize=False):
        cache = os.path.join(os.environ.get('CACHE_DIR', os.getcwd()), '.vector_cache')
        self.glove = torchtext.vocab.GloVe(name=kind, cache=cache)
        self.dim = self.glove.dim
        self.vectors = self.glove.vectors
        self.lemmatize = lemmatize
        self.corenlp_annotators = ['tokenize', 'ssplit']
        if lemmatize:
            self.corenlp_annotators.append('lemma')

    @functools.lru_cache(maxsize=1024)
    def tokenize(self, text):
        ann = corenlp.annotate(text, self.corenlp_annotators)
        if self.lemmatize:
            return [tok.lemma.lower() for sent in ann.sentence for tok in sent.token]
        else:
            return [tok.word.lower() for sent in ann.sentence for tok in sent.token]
    
    @functools.lru_cache(maxsize=1024)
    def tokenize_for_copying(self, text):
        ann = corenlp.annotate(text, self.corenlp_annotators)
        text_for_copying = [tok.originalText.lower() for sent in ann.sentence for tok in sent.token]
        if self.lemmatize:
            text = [tok.lemma.lower() for sent in ann.sentence for tok in sent.token]
        else:
            text = [tok.word.lower() for sent in ann.sentence for tok in sent.token]
        return text, text_for_copying

    def untokenize(self, tokens):
        return ' '.join(tokens)

    def lookup(self, token):
        i = self.glove.stoi.get(token)
        if i is None:
            return None
        return self.vectors[i]

    def contains(self, token):
        return token in self.glove.stoi

    def to(self, device):
        self.vectors = self.vectors.to(device)


@registry.register('word_emb', 'bpemb')
class BPEmb(Embedder):
    def __init__(self, dim, vocab_size, lang='en'):
        self.bpemb = bpemb.BPEmb(lang=lang, dim=dim, vs=vocab_size)
        self.dim = dim
        self.vectors = torch.from_numpy(self.bpemb.vectors)

    def tokenize(self, text):
        return self.bpemb.encode(text)

    def untokenize(self, tokens):
        return self.bpemb.decode(tokens)

    def lookup(self, token):
        i = self.bpemb.spm.PieceToId(token)
        if i == self.bpemb.spm.unk_id():
            return None
        return self.vectors[i]

    def contains(self, token):
        return self.lookup(token) is not None

    def to(self, device):
        self.vectors = self.vectors.to(device)


class Tokenizer:

    def __init__(self, path = './vncorenlp/VnCoreNLP-1.1.1.jar'):

        self.path = path 
        self.rdrsegenter = VnCoreNLP(self.path, annotators="wseg", max_heap_size='-Xmx500m')

    def tokenizer(self, sentences, return_string = False):
        
        re_sentences = self.rdrsegenter.tokenize(sentences)
        if return_string:
            return " ".join([s for s in re_sentences])
        return re_sentences



class BPE_BASE():
    bpe_codes = "./PhoBERT_base_fairseq/bpe.codes"

class BPE_LARGE():
    bpe_codes = "./PhoBERT_large_fairseq/bpe.codes"


@registry.register("word_emb", "phoBert")
class phoBert(Embedder):
    
    def __init__(self, BERT_MODEL, write_file = True):
        
        self.method = BERT_MODEL
        self.dict_model = {
            "BERT_BASE" : {
                "NAME" : "./PhoBERT_base_fairseq",
                "PATH_CHECKPOINT_FILE" : "model.pt"
            },

            "BERT_LARGE" : {
                "NAME" : "./PhoBERT_large_fairseq",
                "PATH_CHECKPOINT_FILE" : "model.pt"
            }

        }
        assert self.method in self.dict_model.keys(), "[ERROR] Method {} not supported!!!!".format(self.method)
        self.pho_bert = RobertaModel(self.dict_model[self.method]["NAME"], self.dict_model[self.method]["PATH_CHECKPOINT_FILE"])
        self.tokenize = Tokenizer()
        self.pho_bert.eval()
        if self.method == "BERT_BASE":
            args = BPE_BASE()
        else:
            args = BPE_LARGE()
        self.pho_bert.bpe = fastBPE(args)
        self.embeding = {}
        self.write_file = write_file

    def run(self, data : List[Dict]) -> None:
        print(datetime.now().strftime("%H:%M:%S"), f"\t INFO: Extract Features using BERT: {self.method}")
        for d in tqdm.tqdm(data):
            key = d['question_id']
            assert key not in self.embeding.keys(), "ERROR"
            question = self.tokenize.tokenizer(d["question"], return_string = True)
            token_idx = self.pho_bert.encode(question)
            doc = self.pho_bert.extract_features_aligned_to_words(question)
            self.embeding[key] = {
                "vector" : {},
                "idx_token" : token_idx[1:-1]
            }
            for tok in doc[1: -1]:
                self.embeding[key]["vector"][str(tok)] = tok.vector
        
        if self.write_file:
            path = "./dataset/text/extract_bert"
            print(datetime.now().strftime("%H:%M:%S"), f"\t INFO: Saving extract features to file")
            torch.save(self.embeding, os.path.join(path, self.method + '.pt'))


    def extract(self, question: str) -> Dict:
        result = {}
        doc = self.pho_bert.extract_features_aligned_to_words(self.tokenize.tokenizer(question))
        for tok in doc[1: len(doc) - 1]:
            result[tok] = tok.vector
        return result