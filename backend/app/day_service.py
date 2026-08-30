from datetime import date, timedelta

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.game_rules import BuildingType, WorkIntensity
from app.models import BuildingDefinition, BuildingWorkTypeCapability, DayReport, GameItem, Nation, NationBuilding, NationItem, NationLocation, NationLog, NationResource, Process, Resource, WorkTypeDefinition
from app.settings import (
    BASE_FOOD_SPENDING,
    HUNGER_STAGE_ONE_DAYS,
    POPULATION_GROWTH_PERCENT,
    POPULATION_GROWTH_REQUIRED_HEALTHY_DAYS,
    active_population,
)


async def nation_current_day(session: AsyncSession, nation: Nation) -> int:
    if settings.day_progress_mode != "reload":
        return (date.today() - nation.start_date).days + 1
    result = await session.exec(select(DayReport.id).where(DayReport.nation_id == nation.id))
    return len(result.all()) + 1


def daily_resource_flow(
    nation: Nation,
    processes: list[Process],
    resource_amounts: dict[str, float],
    work_types: dict[str, WorkTypeDefinition],
    output_multipliers: dict[int, float] | None = None,
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
                income[resource] = income.get(resource, 0) + workers * amount * (output_multipliers or {}).get(process.id or 0, 1)

    food_spending += (
        (nation.population - assigned_workers)
        * BASE_FOOD_SPENDING
        * WorkIntensity.BASE.coefficient
    )
    return {
        code: {"spending": food_spending if code == "food" else 0, "income": amount}
        for code, amount in income.items()
    }


def storable_income(income: float, storage_coefficient: float, free_capacity: float) -> float:
    if storage_coefficient <= 0:
        return income
    return min(income, max(0, free_capacity) / storage_coefficient)


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
        .join(Resource, NationResource.resource_code == Resource.code)
        .where(NationResource.nation_id == nation.id)
        .order_by(Resource.order, Resource.code)
    )
    resource_rows = result.all()
    result = await session.exec(
        select(BuildingDefinition.capacity)
        .join(NationBuilding, NationBuilding.building_code == BuildingDefinition.code)
        .where(
            NationBuilding.nation_id == nation.id,
            BuildingDefinition.building_type == BuildingType.WAREHOUSE,
        )
    )
    warehouse_capacity = sum(result.all())
    result = await session.exec(select(WorkTypeDefinition))
    work_types = {work_type.code: work_type for work_type in result.all()}
    result = await session.exec(select(NationBuilding).where(NationBuilding.nation_id == nation.id))
    building_codes = {building.id: building.building_code for building in result.all()}
    result = await session.exec(select(BuildingWorkTypeCapability))
    capabilities = {(capability.building_code, capability.work_type_code): capability for capability in result.all()}
    output_multipliers = {
        process.id: capabilities[(building_codes[process.nation_building_id], process.work_type)].output_multiplier or 1
        for process in processes
        if process.nation_building_id in building_codes
        and (building_codes[process.nation_building_id], process.work_type) in capabilities
    }
    resource_amounts = {resource.code: nation_resource.amount for nation_resource, resource in resource_rows}
    if sum(process.assigned_workers for process in processes) > active_population(
        nation.population
    ):
        raise ValueError("More workers assigned than the active population")

    resource_flow = daily_resource_flow(nation, processes, resource_amounts, work_types, output_multipliers)
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
                building_code = process.details.get("building_code")
                if building_code is not None:
                    definition = await session.get(BuildingDefinition, building_code)
                    if definition is not None:
                        session.add(NationBuilding(nation_id=nation.id, location_code=process.location_code, building_code=definition.code, built_at=report_date))
                        session.add(NationLog(nation_id=nation.id, day=game_day, message=f"Завершено будівництво: {definition.name}", amount=1))
                item_code = process.details.get("item_code")
                if item_code is not None:
                    item = await session.get(GameItem, item_code)
                    if item is not None:
                        session.add(NationItem(nation_id=nation.id, process_id=process.id, game_item_code=item.code, built_at=report_date))
                        session.add(NationLog(nation_id=nation.id, day=game_day, message=f"Завершено створення: {item.name}", amount=1))
                discovery_location_code = process.details.get("discovery_location_code")
                if discovery_location_code is not None:
                    nation_location = await session.get(NationLocation, (nation.id, discovery_location_code))
                    if nation_location is not None:
                        nation_location.is_discovered = True
                        session.add(nation_location)
                        session.add(NationLog(nation_id=nation.id, day=game_day, message=f"Відкрито локацію: {discovery_location_code}", amount=0))

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

    post_spending = {
        resource.code: max(0, nation_resource.amount - resource_flow[resource.code]["spending"])
        for nation_resource, resource in resource_rows
    }
    free_storage = warehouse_capacity - sum(
        post_spending[resource.code] * resource.storage_coefficient
        for _, resource in resource_rows
        if not resource.is_system
    )
    resources_snapshot = {}
    uncollected: list[tuple[str, float]] = []
    for nation_resource, resource in resource_rows:
        flow = resource_flow[resource.code]
        income = flow["income"]
        stored_income = income if resource.is_system else storable_income(
            income, resource.storage_coefficient, free_storage
        )
        if not resource.is_system:
            free_storage -= stored_income * resource.storage_coefficient
        if income > stored_income:
            uncollected.append((resource.name, income - stored_income))
        nation_resource.amount = post_spending[resource.code] + stored_income
        resources_snapshot[resource.code] = {
            "amount": nation_resource.amount,
            "spending": flow["spending"],
            "income": stored_income,
        }
        session.add(nation_resource)
    available_food = resource_amounts.get("food", 0) + resources_snapshot["food"]["income"]
    food_consumed = resource_flow["food"]["spending"]
    notes: list[str] = []
    food_shortage = max(0, food_consumed - available_food)
    is_hungry = food_shortage > 0
    if is_hungry:
        notes.append(f"Food shortage: {food_shortage:g}")
    if uncollected:
        details = ", ".join(f"{name} — {amount:g}" for name, amount in uncollected)
        session.add(NationLog(nation_id=nation.id, day=game_day, message=f"Недостатньо місця на складах: не зібрано {details}", amount=0))
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
    if settings.day_progress_mode == "reload":
        return [await advance_day(session, nation, next_report_date)] if reload_tick else []

    last_completed_date = today - timedelta(days=1)

    reports = []
    while next_report_date <= last_completed_date:
        reports.append(await advance_day(session, nation, next_report_date))
        next_report_date += timedelta(days=1)
    return reports
