from enum import Enum


class HouseMaterial(Enum):
    WOOD = 0
    FIRE_PRE_WOOD = 1
    FIREPROOF = 2

MaterialMap = {
    HouseMaterial.WOOD: 1.0,
    HouseMaterial.FIRE_PRE_WOOD: 0.8,
    HouseMaterial.FIREPROOF: 0.6,
}