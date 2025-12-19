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

    def get_area(self) -> float:
        return float(len(set(self.cells)))
    
    def get_center(self) -> Tuple[int, int]:
        if not self.cells:
            return (0, 0)
        unique_cells = list(set(self.cells))
        ys = [y for y, _ in unique_cells]
        xs = [x for _, x in unique_cells]
        center_y = int(sum(ys) / len(ys))
        center_x = int(sum(xs) / len(xs))
        return (center_y, center_x)

