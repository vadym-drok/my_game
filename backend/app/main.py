from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.day_service import daily_resource_flow, nation_current_day, sync_nation
from app.db import get_session
from app.game_rules import BuildingType, PersonalTaskStatus, WorkMode
from app.models import BuildingDefinition, BuildingItemCapability, BuildingWorkTypeCapability, DayReport, GameItem, Location, LocationBuildingDefinition, LocationNeighbor, LocationWorkType, Nation, NationBuilding, NationItem, NationLocation, NationLog, NationResource, PersonalTask, Process, ProcessNationItem, Resource, WorkTypeDefinition, WorkTypeItemRequirement
from app.population_growth import population_growth_available, population_growth_limit
from app.schemas import (
    NationCreate,
    ConstructionStart,
    BuildingAdd,
    ItemAdd,
    DiscoveryStart,
    PopulationGrowth,
    ResourceAdjustment,
    ResourcePurchase,
    ProcessCreate,
    ProcessUpdate,
    PersonalTaskAction,
    PersonalTaskCreate,
    LocationMapLayoutUpdate,
)
from app.settings import (
    HUNGER_STAGE_ONE_DAYS,
    GENERAL_POINT_RESOURCE_COST,
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


async def building_capacity(session: AsyncSession, nation_id: int, building_type: BuildingType) -> int:
    result = await session.exec(
        select(BuildingDefinition.capacity)
        .join(NationBuilding, NationBuilding.building_code == BuildingDefinition.code)
        .where(NationBuilding.nation_id == nation_id, BuildingDefinition.building_type == building_type)
    )
    return sum(result.all())


async def validate_building_location(session: AsyncSession, nation_id: int, location_code: str, building_code: str) -> None:
    nation_location = await session.get(NationLocation, (nation_id, location_code))
    if nation_location is None or not nation_location.is_discovered:
        raise HTTPException(status_code=422, detail="Location is not discovered")
    result = await session.exec(select(LocationBuildingDefinition).where(LocationBuildingDefinition.location_code == location_code, LocationBuildingDefinition.building_code == building_code))
    if result.first() is None:
        raise HTTPException(status_code=422, detail="Building is not available at this location")


@app.get("/resources")
async def list_resources(session: AsyncSession = Depends(get_session)) -> list[dict]:
    result = await session.exec(select(Resource).order_by(Resource.order, Resource.code))
    return [item.model_dump() for item in result.all()]


@app.get("/work-rules")
async def get_work_rules(session: AsyncSession = Depends(get_session)) -> list[dict]:
    result = await session.exec(select(WorkTypeDefinition).order_by(WorkTypeDefinition.code))
    work_types = result.all()
    result = await session.exec(select(WorkTypeItemRequirement))
    requirements: dict[str, list[dict]] = {}
    for requirement in result.all():
        requirements.setdefault(requirement.work_type_code, []).append(requirement.model_dump())
    return [{**item.model_dump(), "item_requirements": requirements.get(item.code, [])} for item in work_types]


@app.get("/buildings")
async def list_building_definitions(session: AsyncSession = Depends(get_session)) -> list[dict]:
    result = await session.exec(select(BuildingDefinition).order_by(BuildingDefinition.code))
    buildings = result.all()
    result = await session.exec(select(BuildingWorkTypeCapability))
    work_capabilities: dict[str, list[dict]] = {}
    for capability in result.all():
        work_capabilities.setdefault(capability.building_code, []).append(capability.model_dump())
    result = await session.exec(select(BuildingItemCapability))
    item_capabilities: dict[str, list[dict]] = {}
    for capability in result.all():
        item_capabilities.setdefault(capability.building_code, []).append(capability.model_dump())
    return [{**item.model_dump(), "work_type_capabilities": work_capabilities.get(item.code, []), "item_capabilities": item_capabilities.get(item.code, [])} for item in buildings]


@app.get("/nations/{nation_id}/locations")
async def list_locations(nation_id: int, session: AsyncSession = Depends(get_session)) -> list[dict]:
    if await session.get(Nation, nation_id) is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    result = await session.exec(select(Location, NationLocation).join(NationLocation, NationLocation.location_code == Location.code).where(NationLocation.nation_id == nation_id).order_by(Location.code))
    locations = result.all()
    result = await session.exec(select(LocationWorkType))
    work_types = {}
    for link in result.all():
        work_types.setdefault(link.location_code, []).append(link.work_type_code)
    result = await session.exec(select(LocationBuildingDefinition))
    buildings = {}
    for link in result.all():
        buildings.setdefault(link.location_code, []).append(link.building_code)
    return [{**location.model_dump(), "is_discovered": nation_location.is_discovered, "work_types": work_types.get(location.code, []), "buildings": buildings.get(location.code, [])} for location, nation_location in locations]


@app.get("/locations/map")
async def get_location_map(session: AsyncSession = Depends(get_session)) -> dict:
    locations = (await session.exec(select(Location).order_by(Location.code))).all()
    neighbors = (await session.exec(select(LocationNeighbor))).all()
    connections = {(edge.location_code, edge.neighbor_location_code, edge.location_handle, edge.neighbor_handle) for edge in neighbors}
    return {
        "nodes": [{"location_code": location.code, "x": location.map_x, "y": location.map_y} for location in locations],
        "connections": [{"source": source, "target": target, "source_handle": source_handle, "target_handle": target_handle} for source, target, source_handle, target_handle in sorted(connections)],
    }


@app.put("/locations/map")
async def save_location_map(layout: LocationMapLayoutUpdate, session: AsyncSession = Depends(get_session)) -> dict:
    codes = set((await session.exec(select(Location.code))).all())
    node_codes = [node.location_code for node in layout.nodes]
    if len(node_codes) != len(set(node_codes)) or not set(node_codes).issubset(codes):
        raise HTTPException(status_code=422, detail="Unknown or duplicate location node")
    connections = {}
    for edge in layout.connections:
        source, target, source_handle, target_handle = edge.source, edge.target, edge.source_handle, edge.target_handle
        if source > target:
            source, target, source_handle, target_handle = target, source, target_handle, source_handle
        connections[(source, target)] = (source_handle, target_handle)
    if any(source == target or source not in node_codes or target not in node_codes for source, target in connections):
        raise HTTPException(status_code=422, detail="Invalid location connection")
    await session.exec(delete(LocationNeighbor))
    for node in layout.nodes:
        location = await session.get(Location, node.location_code)
        location.map_x, location.map_y = node.x, node.y
        session.add(location)
    session.add_all([LocationNeighbor(location_code=source, neighbor_location_code=target, location_handle=handles[0], neighbor_handle=handles[1]) for (source, target), handles in connections.items()])
    await session.commit()
    return {"nodes": len(layout.nodes), "connections": len(connections)}


@app.get("/items", response_model=list[GameItem])
async def list_game_items(session: AsyncSession = Depends(get_session)) -> list[GameItem]:
    result = await session.exec(select(GameItem).order_by(GameItem.code))
    return list(result.all())


@app.get("/nations/{nation_id}/items")
async def list_nation_items(nation_id: int, session: AsyncSession = Depends(get_session)) -> list[dict]:
    result = await session.exec(
        select(NationItem, GameItem)
        .join(GameItem, NationItem.game_item_code == GameItem.code)
        .where(NationItem.nation_id == nation_id)
        .order_by(NationItem.id.desc())
    )
    return [{**game_item.model_dump(), "id": nation_item.id, "built_at": nation_item.built_at} for nation_item, game_item in result.all()]


async def validate_item_location(session: AsyncSession, nation_id: int, location_code: str) -> None:
    nation_location = await session.get(NationLocation, (nation_id, location_code))
    if nation_location is None or not nation_location.is_discovered:
        raise HTTPException(status_code=422, detail="Location is not discovered")


@app.post("/nations/{nation_id}/items/{code}", response_model=NationItem)
async def add_item(nation_id: int, code: str, data: ItemAdd, session: AsyncSession = Depends(get_session)) -> NationItem:
    nation = await session.get(Nation, nation_id)
    if nation is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    definition = await session.get(GameItem, code)
    if definition is None:
        raise HTTPException(status_code=404, detail="Item not found")
    await validate_item_location(session, nation_id, data.location_code)
    item = NationItem(nation_id=nation_id, game_item_code=definition.code)
    session.add(item)
    session.add(NationLog(nation_id=nation_id, day=await nation_current_day(session, nation), message=f"Додано предмет: {definition.name}", amount=1))
    await session.commit()
    await session.refresh(item)
    return item


@app.post("/nations/{nation_id}/items/{code}/creation", response_model=Process)
async def start_item_creation(nation_id: int, code: str, data: ConstructionStart, session: AsyncSession = Depends(get_session)) -> Process:
    nation = await session.get(Nation, nation_id)
    if nation is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    definition = await session.get(GameItem, code)
    if definition is None:
        raise HTTPException(status_code=404, detail="Item not found")
    await validate_item_location(session, nation_id, data.location_code)
    if definition.worker_days < 1:
        raise HTTPException(status_code=422, detail="Item requires worker_days")
    if definition.max_workers < 1 or data.assigned_workers > definition.max_workers:
        raise HTTPException(status_code=422, detail=f"Item supports up to {definition.max_workers} workers")
    work_type = await session.get(WorkTypeDefinition, "creation")
    if work_type is None or work_type.mode != WorkMode.FINITE:
        raise HTTPException(status_code=422, detail="Creation work type is unavailable")
    active_processes = await session.exec(select(Process).where(Process.nation_id == nation_id, Process.status == "active"))
    if sum(process.assigned_workers for process in active_processes.all()) + data.assigned_workers > active_population(nation.population):
        raise HTTPException(status_code=422, detail="Active population limit exceeded")
    resource_rows = await session.exec(select(NationResource, Resource).join(Resource, NationResource.resource_code == Resource.code).where(NationResource.nation_id == nation_id))
    nation_resources = {resource.code: (nation_resource, resource) for nation_resource, resource in resource_rows.all()}
    for resource_code, amount in definition.construction_resources.items():
        nation_resource, resource = nation_resources.get(resource_code, (None, None))
        if not isinstance(amount, (int, float)) or amount < 0:
            raise HTTPException(status_code=422, detail="Invalid creation resource cost")
        if nation_resource is None or nation_resource.amount < amount:
            raise HTTPException(status_code=422, detail=f"Not enough resource: {resource.name if resource else resource_code}")
    for resource_code, amount in definition.construction_resources.items():
        nation_resource, resource = nation_resources[resource_code]
        nation_resource.amount -= amount
        session.add(nation_resource)
        if amount:
            session.add(NationLog(nation_id=nation_id, day=await nation_current_day(session, nation), message=f"Створення: {definition.name} — {resource.name}", amount=-amount))
    process = Process(nation_id=nation_id, location_code=data.location_code, work_type=work_type.code, mode=WorkMode.FINITE, assigned_workers=data.assigned_workers, required_worker_days=definition.worker_days, outputs={"item": {"code": definition.code, "name": definition.name}}, details={"item_code": definition.code, "creation_resources": definition.construction_resources})
    session.add(process)
    session.add(NationLog(nation_id=nation_id, day=await nation_current_day(session, nation), message=f"Розпочато створення: {definition.name}", amount=0))
    await session.commit()
    await session.refresh(process)
    return process


@app.get("/nations/{nation_id}/buildings")
async def list_nation_buildings(nation_id: int, session: AsyncSession = Depends(get_session)) -> list[dict]:
    result = await session.exec(
        select(NationBuilding, BuildingDefinition)
        .join(BuildingDefinition, NationBuilding.building_code == BuildingDefinition.code)
        .where(NationBuilding.nation_id == nation_id)
        .order_by(NationBuilding.id.desc())
    )
    return [{**definition.model_dump(), "id": building.id, "location_code": building.location_code, "built_at": building.built_at} for building, definition in result.all()]


@app.post("/nations/{nation_id}/buildings/{code}", response_model=NationBuilding)
async def build(nation_id: int, code: str, data: BuildingAdd, session: AsyncSession = Depends(get_session)) -> NationBuilding:
    nation = await session.get(Nation, nation_id)
    if nation is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    result = await session.exec(select(BuildingDefinition).where(BuildingDefinition.code == code))
    definition = result.first()
    if definition is None:
        raise HTTPException(status_code=404, detail="Building not found")
    await validate_building_location(session, nation_id, data.location_code, code)
    building = NationBuilding(nation_id=nation_id, location_code=data.location_code, building_code=definition.code)
    session.add(building)
    session.add(NationLog(nation_id=nation_id, day=await nation_current_day(session, nation), message=f"Додано будівлю: {definition.name}", amount=1))
    await session.commit()
    await session.refresh(building)
    return building


@app.post("/nations/{nation_id}/buildings/{code}/construction", response_model=Process)
async def start_construction(
    nation_id: int,
    code: str,
    data: ConstructionStart,
    session: AsyncSession = Depends(get_session),
) -> Process:
    nation = await session.get(Nation, nation_id)
    if nation is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    result = await session.exec(select(BuildingDefinition).where(BuildingDefinition.code == code))
    definition = result.first()
    if definition is None:
        raise HTTPException(status_code=404, detail="Building not found")
    await validate_building_location(session, nation_id, data.location_code, code)
    cost = definition.construction_cost
    worker_days = cost.get("worker_days", 0)
    if not isinstance(worker_days, int) or worker_days < 1:
        raise HTTPException(status_code=422, detail="Building requires worker_days")
    result = await session.exec(select(WorkTypeDefinition).where(WorkTypeDefinition.code == "building"))
    work_type = result.first()
    if work_type is None or work_type.mode != WorkMode.FINITE:
        raise HTTPException(status_code=422, detail="Building work type is unavailable")
    result = await session.exec(select(Process).where(Process.nation_id == nation_id, Process.status == "active"))
    if sum(process.assigned_workers for process in result.all()) + data.assigned_workers > active_population(nation.population):
        raise HTTPException(status_code=422, detail="Active population limit exceeded")
    result = await session.exec(
        select(NationResource, Resource)
        .join(Resource, NationResource.resource_code == Resource.code)
        .where(NationResource.nation_id == nation_id)
    )
    nation_resources = {resource.code: (nation_resource, resource) for nation_resource, resource in result.all()}
    resource_costs = cost.get("resources", {})
    for resource_code, amount in resource_costs.items():
        if not isinstance(amount, (int, float)) or amount < 0:
            raise HTTPException(status_code=422, detail="Invalid construction resource cost")
        nation_resource, resource = nation_resources.get(resource_code, (None, None))
        if nation_resource is None or nation_resource.amount < amount:
            raise HTTPException(status_code=422, detail=f"Not enough resource: {resource.name if resource else resource_code}")
    for resource_code, amount in resource_costs.items():
        nation_resource, resource = nation_resources[resource_code]
        nation_resource.amount -= amount
        session.add(nation_resource)
        if amount:
            session.add(NationLog(nation_id=nation_id, day=await nation_current_day(session, nation), message=f"Будівництво: {definition.name} — {resource.name}", amount=-amount))
    process = Process(
        nation_id=nation_id,
        location_code=data.location_code,
        work_type=work_type.code,
        mode=WorkMode.FINITE,
        assigned_workers=data.assigned_workers,
        required_worker_days=worker_days,
        outputs={"building": {"code": definition.code, "name": definition.name}},
        details={"building_code": definition.code, "construction_cost": cost},
    )
    session.add(process)
    session.add(NationLog(nation_id=nation_id, day=await nation_current_day(session, nation), message=f"Розпочато будівництво: {definition.name}", amount=0))
    await session.commit()
    await session.refresh(process)
    return process


@app.delete("/nations/{nation_id}/buildings/{building_id}", status_code=204)
async def remove_building(nation_id: int, building_id: int, session: AsyncSession = Depends(get_session)) -> None:
    building = await session.get(NationBuilding, building_id)
    if building is None or building.nation_id != nation_id:
        raise HTTPException(status_code=404, detail="Built building not found")
    definition = await session.get(BuildingDefinition, building.building_code)
    nation = await session.get(Nation, nation_id)
    await session.delete(building)
    session.add(NationLog(nation_id=nation_id, day=await nation_current_day(session, nation), message=f"Прибрано будівлю: {definition.name if definition else building_id}", amount=-1))
    await session.commit()


@app.post("/nations", response_model=Nation)
async def create_nation(
    data: NationCreate, session: AsyncSession = Depends(get_session)
) -> Nation:
    nation = Nation(name=data.name, population=data.population)
    session.add(nation)
    await session.commit()
    await session.refresh(nation)
    locations = (await session.exec(select(Location))).all()
    session.add_all([NationLocation(nation_id=nation.id, location_code=location.code, is_discovered=location.code == "starting_bay") for location in locations])
    result = await session.exec(select(Resource))
    for resource in result.all():
        session.add(
            NationResource(
                nation_id=nation.id,
                resource_code=resource.code,
                amount=data.resources.get(resource.code, 0),
            )
        )
    await session.commit()
    return nation


@app.get("/nations")
async def list_nations(session: AsyncSession = Depends(get_session)) -> list[dict]:
    result = await session.exec(select(Nation).order_by(Nation.id))
    nations = result.all()
    return [nation.model_dump() | {"current_day": await nation_current_day(session, nation)} for nation in nations]


@app.get("/nations/{nation_id}")
async def get_nation(
    nation_id: int, session: AsyncSession = Depends(get_session)
) -> dict:
    nation = await session.get(Nation, nation_id)
    if nation is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    active = active_population(nation.population)
    current_day = await nation_current_day(session, nation)
    result = await session.exec(
        select(Process).where(
            Process.nation_id == nation_id, Process.status == "active"
        )
    )
    process_rows = list(result.all())
    result = await session.exec(
        select(NationResource, Resource)
        .join(Resource, NationResource.resource_code == Resource.code)
        .where(NationResource.nation_id == nation_id)
        .order_by(Resource.order, Resource.code)
    )
    resource_rows = result.all()
    result = await session.exec(select(WorkTypeDefinition))
    work_types = {work_type.code: work_type for work_type in result.all()}
    housing_capacity = await building_capacity(session, nation_id, BuildingType.HOUSING)
    warehouse_capacity = await building_capacity(session, nation_id, BuildingType.WAREHOUSE)
    storage_used = sum(
        nation_resource.amount * resource.storage_coefficient
        for nation_resource, resource in resource_rows
        if not resource.is_system
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
    if nation.population + data.amount > await building_capacity(session, nation_id, BuildingType.HOUSING):
        raise HTTPException(status_code=422, detail="Недостатньо житла для збільшення населення")
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
            NationResource.resource_code == resource_definition.code,
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
                day=await nation_current_day(session, nation),
                message=f"Ручна зміна: {resource_definition.name}",
                amount=current_amount - previous_amount,
            )
        )
    session.add(nation_resource)
    await session.commit()
    await session.refresh(nation)
    return nation


