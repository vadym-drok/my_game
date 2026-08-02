from datetime import date

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.game_rules import WORK_INTENSITY, WORK_OUTPUTS, WorkType
from app.models import DayReport, Nation, Process


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
        raise ValueError("A report for today already exists")

    result = await session.exec(
        select(Process).where(
            Process.nation_id == nation.id, Process.status == "active"
        )
    )
    processes = result.all()
    if sum(process.assigned_workers for process in processes) > nation.population:
        raise ValueError("More workers assigned than the nation population")

    workers_summary: dict[str, int] = {}
    processes_summary: list[dict] = []
    produced = {"food": 0, "wood": 0, "stone": 0}
    food_consumed = 0.0
    for process in processes:
        work_type = WorkType(process.work_type)
        workers = process.assigned_workers
        workers_summary[work_type] = workers_summary.get(work_type, 0) + workers
        food_consumed += workers * WORK_INTENSITY[work_type].value
        progress_added = 0

        if process.mode == "continuous":
            for resource, amount in WORK_OUTPUTS.get(work_type, {}).items():
                produced[resource] += workers * amount
        else:
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

    idle_workers = nation.population - sum(workers_summary.values())
    food_consumed += idle_workers * WORK_INTENSITY[WorkType.FOOD_GATHERING].value

    available_food = nation.food + produced["food"]
    notes: list[str] = []
    if available_food < food_consumed:
        notes.append(f"Food shortage: {food_consumed - available_food:g}")
    nation.food = max(0, available_food - food_consumed)
    nation.wood += produced["wood"]
    nation.stone += produced["stone"]

    report = DayReport(
        nation_id=nation.id,
        report_date=report_date,
        population=nation.population,
        food=nation.food,
        wood=nation.wood,
        stone=nation.stone,
        influence=nation.influence,
        food_produced=produced["food"],
        food_consumed=food_consumed,
        workers_summary=workers_summary,
        processes_summary=processes_summary,
        notes=notes,
    )
    session.add(nation)
    session.add(report)
    await session.commit()
    await session.refresh(report)
    return report
