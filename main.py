import math
import random

import numpy as np


import utils
from models import ForestState, UrbanState, HouseMaterial
from models.cell_types import UrbanCell, ForestCell, CellType


class WUIModel:
    def __init__(self,
                 x_size: int,
                 y_size: int,
                 cell_length: float,
                 temperature: float,
                 wind_speed: float,
                 relative_humidity: float,
    ):
        self.x_size = x_size
        self.y_size = y_size
        self.cell_length = cell_length

        self.temperature = temperature
        self.wind_speed = wind_speed
        self.relative_humidity = relative_humidity

        self.grid = np.full((y_size, x_size), CellType.EMPTY, dtype=int)
        self.forest = [[ForestCell() for _ in range(x_size)] for _ in range(y_size)]
        self.urban = [[UrbanCell() for _ in range(x_size)] for _ in range(y_size)]

    def fill_forest_all(self) -> None:
        self.grid[:, :] = CellType.FOREST

    def _ignite_forest_cell(self, x: int, y: int) -> None:
        if self.grid[x][y] == CellType.FOREST:
            c = self.forest[x][y]
            c.state = ForestState.SF2
            c.time_of_state = 0.0

    def _ignite_urban_cell(self, x: int, y: int) -> None:
        if self.grid[x][y] == CellType.URBAN:
            u = self.urban[x][y]
            u.state = UrbanState.SU4
            u.time_of_state = 0.0
            self._generate_transfer_time(u)

    def _generate_transfer_time(self, u: UrbanCell) -> None:
        house_material: HouseMaterial = u.material

        u.t12 = random.randint(4, 6) * 60.0
        u.t23 = random.randint(5, 8) * 60.0

        if house_material == HouseMaterial.WOOD:
            u.t34 = random.randint(10, 20) * 60.0
            u.t45 = random.randint(20, 30) * 60.0

        if house_material == HouseMaterial.FIRE_PRE_WOOD:
            u.t34 = random.randint(20, 30) * 60.0
            u.t45 = random.randint(30, 40) * 60.0

        if house_material == HouseMaterial.FIREPROOF:
            u.t34 = random.randint(30, 40) * 60.0
            u.t45 = random.randint(50, 60) * 60.0

    def _R0_forest_calculate(self) -> float:
        R0 = 0.03 * self.temperature + \
             0.05 * self.wind_speed + \
             0.01 * (100 - self.relative_humidity) - 0.3

        return R0

    def _R_calculate(self,
                     x: int,
                     y: int,
                     dx: int,
                     dy: int) -> float:
        R0 = self._R0_forest_calculate()
        Kw = 1.0
        Ks = 1.0
        Kf = 1.0

        return R0 * Kw * Ks * Kf

    def _calculate_dt_forest(self, Rmax: float) -> float:
        if Rmax < utils.LOW_PARAMETER:
            return 60.0
        return utils.k * self.cell_length / Rmax * 60.0

    def _check_limitations(self, x, y):
        if 0 <= x <= self.x_size and 0 <= y <= self.y_size and \
                self.grid[x][y] == CellType.FOREST:
            return True
        return False

    def _calculate_Rin(self, x: int, y: int) -> float:
        return self._R_calculate(x, y, 0, 0)

    def run(self, total_time):
        current_time = 0.0

        while current_time < total_time:
            R_max = 0.0

            for y in range(self.y_size):
                for x in range(self.x_size):
                    if self.grid[y, x] != CellType.FOREST:
                        continue
                    local_max = 0.0
                    for dx, dy in utils.DIRECTIONS:
                        local_max = max(local_max, self._R_calculate(x, y, dx, dy))
                    self.forest[y][x].Rmax_per_min = local_max
                    R_max = max(R_max, local_max)
            dt = self._calculate_dt_forest(R_max)

            new_ignited_by_neigbours = set()
            SF1_states = []

            for y in range(self.y_size):
                for x in range(self.x_size):
                    if self.grid[y, x] != CellType.FOREST:
                        continue
                    forest_cell = self.forest[y][x]
                    if forest_cell.state == ForestState.SF0:
                        ostatok = 0.0
                        is_SF2_neig = False
                        for dx, dy in utils.DIRECTIONS:
                            new_x, new_y = x + dx, y + dy
                            if not self._check_limitations(new_x, new_y):
                                continue
                            neighbor_forest = self.forest[new_y][new_x]
                            R = self._R_calculate(x, y, dx, dy)
                            if neighbor_forest.state == ForestState.SF2:
                                is_SF2_neig = True
                            if dx != 0 and dy != 0:
                                ostatok += R * dt / 60.0 / math.sqrt(2.0) / self.cell_length
                            else:
                                ostatok += R * dt / 60.0 / self.cell_length
                        if is_SF2_neig:
                            forest_cell.C += ostatok
                            if forest_cell.C > 1.0:
                                SF1_states.append((x, y))
                                new_ignited_by_neigbours.add((x, y))
                    if forest_cell.state == ForestState.SF1:
                        RIN = self._calculate_Rin(x, y)



            current_time += dt

s = WUIModel(
    x_size=10,
    y_size=10,
    cell_length=10,
    temperature=10,
    wind_speed=10,
    relative_humidity=10)

s.fill_forest_all()

s.run(6 * 3600)