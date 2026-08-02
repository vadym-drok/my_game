from sqlmodel import Field, SQLModel

from app.game_rules import WorkType


class SettlementCreate(SQLModel):
    name: str
    population: int = Field(ge=0)
    food: float = Field(default=0, ge=0)
    wood: int = Field(default=0, ge=0)
    stone: int = Field(default=0, ge=0)
    influence: int = Field(default=0, ge=0)
    housing_capacity: int = Field(default=0, ge=0)


class DayAdvance(SQLModel):
    assignments: dict[WorkType, int] = Field(default_factory=dict)
