import random
import numpy as np
import osmnx as ox
import rasterio
from rasterio.features import rasterize
from models.cell_types import UrbanCell
from models import HouseMaterial

def load_buildings(place: str):
    gdf = ox.features_from_place(place, tags={"building": True})
    gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])].copy()
    gdf = gdf.explode(index_parts=False)

    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)

    gdf_utm = gdf.to_crs(gdf.estimate_utm_crs())
    print(gdf.estimate_utm_crs())
    return gdf_utm


def make_grid(buildings, cell_length):
    minx, miny, maxx, maxy = buildings.total_bounds

    W = int((maxx - minx) / cell_length) + 1
    H = int((maxy - miny) / cell_length) + 1

    transform = rasterio.transform.from_origin(
        minx, maxy, cell_length, cell_length
    )
    return H, W, transform


def rasterize_buildings(buildings, H, W, transform):
    return rasterize(
        [(geom, i + 1) for i, geom in enumerate(buildings.geometry)],
        out_shape=(H, W),
        transform=transform,
        fill=0,
        dtype=np.int32
    )


def make_houses(house_raster):
    houses = []

    if house_raster.max() == 0:
        return houses

    for i in range(1, house_raster.max() + 1):
        ys, xs = np.where(house_raster == i)
        if len(xs) == 0:
            continue

        cells = [(int(y), int(x)) for y, x in zip(ys, xs)]

        material = random.choices(
            [HouseMaterial.WOOD,
             HouseMaterial.FIRE_PRE_WOOD,
             HouseMaterial.FIREPROOF],
            weights=[0.6, 0.3, 0.1]
        )[0]

        houses.append(UrbanCell(cells=cells, material=material))

    return houses


def rasterize_roads(place, H, W, transform, utm_crs):
    roads = ox.features_from_place(place, tags={"highway": True})

    if roads.crs is None:
        roads = roads.set_crs(epsg=4326)

    roads = roads.to_crs(utm_crs)

    return rasterize(
        [(geom, 1) for geom in roads.geometry],
        out_shape=(H, W),
        transform=transform,
        fill=0
    ).astype(bool)


def load_wui_from_osm(place, cell_length):
    buildings = load_buildings(place)

    H, W, transform = make_grid(buildings, cell_length)

    house_raster = rasterize_buildings(buildings, H, W, transform)
    houses = make_houses(house_raster)

    forest_mask = np.ones((H, W), dtype=bool)
    incomb_mask = rasterize_roads(
        place, H, W, transform, buildings.crs
    )

    return H, W, forest_mask, incomb_mask, houses
