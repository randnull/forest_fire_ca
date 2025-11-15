import datetime
import math
from datetime import time

import numpy as np
from matplotlib import pyplot as plt, patches

from models import ForestState

def plot_colormap_fire(saves, H, W, ignition=[]):
    bins = (0, 10, 15, 20, 25, 50, 60, 70, 80, 100, 200, 500, 700, 800, 1500, 2500)
    map_fire_by_time = np.full((H, W), np.inf, dtype=np.float32)

    for t, forest_state, _ in saves:
        next_fire = (forest_state >= ForestState.SF2) & np.isinf(map_fire_by_time)
        map_fire_by_time[next_fire] = t

    _, _, houses = saves[-1]

    for h in houses:
        y1, x1 = h.cells[0]
        y2, x2 = h.cells[1]
        map_fire_by_time[y1:y2, x1:x2] = None

    Z = np.full((H, W), np.nan, dtype=float)

    for y in range(H):
        for x in range(W):
            for i in range(len(bins) - 1):
                if bins[i] <= map_fire_by_time[y, x] < bins[i+1]:
                    Z[y, x] = i
                    break
    # print(Z)

    plt.figure()
    X, Y = np.meshgrid(np.arange(W+1), np.arange(H+1))
    im = plt.pcolormesh(X, Y, Z, shading='auto', cmap='Reds_r')
    cbar = plt.colorbar(im)
    cbar.set_label('Время (мин) до активного огня')
    tick_pos = [i for i in range(len(bins) - 1)]
    tick_lbl = [b for b in bins[:-1]]
    cbar.set_ticks(tick_pos)
    cbar.set_ticklabels(tick_lbl)

    for h in houses:
        y1, x1 = h.cells[0]
        y2, x2 = h.cells[1]
        rect = patches.Rectangle(
            (x1, y1),
            x2 - x1,
            y2 - y1,
            fill=False,
            edgecolor="black",
            linewidth=1
        )
        plt.gca().add_patch(rect)

    if ignition is not None:
        for (iy, ix) in ignition:
            plt.plot([ix], [iy], marker='^')

    file_to_save = "save" + str(datetime.datetime.now()) + ".png"
    plt.title('Карта мест пожара по времени')
    plt.savefig(file_to_save, dpi=160)
    print(f"[saved] {file_to_save}")