@app.post("/nations/{nation_id}/resource-purchases", response_model=Nation)
async def purchase_resources(
    nation_id: int,
    data: ResourcePurchase,
    session: AsyncSession = Depends(get_session),
) -> Nation:
    nation = await session.get(Nation, nation_id)
    if nation is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    if any(amount < 0 for amount in data.resources.values()):
        raise HTTPException(status_code=422, detail="Purchase amounts cannot be negative")
    purchases = {code: amount for code, amount in data.resources.items() if amount > 0}
    if not purchases:
        raise HTTPException(status_code=422, detail="Choose at least one resource")
    result = await session.exec(
        select(NationResource, Resource)
        .join(Resource, NationResource.resource_code == Resource.code)
        .where(NationResource.nation_id == nation_id)
    )
    resources = {resource.code: (nation_resource, resource) for nation_resource, resource in result.all()}
    points, _ = resources.get("general_points", (None, None))
    if points is None:
        raise HTTPException(status_code=422, detail="General points are unavailable")
    for code in purchases:
        if code == "general_points" or code not in resources:
            raise HTTPException(status_code=422, detail="Unknown purchasable resource")
    total_cost = sum(purchases.values()) * GENERAL_POINT_RESOURCE_COST
    if points.amount < total_cost:
        raise HTTPException(status_code=422, detail="Not enough general points")
    used_storage = sum(
        nation_resource.amount * resource.storage_coefficient
        for code, (nation_resource, resource) in resources.items()
        if not resource.is_system
    )
    purchased_storage = sum(purchases[code] * resources[code][1].storage_coefficient for code in purchases if not resources[code][1].is_system)
    if used_storage + purchased_storage > await building_capacity(session, nation_id, BuildingType.WAREHOUSE):
        raise HTTPException(status_code=422, detail="Not enough warehouse capacity")
    points.amount -= total_cost
    session.add(points)
    day = await nation_current_day(session, nation)
    session.add(NationLog(nation_id=nation_id, day=day, message="Purchase: general points", amount=-total_cost))
    for code, amount in purchases.items():
        nation_resource, resource = resources[code]
        nation_resource.amount += amount
        session.add(nation_resource)
        session.add(NationLog(nation_id=nation_id, day=day, message=f"Purchase: {resource.name}", amount=amount))
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
    if work_type.code == "investigation":
        raise HTTPException(status_code=422, detail="Start investigations from the location map")
    if work_type.code == "building":
        raise HTTPException(status_code=422, detail="Start construction from buildings")
    if work_type.code == "creation":
        raise HTTPException(status_code=422, detail="Start item creation from items")
    building = None
    capability = None
    if data.nation_building_id is not None:
        building = await session.get(NationBuilding, data.nation_building_id)
        if building is None or building.nation_id != nation_id:
            raise HTTPException(status_code=422, detail="Nation building not found")
        if building.location_code != data.location_code:
            raise HTTPException(status_code=422, detail="Nation building is not at this location")
        capability = await session.get(BuildingWorkTypeCapability, (building.building_code, data.work_type))
        if capability is None:
            raise HTTPException(status_code=422, detail="Building does not support this work type")
    nation_location = await session.get(NationLocation, (nation_id, data.location_code))
    if nation_location is None or not nation_location.is_discovered:
        raise HTTPException(status_code=422, detail="Location is not discovered")
    result = await session.exec(select(LocationWorkType).where(LocationWorkType.location_code == data.location_code, LocationWorkType.work_type_code == data.work_type))
    if result.first() is None:
        raise HTTPException(status_code=422, detail="Work type is not available at this location")
    if len(data.nation_item_ids) != len(set(data.nation_item_ids)):
        raise HTTPException(status_code=422, detail="Nation items must not be repeated")
    nation_items = []
    for item_id in data.nation_item_ids:
        item = await session.get(NationItem, item_id)
        if item is None or item.nation_id != nation_id:
            raise HTTPException(status_code=422, detail="Nation item not found")
        nation_items.append(item)
    result = await session.exec(select(WorkTypeItemRequirement).where(WorkTypeItemRequirement.work_type_code == data.work_type))
    requirements = result.all()
    selected_counts: dict[str, int] = {}
    for item in nation_items:
        selected_counts[item.game_item_code] = selected_counts.get(item.game_item_code, 0) + 1
    for requirement in requirements:
        if selected_counts.get(requirement.item_code, 0) < requirement.quantity:
            raise HTTPException(status_code=422, detail=f"Work type requires {requirement.quantity} {requirement.item_code}")
    if building is not None:
        result = await session.exec(select(BuildingItemCapability).where(BuildingItemCapability.building_code == building.building_code))
        item_capabilities = {link.item_code: link.capacity for link in result.all()}
        active_item_ids = (await session.exec(
            select(ProcessNationItem.nation_item_id)
            .join(Process, ProcessNationItem.process_id == Process.id)
            .where(Process.nation_building_id == building.id, Process.status == "active")
        )).all()
        active_items = [await session.get(NationItem, item_id) for item_id in active_item_ids]
        active_counts: dict[str, int] = {}
        for item in active_items + nation_items:
            if item is not None:
                active_counts[item.game_item_code] = active_counts.get(item.game_item_code, 0) + 1
        for item_code, count in active_counts.items():
            if item_code in item_capabilities and count > item_capabilities[item_code]:
                raise HTTPException(status_code=422, detail=f"Building capacity exceeded for {item_code}")
    mode = data.mode if work_type.code == "other" else WorkMode(work_type.mode)
    if mode == WorkMode.FINITE and data.required_worker_days is None:
        raise HTTPException(
            status_code=422, detail="Finite processes require worker days"
        )
    if mode == WorkMode.CONTINUOUS and data.required_worker_days is not None:
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
    if capability is not None and capability.max_workers is not None and data.assigned_workers > capability.max_workers:
        raise HTTPException(status_code=422, detail=f"Building supports up to {capability.max_workers} workers")
    process = Process(nation_id=nation_id, **data.model_dump(exclude={"nation_item_ids"}) | {"work_type": work_type.code, "mode": mode})
    session.add(process)
    await session.flush()
    session.add_all([ProcessNationItem(process_id=process.id, nation_item_id=item.id) for item in nation_items])
    await session.commit()
    await session.refresh(process)
    return process


