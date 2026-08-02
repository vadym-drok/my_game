from sqlmodel.ext.asyncio.session import AsyncSession

from app.game_rules import FOOD_MULTIPLIERS, WORKS, WorkType
from app.models import DayReport, Settlement


async def advance_day(
    session: AsyncSession, settlement: Settlement, assignments: dict[WorkType, int]
) -> DayReport:
    if any(workers < 0 for workers in assignments.values()):
        raise ValueError("Worker count cannot be negative")
    if sum(assignments.values()) > settlement.population:
        raise ValueError("More workers assigned than the settlement population")

    food_produced = sum(
        workers * WORKS[work_type].food_per_worker
        for work_type, workers in assignments.items()
    )
    wood_produced = sum(
        workers * WORKS[work_type].wood_per_worker
        for work_type, workers in assignments.items()
    )
    food_consumed = sum(
        workers * FOOD_MULTIPLIERS[WORKS[work_type].intensity]
        for work_type, workers in assignments.items()
    )
    idle_workers = settlement.population - sum(assignments.values())
    food_consumed += idle_workers * FOOD_MULTIPLIERS[WORKS[WorkType.FOOD_GATHERING].intensity]

    available_food = settlement.food + food_produced
    notes: list[str] = []
    if available_food < food_consumed:
        notes.append(f"Food shortage: {food_consumed - available_food:g}")
    settlement.food = max(0, available_food - food_consumed)
    settlement.wood += wood_produced
    settlement.current_day += 1

    report = DayReport(
        settlement_id=settlement.id,
        day_number=settlement.current_day,
        population=settlement.population,
        food=settlement.food,
        wood=settlement.wood,
        stone=settlement.stone,
        influence=settlement.influence,
        food_produced=food_produced,
        food_consumed=food_consumed,
        workers_summary={work_type.value: workers for work_type, workers in assignments.items()},
        notes=notes,
    )
    session.add(settlement)
    session.add(report)
    await session.commit()
    await session.refresh(report)
    return report
