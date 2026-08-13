from enum import StrEnum

from sqlmodel import Field, SQLModel

from app.game_rules import PersonalTaskType, WorkMode
from app.models import Process


class NationCreate(SQLModel):
    name: str
    population: int = Field(ge=0)
    resources: dict[str, float] = Field(default_factory=dict)
    influence: int = Field(default=0, ge=0)
    housing_capacity: int = Field(default=0, ge=0)


class ProcessStatus(StrEnum):
    ACTIVE = "active"
    STOPPED = "stopped"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProcessCreate(SQLModel):
    location_code: str
    work_type: str
    mode: WorkMode
    description: str = ""
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


class ResourcePurchase(SQLModel):
    resources: dict[str, int]


class LocationMapNodeInput(SQLModel):
    location_code: str
    x: float
    y: float


class LocationMapConnectionInput(SQLModel):
    source: str
    target: str
    source_handle: str | None = None
    target_handle: str | None = None


class LocationMapLayoutUpdate(SQLModel):
    nodes: list[LocationMapNodeInput]
    connections: list[LocationMapConnectionInput]


class ConstructionStart(SQLModel):
    location_code: str
    assigned_workers: int = Field(ge=1)


class BuildingAdd(SQLModel):
    location_code: str


class DiscoveryStart(SQLModel):
    assigned_workers: int = Field(ge=1, le=3)


class PersonalTaskCreate(SQLModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1)
    reward: int = Field(ge=0)
    task_type: PersonalTaskType


class PersonalTaskAction(StrEnum):
    CANCEL = "cancel"
    DONE = "done"
    RESTART = "restart"
    CONTINUE = "continue"
