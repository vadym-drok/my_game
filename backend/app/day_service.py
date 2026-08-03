from datetime import date, timedelta

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.game_rules import (
    WORK_INTENSITY,
    WORK_OUTPUTS,
    WorkType,
)
from app.models import DayReport, Nation, NationLog, Process
from app.settings import (
    BASE_FOOD_SPENDING,
    DAY_PROGRESS_MODE,
    HUNGER_STAGE_ONE_DAYS,
    POPULATION_GROWTH_PERCENT,
    POPULATION_GROWTH_REQUIRED_HEALTHY_DAYS,
    active_population,
)


def daily_resource_flow(nation: Nation, processes: list[Process]) -> dict[str, dict[str, float]]:
    income = {"general_points": 0, "food": 0, "wood": 0, "stone": 0}
    food_spending = 0.0
    assigned_workers = 0
    for process in processes:
        work_type = WorkType(process.work_type)
        workers = process.assigned_workers
        assigned_workers += workers
        food_spending += workers * BASE_FOOD_SPENDING * WORK_INTENSITY[work_type].value
        if process.mode == "continuous":
            for resource, amount in WORK_OUTPUTS.get(work_type, {}).items():
                income[resource] += workers * amount

    food_spending += (
        (nation.population - assigned_workers)
        * BASE_FOOD_SPENDING
        * WORK_INTENSITY[WorkType.FOOD_GATHERING].value
    )
    return {
        resource: {"spending": food_spending if resource == "food" else 0, "income": amount}
        for resource, amount in income.items()
    }


async def advance_day(
    session: AsyncSession, nation: Nation, report_date: date | None = None
) -> DayReport:
    report_date = report_date or date.today()
    existing = await session.exec(
        select(DayReport).where(
            DayReport.nation_id == nation.id,
            DayReport.report_date == report_date,
        )
    )
    if existing.first() is not None:
        raise ValueError(f"A report for {report_date.isoformat()} already exists")

    result = await session.exec(
        select(Process).where(
            Process.nation_id == nation.id, Process.status == "active"
        )
    )
    processes = result.all()
    if sum(process.assigned_workers for process in processes) > active_population(
        nation.population
    ):
        raise ValueError("More workers assigned than the active population")

    resource_flow = daily_resource_flow(nation, processes)
    workers_summary: dict[str, int] = {}
    processes_summary: list[dict] = []
    for process in processes:
        work_type = WorkType(process.work_type)
        workers = process.assigned_workers
        workers_summary[work_type] = workers_summary.get(work_type, 0) + workers
        progress_added = 0

        if process.mode == "finite":
            assert process.required_worker_days is not None
            progress_added = min(
                workers, process.required_worker_days - process.completed_worker_days
            )
            process.completed_worker_days += progress_added
            if process.completed_worker_days == process.required_worker_days:
                process.status = "completed"
                process.completed_at = report_date

        processes_summary.append(
            {
                "process_id": process.id,
                "work_type": work_type,
                "mode": process.mode,
                "workers": workers,
                "progress_added": progress_added,
                "status": process.status,
            }
        )

    available_food = nation.food + resource_flow["food"]["income"]
    food_consumed = resource_flow["food"]["spending"]
    notes: list[str] = []
    food_shortage = max(0, food_consumed - available_food)
    is_hungry = food_shortage > 0
    if is_hungry:
        notes.append(f"Food shortage: {food_shortage:g}")
    nation.food = max(0, available_food - food_consumed)
    nation.wood = max(0, nation.wood + resource_flow["wood"]["income"])
    nation.stone = max(0, nation.stone + resource_flow["stone"]["income"])
    if is_hungry:
        nation.consecutive_hunger_days += 1
        nation.population_growth_progress = 0
        if nation.consecutive_hunger_days > HUNGER_STAGE_ONE_DAYS:
            population_loss = nation.population * POPULATION_GROWTH_PERCENT // 100
            nation.population -= population_loss
            nation.consecutive_hunger_days = 1
            notes.append(f"Population loss: {population_loss}")
            session.add(
                NationLog(
                    nation_id=nation.id,
                    message="Голод: населення",
                    amount=-population_loss,
                )
            )
    else:
        nation.consecutive_hunger_days = 0
        nation.population_growth_progress = min(
            nation.population_growth_progress + 1,
            POPULATION_GROWTH_REQUIRED_HEALTHY_DAYS,
        )

    report = DayReport(
        nation_id=nation.id,
        report_date=report_date,
        population=nation.population,
        food=nation.food,
        general_points=nation.general_points,
        wood=nation.wood,
        stone=nation.stone,
        influence=nation.influence,
        food_produced=resource_flow["food"]["income"],
        food_consumed=food_consumed,
        food_shortage=food_shortage,
        is_hungry=is_hungry,
        workers_summary=workers_summary,
        processes_summary=processes_summary,
        notes=notes,
    )
    session.add(nation)
    session.add(report)
    await session.commit()
    await session.refresh(report)
    return report


async def sync_nation(
    session: AsyncSession,
    nation: Nation,
    today: date | None = None,
    reload_tick: bool = False,
) -> list[DayReport]:
    today = today or date.today()
    result = await session.exec(
        select(DayReport)
        .where(DayReport.nation_id == nation.id)
        .order_by(DayReport.report_date.desc())
        .limit(1)
    )
    last_report = result.first()
    next_report_date = (
        last_report.report_date + timedelta(days=1)
        if last_report is not None
        else nation.start_date
    )
    if DAY_PROGRESS_MODE == "reload":
        return [await advance_day(session, nation, next_report_date)] if reload_tick else []

    last_completed_date = today - timedelta(days=1)

    reports = []
    while next_report_date <= last_completed_date:
        reports.append(await advance_day(session, nation, next_report_date))
        next_report_date += timedelta(days=1)
    return reports
