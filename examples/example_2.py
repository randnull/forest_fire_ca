from wui_from_osm import load_wui_from_osm
from model.main import WUIModel
from models import WeatherType
from model.visualize import plot_colormap_fire

H, W, forest_mask, incomb_mask, houses = load_wui_from_osm("...")

model = WUIModel(
    height=H,
    width=W,
    forest_mask=forest_mask,
    incombustible_mask=incomb_mask,
    houses=houses,
    wind_speed=8.0,
    weather_type=WeatherType.NEUTRAL
)
ignitions = [(160, 110)]

model.ignite_forest(ignitions[0])

saves = model.run(total_minutes=1000)

plot_colormap_fire(saves, H, W, ignitions)
