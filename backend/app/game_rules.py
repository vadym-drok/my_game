from enum import Enum, StrEnum


BASE_FOOD_SPENDING = 1


class WorkIntensity(float, Enum):
    BASE = 1
    LIGHT = 1.5
    STANDARD = 2
    MEDIUM = 2.5
    HEAVY = 3


class WorkType(StrEnum):
    HUNTING = "hunting"
    FOOD_GATHERING = "food_gathering"
    FISHING = "fishing"
    WOODCUTTING = "woodcutting"
    BUILDING = "building"
    INVESTIGATION = "investigation"
    MINING = "mining"


WORK_INTENSITY = {
    WorkType.HUNTING: WorkIntensity.BASE,
    WorkType.FOOD_GATHERING: WorkIntensity.BASE,
    WorkType.FISHING: WorkIntensity.BASE,
    WorkType.WOODCUTTING: WorkIntensity.STANDARD,
    WorkType.BUILDING: WorkIntensity.LIGHT,
    WorkType.INVESTIGATION: WorkIntensity.STANDARD,
    WorkType.MINING: WorkIntensity.HEAVY,
}

WORK_OUTPUTS = {
    WorkType.HUNTING: {"food": 3},
    WorkType.FOOD_GATHERING: {"food": 2},
    WorkType.FISHING: {"food": 3},
    WorkType.WOODCUTTING: {"wood": 1},
    WorkType.MINING: {"stone": 1},
}
