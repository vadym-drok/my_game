from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Settlement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    population: int = 0
    current_day: int = 0
    food: float = 0
    wood: int = 0
    stone: int = 0
    influence: int = 0
    housing_capacity: int = 0


class DayReport(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    settlement_id: int = Field(foreign_key="settlement.id", index=True)
    day_number: int
    population: int
    food: float
    wood: int
    stone: int
    influence: int
    food_produced: float
    food_consumed: float
    workers_summary: dict[str, int] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    notes: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
