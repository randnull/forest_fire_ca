from enum import IntEnum
from dataclasses import dataclass

from models import ForestState, UrbanState
from models.materials_models import HouseMaterial


class CellType(IntEnum):
    EMPTY = 0
    FOREST = 1
    URBAN = 2


@dataclass
class ForestCell:
    state: ForestState = ForestState.SF0
    C: float = 0.0
    time_of_state: float = 0.0


@dataclass
class UrbanCell:
    state: UrbanState = UrbanState.SU0
    material: HouseMaterial = HouseMaterial.WOOD
    time_of_state: float = 0.0

    t12: float = 0.0
    t23: float = 0.0
    t34: float = 0.0
    t45: float = 0.0