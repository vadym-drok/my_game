from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.day_service import daily_resource_flow, sync_nation
from app.db import get_session
from app.game_rules import BuildingType, WorkMode
from app.models import BuildingDefinition, DayReport, IconFrame, Nation, NationBuilding, NationLog, NationResource, Process, Resource, WorkTypeDefinition
from app.population_growth import population_growth_available, population_growth_limit
from app.schemas import (
    NationCreate,
    PopulationGrowth,
    ResourceAdjustment,
    ProcessCreate,
    ProcessUpdate,
)
from app.settings import (
    HUNGER_STAGE_ONE_DAYS,
    DAY_PROGRESS_MODE,
    POPULATION_GROWTH_REQUIRED_HEALTHY_DAYS,
    active_population,
)

app = FastAPI(title="My Game API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3010"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def icon_frame_paths(session: AsyncSession) -> dict[int, str | None]:
    result = await session.exec(select(IconFrame))
    return {frame.id: frame.image_path for frame in result.all() if frame.id is not None}


def with_icon_frame(item: Resource | WorkTypeDefinition | BuildingDefinition, paths: dict[int, str | None]) -> dict:
    return item.model_dump() | {"icon_frame_image_path": paths.get(item.icon_frame_id)}


@app.get("/resources")
async def list_resources(session: AsyncSession = Depends(get_session)) -> list[dict]:
    result = await session.exec(select(Resource).order_by(Resource.id))
    paths = await icon_frame_paths(session)
    return [with_icon_frame(item, paths) for item in result.all()]


@app.get("/work-rules")
async def get_work_rules(session: AsyncSession = Depends(get_session)) -> list[dict]:
    result = await session.exec(select(WorkTypeDefinition).order_by(WorkTypeDefinition.id))
    paths = await icon_frame_paths(session)
    return [with_icon_frame(item, paths) for item in result.all()]


@app.get("/buildings")
async def list_building_definitions(session: AsyncSession = Depends(get_session)) -> list[dict]:
    result = await session.exec(select(BuildingDefinition).order_by(BuildingDefinition.id))
    paths = await icon_frame_paths(session)
    return [with_icon_frame(item, paths) for item in result.all()]


@app.get("/nations/{nation_id}/buildings")
async def list_nation_buildings(nation_id: int, session: AsyncSession = Depends(get_session)) -> list[dict]:
    result = await session.exec(
        select(NationBuilding, BuildingDefinition)
        .join(BuildingDefinition, NationBuilding.building_definition_id == BuildingDefinition.id)
        .where(NationBuilding.nation_id == nation_id)
        .order_by(NationBuilding.id.desc())
    )
    paths = await icon_frame_paths(session)
    return [{**with_icon_frame(definition, paths), "id": building.id, "built_at": building.built_at} for building, definition in result.all()]


@app.post("/nations/{nation_id}/buildings/{code}", response_model=NationBuilding)
async def build(nation_id: int, code: str, action: str = "build", session: AsyncSession = Depends(get_session)) -> NationBuilding:
    if await session.get(Nation, nation_id) is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    result = await session.exec(select(BuildingDefinition).where(BuildingDefinition.code == code))
    definition = result.first()
    if definition is None:
        raise HTTPException(status_code=404, detail="Building not found")
    if action not in {"build", "add"}:
        raise HTTPException(status_code=422, detail="Unknown building action")
    building = NationBuilding(nation_id=nation_id, building_definition_id=definition.id)
    session.add(building)
    if action == "add":
        session.add(NationLog(nation_id=nation_id, message=f"Додано будівлю: {definition.name}", amount=1))
    await session.commit()
    await session.refresh(building)
    return building


@app.delete("/nations/{nation_id}/buildings/{building_id}", status_code=204)
async def remove_building(nation_id: int, building_id: int, session: AsyncSession = Depends(get_session)) -> None:
    building = await session.get(NationBuilding, building_id)
    if building is None or building.nation_id != nation_id:
        raise HTTPException(status_code=404, detail="Built building not found")
    definition = await session.get(BuildingDefinition, building.building_definition_id)
    await session.delete(building)
    session.add(NationLog(nation_id=nation_id, message=f"Прибрано будівлю: {definition.name if definition else building_id}", amount=-1))
    await session.commit()


@app.post("/nations", response_model=Nation)
async def create_nation(
    data: NationCreate, session: AsyncSession = Depends(get_session)
) -> Nation:
    nation = Nation(name=data.name, population=data.population)
    session.add(nation)
    await session.commit()
    await session.refresh(nation)
    result = await session.exec(select(Resource))
    for resource in result.all():
        session.add(
            NationResource(
                nation_id=nation.id,
                resource_id=resource.id,
                amount=data.resources.get(resource.code, 0),
            )
        )
    await session.commit()
    return nation


@app.get("/nations/{nation_id}")
async def get_nation(
    nation_id: int, session: AsyncSession = Depends(get_session)
) -> dict:
    nation = await session.get(Nation, nation_id)
    if nation is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    active = active_population(nation.population)
    current_day = (date.today() - nation.start_date).days + 1
    if DAY_PROGRESS_MODE == "reload":
        reports = await session.exec(select(DayReport.id).where(DayReport.nation_id == nation_id))
        current_day = len(reports.all()) + 1
    result = await session.exec(
        select(Process).where(
            Process.nation_id == nation_id, Process.status == "active"
        )
    )
    process_rows = list(result.all())
    result = await session.exec(
        select(NationResource, Resource)
        .join(Resource, NationResource.resource_id == Resource.id)
        .where(NationResource.nation_id == nation_id)
        .order_by(Resource.id)
    )
    resource_rows = result.all()
    frames = await icon_frame_paths(session)
    result = await session.exec(select(WorkTypeDefinition))
    work_types = {work_type.code: work_type for work_type in result.all()}
    result = await session.exec(
        select(BuildingDefinition.capacity)
        .join(NationBuilding, NationBuilding.building_definition_id == BuildingDefinition.id)
        .where(
            NationBuilding.nation_id == nation_id,
            BuildingDefinition.building_type == BuildingType.HOUSING,
        )
    )
    housing_capacity = sum(result.all())
    result = await session.exec(
        select(BuildingDefinition.capacity)
        .join(NationBuilding, NationBuilding.building_definition_id == BuildingDefinition.id)
        .where(
            NationBuilding.nation_id == nation_id,
            BuildingDefinition.building_type == BuildingType.WAREHOUSE,
        )
    )
    warehouse_capacity = sum(result.all())
    storage_used = sum(
        nation_resource.amount * resource.storage_coefficient
        for nation_resource, resource in resource_rows
        if resource.code != "general_points"
    )
    resource_amounts = {resource.code: nation_resource.amount for nation_resource, resource in resource_rows}
    flow = daily_resource_flow(nation, process_rows, resource_amounts, work_types)
    return nation.model_dump() | {
        "current_day": current_day,
        "active_population": active,
        "passive_population": nation.population - active,
        "housing_capacity": housing_capacity,
        "storage": {"used": storage_used, "capacity": warehouse_capacity},
        "resources": [
            {
                "code": resource.code,
                "name": resource.name,
                "image_path": resource.image_path,
                "icon_frame_image_path": frames.get(resource.icon_frame_id),
                "amount": nation_resource.amount,
                **flow[resource.code],
            }
            for nation_resource, resource in resource_rows
        ],
        "population_growth": {
            "available": population_growth_available(nation),
            "max_increase": population_growth_limit(nation.population),
            "progress_days": nation.population_growth_progress,
            "required_days": POPULATION_GROWTH_REQUIRED_HEALTHY_DAYS,
        },
        "hunger": {
            "active": nation.consecutive_hunger_days > 0,
            "days": nation.consecutive_hunger_days,
            "stage_days": HUNGER_STAGE_ONE_DAYS,
        },
    }


@app.post("/nations/{nation_id}/sync", response_model=list[DayReport])
async def sync_nation_days(
    nation_id: int,
    reload_tick: bool = False,
    session: AsyncSession = Depends(get_session),
) -> list[DayReport]:
    nation = await session.get(Nation, nation_id)
    if nation is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    try:
        return await sync_nation(session, nation, reload_tick=reload_tick)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/nations/{nation_id}/population-growth", response_model=Nation)
async def apply_population_growth(
    nation_id: int,
    data: PopulationGrowth,
    session: AsyncSession = Depends(get_session),
) -> Nation:
    nation = await session.get(Nation, nation_id)
    if nation is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    if not population_growth_available(nation):
        raise HTTPException(status_code=422, detail="Population growth is not available")
    if data.amount > population_growth_limit(nation.population):
        raise HTTPException(status_code=422, detail="Population growth limit exceeded")
    nation.population += data.amount
    nation.last_population_growth_date = date.today()
    nation.population_growth_progress = 0
    session.add(nation)
    await session.commit()
    await session.refresh(nation)
    return nation


@app.post("/nations/{nation_id}/resources/{resource}", response_model=Nation)
async def adjust_resource(
    nation_id: int,
    resource: str,
    data: ResourceAdjustment,
    session: AsyncSession = Depends(get_session),
) -> Nation:
    nation = await session.get(Nation, nation_id)
    if nation is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    result = await session.exec(select(Resource).where(Resource.code == resource))
    resource_definition = result.first()
    if resource_definition is None:
        raise HTTPException(status_code=422, detail="Unknown resource")
    result = await session.exec(
        select(NationResource).where(
            NationResource.nation_id == nation_id,
            NationResource.resource_id == resource_definition.id,
        )
    )
    nation_resource = result.first()
    if nation_resource is None:
        raise HTTPException(status_code=422, detail="Nation resource not found")
    previous_amount = nation_resource.amount
    current_amount = max(0, previous_amount + data.amount)
    nation_resource.amount = current_amount
    if current_amount != previous_amount:
        session.add(
            NationLog(
                nation_id=nation_id,
                message=f"Ручна зміна: {resource_definition.name}",
                amount=current_amount - previous_amount,
            )
        )
    session.add(nation_resource)
    await session.commit()
    await session.refresh(nation)
    return nation


@app.get("/nations/{nation_id}/logs", response_model=list[NationLog])
async def list_nation_logs(
    nation_id: int, session: AsyncSession = Depends(get_session)
) -> list[NationLog]:
    result = await session.exec(
        select(NationLog)
        .where(NationLog.nation_id == nation_id)
        .order_by(NationLog.id.desc())
    )
    return list(result.all())


@app.post("/nations/{nation_id}/processes", response_model=Process)
async def create_process(
    nation_id: int,
    data: ProcessCreate,
    session: AsyncSession = Depends(get_session),
) -> Process:
    nation = await session.get(Nation, nation_id)
    if nation is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    result = await session.exec(select(WorkTypeDefinition).where(WorkTypeDefinition.code == data.work_type))
    work_type = result.first()
    if work_type is None:
        raise HTTPException(status_code=422, detail="Unknown work type")
    if work_type.mode == WorkMode.FINITE and data.required_worker_days is None:
        raise HTTPException(
            status_code=422, detail="Finite processes require worker days"
        )
    if work_type.mode == WorkMode.CONTINUOUS and data.required_worker_days is not None:
        raise HTTPException(
            status_code=422, detail="Continuous processes cannot have worker days"
        )
    result = await session.exec(
        select(Process).where(
            Process.nation_id == nation_id, Process.status == "active"
        )
    )
    if (
        sum(process.assigned_workers for process in result.all())
        + data.assigned_workers
        > active_population(nation.population)
    ):
        raise HTTPException(status_code=422, detail="Active population limit exceeded")
    process = Process(nation_id=nation_id, **data.model_dump() | {"mode": work_type.mode})
    session.add(process)
    await session.commit()
    await session.refresh(process)
    return process


@app.get("/nations/{nation_id}/processes", response_model=list[Process])
async def list_processes(
    nation_id: int, session: AsyncSession = Depends(get_session)
) -> list[Process]:
    result = await session.exec(
        select(Process)
        .where(Process.nation_id == nation_id)
        .order_by(Process.id.desc())
    )
    return list(result.all())


@app.patch("/processes/{process_id}", response_model=Process)
async def update_process(
    process_id: int,
    data: ProcessUpdate,
    session: AsyncSession = Depends(get_session),
) -> Process:
    process = await session.get(Process, process_id)
    if process is None:
        raise HTTPException(status_code=404, detail="Process not found")
    nation = await session.get(Nation, process.nation_id)
    result = await session.exec(
        select(Process).where(
            Process.nation_id == process.nation_id, Process.status == "active"
        )
    )
    assigned_workers = data.assigned_workers if data.assigned_workers is not None else process.assigned_workers
    status = data.status if data.status is not None else process.status
    other_workers = sum(
        item.assigned_workers for item in result.all() if item.id != process.id
    )
    if status == "active" and other_workers + assigned_workers > active_population(
        nation.population
    ):
        raise HTTPException(status_code=422, detail="Active population limit exceeded")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(process, field, value)
    session.add(process)
    await session.commit()
    await session.refresh(process)
    return process
