from datetime import date, datetime

from sqlalchemy import JSON, Column, UniqueConstraint
from pydantic import field_validator
from sqlmodel import Field, SQLModel

from app.game_rules import BuildingType, WorkIntensity, WorkMode


class Resource(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("code"),)

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True)
    name: str
    storage_coefficient: float = 1


class WorkTypeDefinition(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("code"),)

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True)
    name: str
    intensity: WorkIntensity
    mode: str
    outputs: dict[str, float] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        return WorkMode(value).value


class BuildingDefinition(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("code"),)

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True)
    name: str
    building_type: str
    capacity: int = 0

    @field_validator("building_type")
    @classmethod
    def validate_building_type(cls, value: str) -> str:
        return BuildingType(value).value


class Nation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    population: int = 0
    start_date: date = Field(default_factory=date.today)
    last_population_growth_date: date | None = None
    population_growth_progress: int = 0
    consecutive_hunger_days: int = 0
    influence: int = 0
    housing_capacity: int = 0


class DayReport(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("nation_id", "report_date"),)

    id: int | None = Field(default=None, primary_key=True)
    nation_id: int = Field(foreign_key="nation.id", index=True)
    report_date: date
    population: int
    influence: int
    food_shortage: float = 0
    is_hungry: bool = False
    resources: dict[str, dict[str, float]] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    workers_summary: dict[str, int] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    processes_summary: list[dict] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
    notes: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))


class NationLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nation_id: int = Field(foreign_key="nation.id", index=True)
    message: str
    amount: float
    created_at: datetime = Field(default_factory=datetime.now)


class NationResource(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("nation_id", "resource_id"),)

    id: int | None = Field(default=None, primary_key=True)
    nation_id: int = Field(foreign_key="nation.id", index=True)
    resource_id: int = Field(foreign_key="resource.id", index=True)
    amount: float = 0


class Process(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nation_id: int = Field(foreign_key="nation.id", index=True)
    name: str
    work_type: str
    mode: str
    status: str = "active"
    assigned_workers: int = 0
    required_worker_days: int | None = None
    completed_worker_days: int = 0
    started_at: date = Field(default_factory=date.today)
    completed_at: date | None = None
    details: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
