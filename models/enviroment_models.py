from enum import Enum


class WeatherType(Enum):
    ADVANTAGE = 0
    NEUTRAL = 1
    DISADVANTAGE = 2

WeatherMap = {
    WeatherType.ADVANTAGE: 1.0,
    WeatherType.NEUTRAL: 0.8,
    WeatherType.DISADVANTAGE: 0.4,
}