@app.post("/nations/{nation_id}/locations/{location_code}/discovery", response_model=Process)
async def start_location_discovery(
    nation_id: int,
    location_code: str,
    data: DiscoveryStart,
    session: AsyncSession = Depends(get_session),
) -> Process:
    nation = await session.get(Nation, nation_id)
    target = await session.get(NationLocation, (nation_id, location_code))
    location = await session.get(Location, location_code)
    if nation is None or target is None or location is None:
        raise HTTPException(status_code=404, detail="Nation or location not found")
    if target.is_discovered:
        raise HTTPException(status_code=422, detail="Location is already discovered")
    neighbors = (await session.exec(select(LocationNeighbor))).all()
    neighbor_codes = [edge.neighbor_location_code if edge.location_code == location_code else edge.location_code for edge in neighbors if location_code in {edge.location_code, edge.neighbor_location_code}]
    discovered_neighbors = [await session.get(NationLocation, (nation_id, code)) for code in neighbor_codes]
    if not any(neighbor and neighbor.is_discovered for neighbor in discovered_neighbors):
        raise HTTPException(status_code=422, detail="Location has no discovered neighbor")
    result = await session.exec(select(WorkTypeDefinition).where(WorkTypeDefinition.code == "investigation"))
    work_type = result.first()
    if work_type is None or work_type.mode != WorkMode.FINITE:
        raise HTTPException(status_code=422, detail="Investigation work type is unavailable")
    result = await session.exec(select(LocationWorkType).where(LocationWorkType.location_code == location_code, LocationWorkType.work_type_code == "investigation"))
    if result.first() is None:
        raise HTTPException(status_code=422, detail="Investigation is not available at this location")
    result = await session.exec(select(Process).where(Process.nation_id == nation_id, Process.status == "active"))
    active_processes = result.all()
    if any(process.details.get("discovery_location_code") == location_code for process in active_processes):
        raise HTTPException(status_code=422, detail="Location discovery is already in progress")
    if sum(process.assigned_workers for process in active_processes) + data.assigned_workers > active_population(nation.population):
        raise HTTPException(status_code=422, detail="Active population limit exceeded")
    if location.worker_days < 1:
        raise HTTPException(status_code=422, detail="Location requires worker days")
    process = Process(nation_id=nation_id, location_code=location_code, work_type=work_type.code, mode=WorkMode.FINITE, assigned_workers=data.assigned_workers, required_worker_days=location.worker_days, details={"discovery_location_code": location_code})
    session.add(process)
    session.add(NationLog(nation_id=nation_id, day=await nation_current_day(session, nation), message=f"Розпочато відкриття локації: {location.name}", amount=0))
    await session.commit()
    await session.refresh(process)
    return process


