from datetime import date, datetime

from sqlalchemy import JSON, Column, UniqueConstraint
from sqlmodel import Field, SQLModel


class Nation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    population: int = 0
    start_date: date = Field(default_factory=date.today)
    last_population_growth_date: date | None = None
    population_growth_progress: int = 0
    consecutive_hunger_days: int = 0
    food: float = 0
    general_points: int = 0
    wood: int = 0
    stone: int = 0
    influence: int = 0
    housing_capacity: int = 0


class DayReport(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("nation_id", "report_date"),)

    id: int | None = Field(default=None, primary_key=True)
    nation_id: int = Field(foreign_key="nation.id", index=True)
    report_date: date
    population: int
    food: float
    general_points: int
    wood: int
    stone: int
    influence: int
    food_produced: float
    food_consumed: float
    food_shortage: float = 0
    is_hungry: bool = False
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
    amount: int
    created_at: datetime = Field(default_factory=datetime.now)


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
