from enum import StrEnum


class WorkIntensity(StrEnum):
    BASE = "BASE"
    LIGHT = "LIGHT"
    STANDARD = "STANDARD"
    MEDIUM = "MEDIUM"
    HEAVY = "HEAVY"

    @property
    def coefficient(self) -> float:
        return {"BASE": 1, "LIGHT": 1.5, "STANDARD": 2, "MEDIUM": 2.5, "HEAVY": 3}[self]


class WorkMode(StrEnum):
    CONTINUOUS = "continuous"
    FINITE = "finite"


class BuildingType(StrEnum):
    HOUSING = "housing"
    WAREHOUSE = "warehouse"
    PIER = "pier"


class ItemVisualType(StrEnum):
    ICON = "icon"
    ILLUSTRATION = "illustration"


class PersonalTaskType(StrEnum):
    ONE_TIME = "one_time"
    PERIODIC = "periodic"
    INFINITE = "infinite"


class PersonalTaskStatus(StrEnum):
    ACTIVE = "active"
    DONE = "done"
    CANCELLED = "cancelled"