@app.get("/nations/{nation_id}/processes")
async def list_processes(
    nation_id: int, session: AsyncSession = Depends(get_session)
) -> list[dict]:
    result = await session.exec(
        select(Process, WorkTypeDefinition)
        .join(WorkTypeDefinition, Process.work_type == WorkTypeDefinition.code)
        .where(Process.nation_id == nation_id)
        .order_by(Process.id.desc())
    )
    processes = [process for process, _ in result.all()]
    process_ids = [process.id for process in processes]
    result = await session.exec(select(ProcessNationItem).where(ProcessNationItem.process_id.in_(process_ids))) if process_ids else None
    items: dict[int, list[int]] = {}
    if result is not None:
        for link in result.all():
            items.setdefault(link.process_id, []).append(link.nation_item_id)
    result = await session.exec(select(NationBuilding).where(NationBuilding.nation_id == nation_id))
    building_codes = {building.id: building.building_code for building in result.all()}
    result = await session.exec(select(BuildingWorkTypeCapability))
    capabilities = {(capability.building_code, capability.work_type_code): capability for capability in result.all()}
    return [{**process.model_dump(), "nation_item_ids": items.get(process.id, []), "output_multiplier": (capabilities.get((building_codes.get(process.nation_building_id), process.work_type)).output_multiplier or 1) if process.nation_building_id in building_codes and (building_codes[process.nation_building_id], process.work_type) in capabilities else 1} for process in processes]


