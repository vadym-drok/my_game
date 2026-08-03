import asyncio
from datetime import date, timedelta

import app.day_service as day_service
from app.day_service import advance_day, daily_resource_flow, sync_nation
from app.game_rules import WorkType
from app.main import adjust_resource
from app.models import Nation, NationLog, Process
from app.population_growth import population_growth_available, population_growth_limit
from app.schemas import ResourceAdjustment
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
    assert active_population(50) == 40
    growth_nation = Nation(name="Growth", start_date=date(2026, 8, 2), population=50)
    assert not population_growth_available(growth_nation)
    growth_nation.population_growth_progress = 5
    assert population_growth_available(growth_nation)
    assert population_growth_limit(growth_nation.population) == 5
    nation = Nation(name="Test", population=10, food=20, start_date=date.today())
    nation.id = 1
    process = Process(
        id=1,
        nation_id=1,
        name="Woodcutting",
        work_type=WorkType.WOODCUTTING,
        mode="continuous",
        assigned_workers=5,
    )
    flow = daily_resource_flow(nation, [process])
    assert flow["food"] == {"spending": 15, "income": 0}
    assert flow["wood"] == {"spending": 0, "income": 5}
    report = await advance_day(FakeSession([process]), nation)

    assert report.report_date == date.today()
    assert report.food_produced == 0
    assert report.food_consumed == 15
    assert nation.food == 5
    assert nation.wood == 5
    assert nation.population_growth_progress == 1

    hungry_nation = Nation(name="Hungry", population=10, start_date=date.today())
    hungry_nation.id = 3
    hungry_report = await advance_day(FakeSession([]), hungry_nation)
    assert hungry_nation.food == 0
    assert hungry_nation.consecutive_hunger_days == 1
    assert hungry_nation.population_growth_progress == 0
    assert hungry_report.is_hungry
    assert hungry_report.food_shortage == 10
    await advance_day(FakeSession([]), hungry_nation, date.today() + timedelta(days=1))
    await advance_day(FakeSession([]), hungry_nation, date.today() + timedelta(days=2))
    hunger_penalty_session = FakeSession([])
    hunger_penalty_report = await advance_day(
        hunger_penalty_session, hungry_nation, date.today() + timedelta(days=3)
    )
    assert hungry_nation.population == 9
    assert hungry_nation.consecutive_hunger_days == 1
    assert hunger_penalty_report.notes == ["Food shortage: 10", "Population loss: 1"]
    assert any(isinstance(item, NationLog) and item.amount == -1 for item in hunger_penalty_session.added)

    resource_nation = Nation(name="Resources", food=5)
    resource_nation.id = 5
    resource_session = FakeSession([], resource_nation)
    await adjust_resource(5, "food", ResourceAdjustment(amount=-9), resource_session)
    await adjust_resource(5, "stone", ResourceAdjustment(amount=7), resource_session)
    assert resource_nation.food == 0
    assert resource_nation.stone == 7
    assert any(isinstance(item, NationLog) and item.amount == 7 for item in resource_session.added)

    original_mode = day_service.DAY_PROGRESS_MODE
    day_service.DAY_PROGRESS_MODE = "calendar"
    delayed_nation = Nation(
        name="Delayed", population=5, food=10, start_date=date.today() - timedelta(days=1)
    )
    delayed_nation.id = 2
    reports = await sync_nation(FakeSession([]), delayed_nation)
    assert len(reports) == 1
    assert reports[0].report_date == date.today() - timedelta(days=1)

    day_service.DAY_PROGRESS_MODE = "reload"
    reload_nation = Nation(name="Reload", population=5, food=10, start_date=date.today())
    reload_nation.id = 4
    assert not await sync_nation(FakeSession([]), reload_nation)
    reports = await sync_nation(FakeSession([]), reload_nation, reload_tick=True)
    assert len(reports) == 1
    day_service.DAY_PROGRESS_MODE = original_mode


asyncio.run(check())
