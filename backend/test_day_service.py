import asyncio
from datetime import date, timedelta

import app.day_service as day_service
from app.day_service import daily_resource_flow
from app.game_rules import WorkType
from app.main import get_work_rules
from app.models import Nation, Process, Resource
from app.population_growth import population_growth_available, population_growth_limit
from app.settings import active_population

class FakeSession:
    def __init__(self, processes: list[Process], nation: Nation | None = None) -> None:
        self.processes = processes
        self.nation = nation
        self.added: list[object] = []

    def add(self, item: object) -> None:
        self.added.append(item)

    async def commit(self) -> None:
        pass

    async def refresh(self, _: object) -> None:
        pass

    async def get(self, _: object, __: int) -> Nation | None:
        return self.nation

    async def exec(self, _: object) -> "FakeResult":
        return FakeResult(self.processes)


class FakeResult:
    def __init__(self, processes: list[Process]) -> None:
        self.processes = processes

    def first(self) -> None:
        return None

    def all(self) -> list:
        return self.processes


async def check() -> None:
    resource = Resource(code="food", name="Їжа")
    assert resource.storage_coefficient == 1
    rules = await get_work_rules()
    assert next(rule for rule in rules if rule["work_type"] == "woodcutting") == {
        "work_type": "woodcutting", "food_multiplier": 2, "outputs": {"wood": 1}
    }
    assert active_population(50) == 40
    growth_nation = Nation(name="Growth", start_date=date(2026, 8, 2), population=50)
    assert not population_growth_available(growth_nation)
    growth_nation.population_growth_progress = 5
    assert population_growth_available(growth_nation)
    assert population_growth_limit(growth_nation.population) == 5
    nation = Nation(name="Test", population=10, start_date=date.today())
    nation.id = 1
    process = Process(
        id=1,
        nation_id=1,
        name="Woodcutting",
        work_type=WorkType.WOODCUTTING,
        mode="continuous",
        assigned_workers=5,
    )
    flow = daily_resource_flow(
        nation, [process], {"general_points": 0, "food": 20, "wood": 0, "stone": 0}
    )
    assert flow["general_points"] == {"spending": 0, "income": 0}
    assert flow["food"] == {"spending": 15, "income": 0}
    assert flow["wood"] == {"spending": 0, "income": 5}


asyncio.run(check())
