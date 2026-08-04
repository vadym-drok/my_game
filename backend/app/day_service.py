from datetime import date, timedelta

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.game_rules import WorkIntensity
from app.models import BuildingDefinition, DayReport, Nation, NationBuilding, NationLog, NationResource, Process, Resource, WorkTypeDefinition
from app.settings import (
    BASE_FOOD_SPENDING,
    DAY_PROGRESS_MODE,
    HUNGER_STAGE_ONE_DAYS,
    POPULATION_GROWTH_PERCENT,
    POPULATION_GROWTH_REQUIRED_HEALTHY_DAYS,
    active_population,
)


async def nation_current_day(session: AsyncSession, nation: Nation) -> int:
    if DAY_PROGRESS_MODE != "reload":
        return (date.today() - nation.start_date).days + 1
    result = await session.exec(select(DayReport.id).where(DayReport.nation_id == nation.id))
    return len(result.all()) + 1


def daily_resource_flow(
    nation: Nation,
    processes: list[Process],
    resource_amounts: dict[str, float],
    work_types: dict[str, WorkTypeDefinition],
) -> dict[str, dict[str, float]]:
    income = {code: 0 for code in resource_amounts}
    food_spending = 0.0
    assigned_workers = 0
    for process in processes:
        work_type = work_types[process.work_type]
        workers = process.assigned_workers
        assigned_workers += workers
        food_spending += workers * BASE_FOOD_SPENDING * work_type.intensity.coefficient
        if process.mode == "continuous":
            for resource, amount in work_type.outputs.items():
                income[resource] = income.get(resource, 0) + workers * amount

    food_spending += (
        (nation.population - assigned_workers)
        * BASE_FOOD_SPENDING
        * WorkIntensity.BASE.coefficient
    )
    return {
        code: {"spending": food_spending if code == "food" else 0, "income": amount}
        for code, amount in income.items()
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
    game_day = await nation_current_day(session, nation)

    result = await session.exec(
        select(Process).where(
            Process.nation_id == nation.id, Process.status == "active"
        )
    )
    processes = result.all()
    result = await session.exec(
        select(NationResource, Resource)
        .join(Resource, NationResource.resource_id == Resource.id)
        .where(NationResource.nation_id == nation.id)
    )
    resource_rows = result.all()
    result = await session.exec(select(WorkTypeDefinition))
    work_types = {work_type.code: work_type for work_type in result.all()}
    resource_amounts = {resource.code: nation_resource.amount for nation_resource, resource in resource_rows}
    if sum(process.assigned_workers for process in processes) > active_population(
        nation.population
    ):
        raise ValueError("More workers assigned than the active population")

    resource_flow = daily_resource_flow(nation, processes, resource_amounts, work_types)
    workers_summary: dict[str, int] = {}
    processes_summary: list[dict] = []
    for process in processes:
        work_type = work_types[process.work_type]
        workers = process.assigned_workers
        workers_summary[work_type.code] = workers_summary.get(work_type.code, 0) + workers
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
                building_definition_id = process.details.get("building_definition_id")
                if building_definition_id is not None:
                    definition = await session.get(BuildingDefinition, building_definition_id)
                    if definition is not None:
                        session.add(NationBuilding(nation_id=nation.id, building_definition_id=definition.id, built_at=report_date))
                        session.add(NationLog(nation_id=nation.id, day=game_day, message=f"Завершено будівництво: {definition.name}", amount=1))

        processes_summary.append(
            {
                "process_id": process.id,
                "work_type": work_type.code,
                "mode": process.mode,
                "workers": workers,
                "progress_added": progress_added,
                "status": process.status,
            }
        )

    available_food = resource_amounts.get("food", 0) + resource_flow["food"]["income"]
    food_consumed = resource_flow["food"]["spending"]
    notes: list[str] = []
    food_shortage = max(0, food_consumed - available_food)
    is_hungry = food_shortage > 0
    if is_hungry:
        notes.append(f"Food shortage: {food_shortage:g}")
    resources_snapshot = {}
    for nation_resource, resource in resource_rows:
        flow = resource_flow[resource.code]
        nation_resource.amount = max(0, nation_resource.amount + flow["income"] - flow["spending"])
        resources_snapshot[resource.code] = {"amount": nation_resource.amount, **flow}
        session.add(nation_resource)
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
                    day=game_day,
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
        influence=nation.influence,
        food_shortage=food_shortage,
        is_hungry=is_hungry,
        resources=resources_snapshot,
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
