from sqlmodel import Field, SQLModel


class Settlement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    population: int = 0