@app.post("/nations/{nation_id}/personal-tasks", response_model=PersonalTask)
async def create_personal_task(
    nation_id: int,
    data: PersonalTaskCreate,
    session: AsyncSession = Depends(get_session),
) -> PersonalTask:
    if await session.get(Nation, nation_id) is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    task = PersonalTask(nation_id=nation_id, **data.model_dump())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@app.get("/nations/{nation_id}/personal-tasks", response_model=list[PersonalTask])
async def list_personal_tasks(
    nation_id: int, session: AsyncSession = Depends(get_session)
) -> list[PersonalTask]:
    result = await session.exec(
        select(PersonalTask)
        .where(PersonalTask.nation_id == nation_id)
        .order_by(PersonalTask.id.desc())
    )
    return list(result.all())


@app.patch("/personal-tasks/{task_id}", response_model=PersonalTask)
async def update_personal_task(
    task_id: int,
    action: PersonalTaskAction,
    session: AsyncSession = Depends(get_session),
) -> PersonalTask:
    task = await session.get(PersonalTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Personal task not found")
    if action in {PersonalTaskAction.RESTART, PersonalTaskAction.CONTINUE}:
        if task.status != PersonalTaskStatus.CANCELLED or task.task_type == "one_time":
            raise HTTPException(status_code=422, detail="Only cancelled recurring tasks can be restarted")
        if action == PersonalTaskAction.RESTART:
            task = PersonalTask(
                nation_id=task.nation_id,
                name=task.name,
                description=task.description,
                reward=task.reward,
                task_type=task.task_type,
            )
        else:
            task.status = PersonalTaskStatus.ACTIVE
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task
    if task.status != PersonalTaskStatus.ACTIVE:
        raise HTTPException(status_code=422, detail="Personal task is already closed")
    if action == PersonalTaskAction.CANCEL:
        task.status = PersonalTaskStatus.CANCELLED
    else:
        result = await session.exec(
            select(NationResource)
            .join(Resource, NationResource.resource_code == Resource.code)
            .where(NationResource.nation_id == task.nation_id, Resource.code == "general_points")
        )
        points = result.first()
        if points is None:
            raise HTTPException(status_code=422, detail="General points are unavailable")
        points.amount += task.reward
        task.counter += 1
        session.add(points)
        nation = await session.get(Nation, task.nation_id)
        session.add(NationLog(
            nation_id=task.nation_id,
            day=await nation_current_day(session, nation),
            message=f"Виконано особисту задачу: {task.name}",
            amount=task.reward,
        ))
        if task.task_type == "one_time":
            task.status = PersonalTaskStatus.DONE
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


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
    status = data.status.value if data.status is not None else process.status
    other_workers = sum(
        item.assigned_workers for item in result.all() if item.id != process.id
    )
    if status == "active" and other_workers + assigned_workers > active_population(
        nation.population
    ):
        raise HTTPException(status_code=422, detail="Active population limit exceeded")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(process, field, status if field == "status" else value)
    session.add(process)
    await session.commit()
    await session.refresh(process)
    return process
