from datetime import date, datetime

from sqlalchemy import JSON, Column, Enum, UniqueConstraint
from pydantic import field_validator, model_validator
from sqlmodel import Field, SQLModel

from app.game_rules import BuildingType, ItemVisualType, PersonalTaskStatus, PersonalTaskType, WorkIntensity, WorkMode


class Resource(SQLModel, table=True):
    code: str = Field(primary_key=True)
    name: str
    order: int = 0
    storage_coefficient: float = 1
    is_system: bool = False
    image_path: str | None = None


class WorkTypeDefinition(SQLModel, table=True):
    code: str = Field(primary_key=True)
    name: str
    intensity: WorkIntensity
    mode: str
    outputs: dict[str, float] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    image_path: str | None = None

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        return WorkMode(value).value


class BuildingDefinition(SQLModel, table=True):
    code: str = Field(primary_key=True)
    name: str
    building_type: str
    capacity: int = 0
    image_path: str | None = None
    construction_cost: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    additional_data: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))

    @field_validator("building_type")
    @classmethod
    def validate_building_type(cls, value: str) -> str:
        return BuildingType(value).value

    @model_validator(mode="after")
    def validate_additional_data(self) -> "BuildingDefinition":
        if self.building_type == BuildingType.PIER:
            boats = self.additional_data.get("boats")
            if not isinstance(boats, dict) or not boats or any(
                not isinstance(code, str) or not isinstance(count, int) or isinstance(count, bool) or count < 0
                for code, count in boats.items()
            ):
                raise ValueError("Pier additional_data.boats must be a map of boat codes to non-negative counts")
        if self.building_type == BuildingType.PRODUCTION:
            processes = self.additional_data.get("process")
            if not isinstance(processes, dict) or not processes or any(
                not isinstance(code, str)
                or not isinstance(config, dict)
                or set(config) != {"multiplier", "workers"}
                or not isinstance(config["multiplier"], (int, float))
                or isinstance(config["multiplier"], bool)
                or config["multiplier"] <= 0
                or not isinstance(config["workers"], int)
                or isinstance(config["workers"], bool)
                or config["workers"] < 1
                for code, config in processes.items()
            ):
                raise ValueError("Production additional_data.process entries require positive multiplier and workers")
        return self


class Location(SQLModel, table=True):
    code: str = Field(primary_key=True)
    name: str
    image_path: str | None = None
    description: str = ""
    map_x: float = 0
    map_y: float = 0
    worker_days: int = Field(default=0, ge=0)
    requirements: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))


class LocationNeighbor(SQLModel, table=True):
    location_code: str = Field(foreign_key="location.code", primary_key=True)
    neighbor_location_code: str = Field(foreign_key="location.code", primary_key=True)
    location_handle: str | None = None
    neighbor_handle: str | None = None


class LocationWorkType(SQLModel, table=True):
    location_code: str = Field(foreign_key="location.code", primary_key=True)
    work_type_code: str = Field(foreign_key="worktypedefinition.code", primary_key=True)


class LocationBuildingDefinition(SQLModel, table=True):
    location_code: str = Field(foreign_key="location.code", primary_key=True)
    building_code: str = Field(foreign_key="buildingdefinition.code", primary_key=True)


class NationLocation(SQLModel, table=True):
    nation_id: int = Field(foreign_key="nation.id", primary_key=True)
    location_code: str = Field(foreign_key="location.code", primary_key=True)
    is_discovered: bool = False


class GameItem(SQLModel, table=True):
    code: str = Field(primary_key=True)
    name: str
    image_path: str | None = None
    visual_type: ItemVisualType = Field(default=ItemVisualType.ICON, sa_column=Column(Enum(ItemVisualType, values_callable=lambda enum: [member.value for member in enum]), nullable=False))
    description: str = ""
    worker_days: int = Field(default=0, ge=0)
    construction_resources: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    additional_data: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    max_workers: int = Field(default=0, ge=0)
    outputs: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))


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
    day: int
    message: str
    amount: float
    created_at: datetime = Field(default_factory=datetime.now)


class NationResource(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("nation_id", "resource_code"),)

    id: int | None = Field(default=None, primary_key=True)
    nation_id: int = Field(foreign_key="nation.id", index=True)
    resource_code: str = Field(foreign_key="resource.code", index=True)
    amount: float = 0


class NationBuilding(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nation_id: int = Field(foreign_key="nation.id", index=True)
    location_code: str = Field(foreign_key="location.code", index=True)
    building_code: str = Field(foreign_key="buildingdefinition.code", index=True)
    built_at: date = Field(default_factory=date.today)


class NationItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nation_id: int = Field(foreign_key="nation.id", index=True)
    nation_building_id: int | None = Field(default=None, foreign_key="nationbuilding.id", index=True)
    game_item_code: str = Field(foreign_key="gameitem.code", index=True)
    built_at: date = Field(default_factory=date.today)


class Process(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nation_id: int = Field(foreign_key="nation.id", index=True)
    location_code: str | None = Field(default=None, foreign_key="location.code", index=True)
    nation_building_id: int | None = Field(default=None, foreign_key="nationbuilding.id", index=True)
    nation_item_id: int | None = Field(default=None, foreign_key="nationitem.id", index=True)
    work_type: str = Field(foreign_key="worktypedefinition.code", index=True)
    description: str = ""
    mode: str
    status: str = "active"
    assigned_workers: int = 0
    required_worker_days: int | None = None
    completed_worker_days: int = 0
    started_at: date = Field(default_factory=date.today)
    completed_at: date | None = None
    outputs: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    details: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))


class PersonalTask(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nation_id: int = Field(foreign_key="nation.id", index=True)
    name: str
    description: str
    reward: int
    task_type: str
    status: str = PersonalTaskStatus.ACTIVE
    counter: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("task_type")
    @classmethod
    def validate_task_type(cls, value: str) -> str:
        return PersonalTaskType(value).value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        return PersonalTaskStatus(value).value
