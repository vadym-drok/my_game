from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.day_service import sync_nation
from app.db import get_session
from app.models import DayReport, Nation, Process
from app.schemas import NationCreate, ProcessCreate, ProcessMode, ProcessUpdate

app = FastAPI(title="My Game API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3010"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/nations", response_model=Nation)
async def create_nation(
    data: NationCreate, session: AsyncSession = Depends(get_session)
) -> Nation:
    nation = Nation.model_validate(data)
    session.add(nation)
    await session.commit()
    await session.refresh(nation)
    return nation


@app.get("/nations/{nation_id}", response_model=Nation)
async def get_nation(nation_id: int, session: AsyncSession = Depends(get_session)) -> Nation:
    nation = await session.get(Nation, nation_id)
    if nation is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    return nation


@app.post("/nations/{nation_id}/sync", response_model=list[DayReport])
async def sync_nation_days(
    nation_id: int,
    session: AsyncSession = Depends(get_session),
) -> list[DayReport]:
    nation = await session.get(Nation, nation_id)
    if nation is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    try:
        return await sync_nation(session, nation)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/nations/{nation_id}/processes", response_model=Process)
async def create_process(
    nation_id: int,
    data: ProcessCreate,
    session: AsyncSession = Depends(get_session),
) -> Process:
    if await session.get(Nation, nation_id) is None:
        raise HTTPException(status_code=404, detail="Nation not found")
    if data.mode == ProcessMode.FINITE and data.required_worker_days is None:
        raise HTTPException(
            status_code=422, detail="Finite processes require worker days"
        )
    if data.mode == ProcessMode.CONTINUOUS and data.required_worker_days is not None:
        raise HTTPException(
            status_code=422, detail="Continuous processes cannot have worker days"
        )
    process = Process(nation_id=nation_id, **data.model_dump())
    session.add(process)
    await session.commit()
    await session.refresh(process)
    return process


@app.get("/nations/{nation_id}/processes", response_model=list[Process])
async def list_processes(
    nation_id: int, session: AsyncSession = Depends(get_session)
) -> list[Process]:
    result = await session.exec(
        select(Process).where(Process.nation_id == nation_id)
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
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(process, field, value)
    session.add(process)
    await session.commit()
    await session.refresh(process)
    return process
