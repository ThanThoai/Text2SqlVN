from dataclasses import dataclass
from typing import Optional

import sys
import os
sys.path.insert(1, os.getcwd())
from duorat.asdl.asdl import Field
from duorat.asdl.transition_system import Pos, Action


@dataclass(order=True, frozen=True)
class ActionInfo(object):
    """sufficient statistics for making a prediction of an action at a time step"""

    action: Action
    parent_pos: Optional[Pos]
    frontier_field: Optional[Field]
