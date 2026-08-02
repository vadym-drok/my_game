from fastapi import Depends, FastAPI, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.day_service import advance_day
from app.db import get_session
from app.models import DayReport, Settlement
from app.schemas import DayAdvance, SettlementCreate

app = FastAPI(title="My Game API")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


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
    data: DayAdvance,
    session: AsyncSession = Depends(get_session),
) -> DayReport:
    settlement = await session.get(Settlement, settlement_id)
    if settlement is None:
        raise HTTPException(status_code=404, detail="Settlement not found")
    try:
        return await advance_day(session, settlement, data.assignments)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
