import asyncio
from datetime import date, timedelta

from app.day_service import advance_day, sync_nation
from app.game_rules import WorkType
from app.models import Nation, Process

class FakeSession:
    def __init__(self, processes: list[Process]) -> None:
        self.processes = processes

    def add(self, _: object) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def refresh(self, _: object) -> None:
        pass

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
    report = await advance_day(FakeSession([process]), nation)

    assert report.report_date == date.today()
    assert report.food_produced == 0
    assert report.food_consumed == 15
    assert nation.food == 5
    assert nation.wood == 5

    delayed_nation = Nation(
        name="Delayed", population=5, food=10, start_date=date.today() - timedelta(days=1)
    )
    delayed_nation.id = 2
    reports = await sync_nation(FakeSession([]), delayed_nation)
    assert len(reports) == 1
    assert reports[0].report_date == date.today() - timedelta(days=1)


asyncio.run(check())
