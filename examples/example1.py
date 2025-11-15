import numpy as np

from model.new_main import WUIModel
from model.visualize import plot_colormap_fire
from models import HouseMaterial, WeatherType
from models.cell_types import UrbanCell

H, W = 80, 80
L = 10

forest = np.ones((H, W), dtype=bool)
incombustible = np.zeros((H, W), dtype=bool)
incombustible[25,:] = True
incombustible[25,-1] = False

print(incombustible)
houses = [
    UrbanCell(
        cells=[(5, 5), (9, 9)],
        material=HouseMaterial.WOOD
    )
]

model = WUIModel(
    height=H,
    width=W,
    forest_mask=forest,
    incombustible_mask=incombustible,
    houses=houses,
    temperature=30.0,
    wind_speed=15.0,
    relative_humidity=20.0,
    wind_direction=30.0,
    cell_length=L,
    weather_type=WeatherType.NEUTRAL,
)

ignitions = [(2, 4)]

model.ignite_forest(ignitions[0])

saves = model.run(total_minutes=10000)

plot_colormap_fire(saves, H, W, ignitions)
