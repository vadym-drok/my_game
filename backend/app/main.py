from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.day_service import advance_day
from app.db import get_session
from app.models import DayReport, Process, Settlement
from app.schemas import ProcessCreate, ProcessMode, ProcessUpdate, SettlementCreate

app = FastAPI(title="My Game API")


@app.post("/settlements", response_model=Settlement)
async def create_settlement(
    data: SettlementCreate, session: AsyncSession = Depends(get_session)
) -> Settlement:
    settlement = Settlement.model_validate(data)
    session.add(settlement)
    await session.commit()
    await session.refresh(settlement)
    return settlement


@app.get("/settlements/{settlement_id}", response_model=Settlement)
async def get_settlement(
    settlement_id: int, session: AsyncSession = Depends(get_session)
) -> Settlement:
    settlement = await session.get(Settlement, settlement_id)
    if settlement is None:
        raise HTTPException(status_code=404, detail="Settlement not found")
    return settlement


@app.post("/settlements/{settlement_id}/advance-day", response_model=DayReport)
async def advance_settlement_day(
    settlement_id: int,
    session: AsyncSession = Depends(get_session),
) -> DayReport:
    settlement = await session.get(Settlement, settlement_id)
    if settlement is None:
        raise HTTPException(status_code=404, detail="Settlement not found")
    try:
        return await advance_day(session, settlement)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/settlements/{settlement_id}/processes", response_model=Process)
async def create_process(
    settlement_id: int,
    data: ProcessCreate,
    session: AsyncSession = Depends(get_session),
) -> Process:
    if await session.get(Settlement, settlement_id) is None:
        raise HTTPException(status_code=404, detail="Settlement not found")
    if data.mode == ProcessMode.FINITE and data.required_worker_days is None:
        raise HTTPException(
            status_code=422, detail="Finite processes require worker days"
        )
    if data.mode == ProcessMode.CONTINUOUS and data.required_worker_days is not None:
        raise HTTPException(
            status_code=422, detail="Continuous processes cannot have worker days"
        )
    process = Process(settlement_id=settlement_id, **data.model_dump())
    session.add(process)
    await session.commit()
    await session.refresh(process)
    return process


@app.get("/settlements/{settlement_id}/processes", response_model=list[Process])
async def list_processes(
    settlement_id: int, session: AsyncSession = Depends(get_session)
) -> list[Process]:
    result = await session.exec(
        select(Process).where(Process.settlement_id == settlement_id)
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
