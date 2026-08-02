import asyncio

from app.day_service import advance_day
from app.game_rules import WorkType
from app.models import Settlement

class FakeSession:
    def add(self, _: object) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def refresh(self, _: object) -> None:
        pass


async def check() -> None:
    settlement = Settlement(name="Test", population=10, food=20)
    settlement.id = 1
    report = await advance_day(
        FakeSession(), settlement, {WorkType.FOOD_GATHERING: 5}
    )

    assert report.day_number == 1
    assert report.food_produced == 10
    assert report.food_consumed == 10
    assert settlement.food == 20


asyncio.run(check())
