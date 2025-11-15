import math
from dataclasses import dataclass
from typing import List, Tuple

from models.state_models import ForestState, UrbanState
from models.materials_models import HouseMaterial


@dataclass
class ForestCell:
    state: ForestState = ForestState.SF0
    C: float = 0.0
    time_of_state: float = 0.0
    Rmax_per_min: float = 0.0


@dataclass
class UrbanCell:
    cells: List[Tuple[int, int]]

    state: UrbanState = UrbanState.SU0
    material: HouseMaterial = HouseMaterial.WOOD
    time_of_state: float = 0.0

    t12: float = 0.0
    t23: float = 0.0
    t34: float = 0.0
    t45: float = 0.0

    def get_area(self):
        x1, y1 = self.cells[0]
        x2, y2 = self.cells[1]

        return math.fabs(x2 - x1) * math.fabs(y2 - y1)

