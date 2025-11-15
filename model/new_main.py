import math
from copy import deepcopy
from typing import List

import numpy as np
import random

import utils
from models import ForestState, UrbanState, HouseMaterial, MaterialMap, WeatherType, WeatherMap
from models.cell_types import UrbanCell

r = []
class WUIModel:
    def __init__(self,
                 height: int,
                 width: int,
                 forest_mask: np.ndarray,
                 incombustible_mask: np.ndarray,
                 houses: List[UrbanCell],
                 temperature: float = 20.0,
                 wind_speed: float = 5.0,
                 relative_humidity: float = 30.0,
                 cell_length: float = 30.0,
                 wind_direction: float = 0.0,
                 weather_type: WeatherType = WeatherType.NEUTRAL
                 ):

        self.H = height
        self.W = width
        self.temperature = temperature
        self.wind_speed = wind_speed
        self.relative_humidity = relative_humidity
        self.cell_length = cell_length
        self.wind_direction = wind_direction
        self.weather_type = weather_type

        self.forest_mask = forest_mask.astype(bool)
        self.incomb_mask = incombustible_mask.astype(bool)
        self.state_forest = np.full((self.H,self.W), ForestState.SF4, dtype=np.int8)
        self.C = np.zeros((self.H,self.W), dtype=np.float32)

        self.time_SF1_SF2 = np.full((self.H,self.W), np.inf, dtype=np.float32)

        self.houses = houses


        self.house_index_grid = np.full((self.H,self.W), -1, dtype=np.int8)
        self.house_grid_mask = np.zeros((self.H,self.W),  dtype=np.bool)

        for i, house in enumerate(self.houses):
            y1, x1, y2, x2 = house.cells[0][0], house.cells[0][1], house.cells[1][0], house.cells[1][1]

            self.house_index_grid[y1:y2, x1:x2] = i
            self.house_grid_mask[y1:y2, x1:x2] = True


        burnable = self.forest_mask & (~self.incomb_mask)
        self.state_forest[burnable] = ForestState.SF0
        # self.state_forest[5, 5] = ForestState.SF2
        # self.state_forest[40, 50] = ForestState.SF2

        # self.state_forest[1, 2] = ForestState.SF2
        # self.state_forest[3, 2] = ForestState.SF2
        # self.state_forest[2, 1] = ForestState.SF2
        # self.state_forest[2, 3] = ForestState.SF2
        # self.state_forest[3, 3] = ForestState.SF2
        # self.state_forest[3, 1] = ForestState.SF2
        # self.state_forest[1, 1] = ForestState.SF2


    def _calculate_initial_state(self) -> None:
        self.R0 = self._R0_forest_calculate()
        self.dir_R = self._R_calculate(self.R0)
        self.Rmax = np.max(self.dir_R)
        self.dt_min = self._dt_min_calculate(self.Rmax)

    def ignite_forest(self, cell):
        # print(cell)
        self.state_forest[cell] = ForestState.SF2

    def ignite_house(self, house_id: int):
        house = self.houses[house_id]
        self._generate_house_transfer_time(house)
        house.time_of_state = 0.0
        house.state = UrbanState.SU3 # 1

    def _generate_house_transfer_time(self, u: UrbanCell) -> None:
        house_material: HouseMaterial = u.material

        u.t12 = random.randint(4, 6)
        u.t23 = random.randint(5, 8)

        if house_material == HouseMaterial.WOOD:
            u.t34 = random.randint(10, 20)
            u.t45 = random.randint(20, 30)

        if house_material == HouseMaterial.FIRE_PRE_WOOD:
            u.t34 = random.randint(20, 30)
            u.t45 = random.randint(30, 40)

        if house_material == HouseMaterial.FIREPROOF:
            u.t34 = random.randint(30, 40)
            u.t45 = random.randint(50, 60)

    def _R0_forest_calculate(self) -> float:
        R0 = 0.03 * self.temperature + \
             0.05 * self.wind_speed + \
             0.01 * (100 - self.relative_humidity) - 0.3

        return R0

    def _R_calculate(self, R0: float) -> np.ndarray:
        tmp_dirs = np.array([1, 1, 1, 1, 1, 1, 1, 1])

        Kw = 1.0 # в идеале это должно быть функцией конечно, но для простоты пока так
        Ks = 1.0
        Kf = 1.0

        return R0 * Kw * Ks * Kf * tmp_dirs

    def _dt_min_calculate(self, Rmax: float) -> float:
        return utils.k * self.cell_length / Rmax

    def step(self) -> None:
        new_SF1 = self._SFO_to_SF1()
        new_SF2 = self._SF1_to_SF2()
        new_SF3 = self._SF2_to_SF3()
        new_SF4 = self._SF3_to_SF4()

        if np.any(new_SF1):
            self.state_forest[new_SF1] = ForestState.SF1
            R_in = self.Rmax
            self.time_SF1_SF2[new_SF1] = self.cell_length / R_in / math.sqrt(math.pi)

        self.state_forest[new_SF2] = ForestState.SF2
        self.C[new_SF2] = 0.0
        self.time_SF1_SF2[new_SF2] = np.inf

        self.state_forest[new_SF3] = ForestState.SF3

        self.state_forest[new_SF4] = ForestState.SF4

        self._house_progress()

        self._house_to_forest()
        self._forest_to_house()

    def _SFO_to_SF1(self):
        SF0_cells = (self.state_forest == ForestState.SF0)
        C_coeffs_current = np.zeros_like(self.C)
        SF2_neigbours = np.zeros_like(SF0_cells)

        for i, (dy, dx) in enumerate(utils.DIRECTIONS):
            translation_matrix = np.zeros_like(SF0_cells)

            if dy >= 0:
                ys = slice(dy, None)
                yd = slice(0, self.H-dy)
            else:
                ys = slice(0, dy)
                yd = slice(-dy, None)
            if dx >= 0:
                xs = slice(dx, None)
                xd = slice(0, self.W-dx)
            else:
                xs = slice(0, dx)
                xd = slice(-dx, None)

            translation_matrix[yd, xd] = (self.state_forest[ys, xs] == ForestState.SF2)
            SF2_neigbours += translation_matrix

            if i in [1, 3, 5, 7]:
                new_C = self.dir_R[i] * (self.dt_min / math.sqrt(2.0)) / self.cell_length
            else:
                new_C = self.dir_R[i] * self.dt_min / self.cell_length

            C_coeffs_current[yd, xd] += new_C * translation_matrix[yd, xd]

        results = SF0_cells & SF2_neigbours
        self.C[results] += C_coeffs_current[results]

        is_burned = self.C >= 1
        burned_now = results & is_burned

        return burned_now


    def _SF1_to_SF2(self):
        actual_SF1 = (self.state_forest == ForestState.SF1)
        self.time_SF1_SF2[actual_SF1] -= self.dt_min

        swithced_to_SF2 = self.time_SF1_SF2 <= 0.0

        swithced_only_now = swithced_to_SF2 & actual_SF1

        return swithced_only_now


    def _SF2_to_SF3(self):
        SF2_cells = (self.state_forest == ForestState.SF2)
        surrounded = np.ones_like(SF2_cells)

        for i, (dy, dx) in enumerate(utils.DIRECTIONS):
            translation_matrix = np.zeros_like(SF2_cells)

            if dy >= 0:
                ys = slice(dy, None)
                yd = slice(0, self.H - dy)
            else:
                ys = slice(0, dy)
                yd = slice(-dy, None)
            if dx >= 0:
                xs = slice(dx, None)
                xd = slice(0, self.W - dx)
            else:
                xs = slice(0, dx)
                xd = slice(-dx, None)

            translation_matrix[yd, xd] = ((self.state_forest[ys, xs] == ForestState.SF0) | (self.state_forest[ys, xs] == ForestState.SF1))
            surrounded[yd, xd] *= ~translation_matrix[yd, xd]

        SF_2_and_surrounded = (SF2_cells & surrounded)
        return SF_2_and_surrounded


    def _SF3_to_SF4(self):
        return self.state_forest == ForestState.SF3


    def _calculate_d(self, u: UrbanCell) -> float:
        A = u.get_area() * self.cell_length**2
        return math.sqrt(A)

    def _calculate_v_a_b_c(self, v: float, d: float):
        a = 0.6 * v + 3 + 0.5 * d
        b = - 2/15.0 * v + 3 + 0.5 * d
        c = - 1/15.0 * v + 3 + 0.5 * d

        return a, b, c


    def _candidates_for_ignite_by_house(self, a, b, c, start, end):
        global r
        a_norm = a / self.cell_length
        b_norm = b / self.cell_length
        c_norm = c / self.cell_length

        max_dc = int(max(a_norm, b_norm, c_norm)) + 1
        moore_direction = utils.DIRECTIONS[int(self.wind_direction % 360.0 // 45)]

        candidates = list()
        # print(start, end, '123123123123')
        center_x = (start[1] + end[1]) // 2
        center_y = (start[0] + end[0]) // 2
        # print(moore_direction)
        # print(start, end)
        # print(center_x, center_y)
        for dx in range(-max_dc, max_dc + 1):
            for dy in range(-max_dc, max_dc + 1):
                new_y = center_y + dy
                new_x = center_x + dx

                if not(0 <= new_y < self.H and 0 <= new_x < self.W):
                    continue

                # идем по направлению ветра по элипсу
                project_f = dx * moore_direction[1] + dy * moore_direction[0]
                project_l = dx * moore_direction[0] - dy * moore_direction[1]

                current_a = a_norm
                if project_f < 0:
                    current_a = c_norm

                result = (project_f / current_a)**2 + (project_l / b_norm)**2

                if result < 1.0:
                    candidates.append((new_y, new_x))
        r = candidates
        return candidates

    def _calculate_pwnm(self, influence_cells, house_cells):
        y1, x1 = house_cells[0]
        y2, x2 = house_cells[1]

        mask_tmp = np.zeros((self.H, self.W), dtype=bool)
        arr = np.asarray(influence_cells, dtype=int)
        ys, xs = arr[:, 0], arr[:, 1]
        mask_tmp[ys, xs] = True
        # print(mask_tmp[y1:y2, x1:x2])

        covered = int(mask_tmp[y1:y2, x1:x2].sum())
        area = (y2 - y1) * (x2 - x1)

        result = covered / area
        return result

    def _house_progress(self):
        for id_house, house in enumerate(self.houses):
            house.time_of_state += self.dt_min
            if house.state == UrbanState.SU1 and house.time_of_state >= house.t12:
                house.state = UrbanState.SU2
            if house.state == UrbanState.SU2 and house.time_of_state >= house.t23:
                house.state = UrbanState.SU3
            if house.state == UrbanState.SU3 and house.time_of_state >= house.t34:
                house.state = UrbanState.SU4
            if house.state == UrbanState.SU4 and house.time_of_state >= house.t45:
                house.state = UrbanState.SU5

            if house.state in {UrbanState.SU3, UrbanState.SU4}:
                d = self._calculate_d(house)
                v = self.wind_speed

                a,b,c = self._calculate_v_a_b_c(v, d)

                candidates = self._candidates_for_ignite_by_house(a,b,c, house.cells[0], house.cells[1])

                for (y,x) in candidates:
                    if self.house_grid_mask[y, x]:
                        index_of_house = self.house_index_grid[y, x]
                        if index_of_house == -1 or index_of_house == id_house:
                            continue

                        house_to_ignite = self.houses[index_of_house]
                        if house_to_ignite.state != UrbanState.SU0:
                            continue
                        PTn = MaterialMap[house_to_ignite.material]
                        PW = WeatherMap[self.weather_type]
                        PSn = 0.0
                        if house.state == UrbanState.SU3:
                            PSn = 0.3
                        else:
                            PSn = 1.0

                        PAmn = self._calculate_pwnm(candidates, house_to_ignite.cells)
                        print((y, x), self.house_grid_mask[y, x])
                        P = PTn * PW * PSn * PAmn
                        if random.random() < P:
                            self.ignite_house(index_of_house)

    def _house_to_forest(self):
        for house in self.houses:
            if house.state not in (UrbanState.SU3, UrbanState.SU4):
                continue
            d = self._calculate_d(house)
            v = self.wind_speed

            a, b, c = self._calculate_v_a_b_c(v, d)

            candidates = self._candidates_for_ignite_by_house(a, b, c, house.cells[0], house.cells[1])

            for (y,x) in candidates:
                if self.forest_mask[y,x] and (self.state_forest[y,x] == ForestState.SF0):

                    self.state_forest[y,x] = ForestState.SF1
                    R_in = self.Rmax
                    self.time_SF1_SF2[y,x] = self.cell_length / R_in / math.sqrt(math.pi)

    def _calculate_a_b_c_forest(self, v, d, k):
        a = (0.6 * v + 3.0) * k + d / 2.0
        b = (-2.0 / 15.0) * v + 3.0 + d / 2.0
        c = (-1.0 / 15.0) * v + 3.0 + d / 2.0
        return a, b, c

    def _forest_to_house(self):
        is_crown = self.Rmax >= utils.Rmax_per_K
        K_coef = utils.K_CF if is_crown else utils.K_SF
        SF2_cellls = np.argwhere(self.state_forest == ForestState.SF2)

        for (y, x) in SF2_cellls:
            a, b, c = self._calculate_a_b_c_forest(self.wind_speed, self.cell_length, K_coef)
            candidates = self._candidates_for_ignite_by_house(a, b, c, (y, x), (y, x))
            for (new_y, new_x) in candidates:
                if self.house_grid_mask[(new_y, new_x)]:
                    id_house = self.house_index_grid[(new_y, new_x)]
                    house_to_ignite = self.houses[id_house]
                    if house_to_ignite.state != UrbanState.SU0:
                        continue

                    PTn = MaterialMap[house_to_ignite.material]
                    PW = WeatherMap[self.weather_type]
                    PSn = 0.0
                    if is_crown:
                        PSn = 0.3
                    else:
                        PSn = 1.0
                    print((new_y, new_x), self.house_grid_mask[new_y, new_x], house_to_ignite.cells)
                    PAmn = self._calculate_pwnm(candidates, house_to_ignite.cells)

                    P = PTn * PW * PSn * PAmn
                    # print(PTn, PSn, PAmn, PW)
                    if random.random() < P:
                        self.ignite_house(id_house)

    def run(self, total_minutes: float) -> List:
        self._calculate_initial_state()
        t = 0.0
        saves = []
        # print(self.dir_R, self.Rmax, self.dt_min)
        while t < total_minutes:
            self.step()
            t += self.dt_min
            saves.append((t, self.state_forest.copy(), deepcopy(self.houses)))
        # print(self.state_forest)
        return saves

