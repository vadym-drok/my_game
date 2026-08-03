from enum import StrEnum

from sqlmodel import Field, SQLModel

from app.game_rules import WorkType
from app.models import Process


class NationCreate(SQLModel):
    name: str
    population: int = Field(ge=0)
    food: float = Field(default=0, ge=0)
    general_points: int = Field(default=0, ge=0)
    wood: int = Field(default=0, ge=0)
    stone: int = Field(default=0, ge=0)
    influence: int = Field(default=0, ge=0)
    housing_capacity: int = Field(default=0, ge=0)


class ProcessMode(StrEnum):
    CONTINUOUS = "continuous"
    FINITE = "finite"


class ProcessStatus(StrEnum):
    ACTIVE = "active"
    STOPPED = "stopped"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProcessCreate(SQLModel):
    name: str
    work_type: WorkType
    mode: ProcessMode
    assigned_workers: int = Field(default=0, ge=0)
    required_worker_days: int | None = Field(default=None, ge=1)
    details: dict = Field(default_factory=dict)


class ProcessUpdate(SQLModel):
    assigned_workers: int | None = Field(default=None, ge=0)
    status: ProcessStatus | None = None


class PopulationGrowth(SQLModel):
    amount: int = Field(ge=0)


class ResourceAdjustment(SQLModel):
    amount: int
