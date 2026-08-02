from dataclasses import dataclass
from enum import StrEnum


class WorkIntensity(StrEnum):
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"


class WorkType(StrEnum):
    FOOD_GATHERING = "food_gathering"
    HUNTING = "hunting"
    WOODCUTTING = "woodcutting"
    BUILDING = "building"


@dataclass(frozen=True)
class WorkInfo:
    intensity: WorkIntensity
    food_per_worker: float = 0
    wood_per_worker: int = 0


FOOD_MULTIPLIERS = {
    WorkIntensity.LIGHT: 1.0,
    WorkIntensity.MEDIUM: 1.25,
    WorkIntensity.HEAVY: 1.5,
}

WORKS = {
    WorkType.FOOD_GATHERING: WorkInfo(WorkIntensity.LIGHT, food_per_worker=2),
    WorkType.HUNTING: WorkInfo(WorkIntensity.MEDIUM, food_per_worker=3),
    WorkType.WOODCUTTING: WorkInfo(WorkIntensity.HEAVY, wood_per_worker=1),
    WorkType.BUILDING: WorkInfo(WorkIntensity.MEDIUM),
}
