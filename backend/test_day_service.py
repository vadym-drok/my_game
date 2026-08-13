from datetime import date

from app.day_service import daily_resource_flow, storable_income
from app.game_rules import WorkIntensity, WorkMode
from app.main import get_work_rules
from app.models import Nation, Process, WorkTypeDefinition


class FakeResult:
    def __init__(self, rules: list[WorkTypeDefinition]) -> None:
        self.rules = rules

    def all(self) -> list[WorkTypeDefinition]:
        return self.rules


class FakeSession:
    def __init__(self, rules: list[WorkTypeDefinition]) -> None:
        self.rules = rules

    async def exec(self, _: object) -> FakeResult:
        return FakeResult(self.rules)


async def test_get_work_rules() -> None:
    rules = await get_work_rules(
        FakeSession([
            WorkTypeDefinition(
                code="woodcutting", name="Woodcutting", intensity=WorkIntensity.STANDARD,
                mode=WorkMode.CONTINUOUS, outputs={"wood": 1},
            )
        ])
    )
    assert rules[0]["code"] == "woodcutting"
    assert rules[0]["outputs"] == {"wood": 1}


def test_daily_resource_flow() -> None:
    nation = Nation(name="Test", population=10, start_date=date.today())
    process = Process(nation_id=1, work_type="woodcutting", mode="continuous", assigned_workers=5)
    work_types = {
        "woodcutting": WorkTypeDefinition(
            code="woodcutting", name="Woodcutting", intensity=WorkIntensity.STANDARD,
            mode=WorkMode.CONTINUOUS, outputs={"wood": 1},
        )
    }

    flow = daily_resource_flow(nation, [process], {"food": 20, "wood": 0}, work_types)

    assert flow["food"] == {"spending": 15, "income": 0}
    assert flow["wood"] == {"spending": 0, "income": 5}


def test_storable_income_respects_available_capacity() -> None:
    assert storable_income(5, 2, 6) == 3
