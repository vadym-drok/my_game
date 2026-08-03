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
