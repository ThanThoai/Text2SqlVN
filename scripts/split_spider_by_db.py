import json
import os
import argparse

from collections import defaultdict
from typing import List, Dict
import tqdm

def write_libsonnet(split_name, list : List) -> None:
    def strings(s, tab = "") -> str:
        return tab + s  + "\n"
    with open(os.path.join("./data", split_name + '.libsonnet'), 'w') as wr:
        wr.write(strings("local databases = ["))
        wr.write(strings(s = "local databases = [", tab = '   '))
        for l in list:
            wr.write(strings(s = "'" + str(l) +"''", tab='    '))
        wr.write(strings(s = "]", tab="  "))
        wr.write(strings(s = "name: 'text2sqlvi',", tab="  "))
        wr.write(strings(s = "paths: [", tab=" "))
        wr.write(strings(s = "prefix + 'database/%s/examples.json' % [db]", tab="  "))
        wr.write(strings(s = "for db in databases", tab="  "))
        wr.write(strings(s = "],", tab=" "))
        wr.write(strings(s = "tables_paths: [", tab=" "))
        wr.write(strings(s = "prefix + 'database/%s/tables.json' % [db]", tab="  "))
        wr.write(strings(s = "for db in databases", tab="  "))
        wr.write(strings(s = "],", tab=" "))
        wr.write(strings(s = "db_path: prefix + 'database'", tab=" "))
        wr.write(strings(s = "}", tab=""))


def main(spider_path, duorat_path) -> None:

    def mkdir_p(path):
        if not os.path.isdir(path):
            os.mkdir(path)

    tables_json_path = "tables.json"
    examples_paths = ["train.json", "dev.json", "test.json"]

    with open(os.path.join(spider_path, tables_json_path), "r") as read_fp:
        payload: List[dict] = json.load(read_fp)

    grouped_payload: Dict[str, dict] = {}
    for item in payload:
        db_id: str = item['db_id']
        assert db_id not in grouped_payload
        grouped_payload[db_id] = item

    for db_id, item in tqdm.tqdm(grouped_payload.items()):
        mkdir_p(os.path.join(duorat_path, db_id))
        with open(os.path.join(duorat_path, db_id, "tables.json"), "wt") as write_fp:
            json.dump([item], write_fp, indent=2, ensure_ascii= False)

    for examples_path in examples_paths:
        with open(os.path.join(spider_path, examples_path), "r") as read_fp:
            payload: List[dict] = json.load(read_fp)

        grouped_payload: Dict[str, List[dict]] = defaultdict(list)
        for item in payload:
            db_id: str = item['db_id']
            grouped_payload[db_id].append(item)
        write_libsonnet(split_name = examples_path.split(".")[0], list = list(grouped_payload.keys()))
        for db_id, payload_group in tqdm.tqdm(grouped_payload.items()):
            mkdir_p(os.path.join(duorat_path, db_id))
            with open(os.path.join(duorat_path, db_id, "examples.json"), "wt") as write_fp:
                json.dump(payload_group, write_fp, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--spider-path", type=str, default='dataset/data')
    parser.add_argument("--duorat-path", type=str, default='dataset/database')
    args = parser.parse_args()

    main(args.spider_path, args.duorat_path)
