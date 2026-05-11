from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from datetime import datetime, UTC

from app.database_depends import get_db

from app.schemas_pydantic.repair_pydantic import (RepairCreate,
                                                  RepairUpdate,
                                                  RepairResponse)

from app.table_models.table_repair import Repair
from app.table_models.table_tool import Tool

from app.enum_file import StatusEnum
from app.helpers import *

router = APIRouter(prefix="/repairs", tags=["Repairs"])

@router.post("/", status_code=201, response_model=RepairResponse)
async def create_new_repair(new_repair: RepairCreate, db: AsyncSession = Depends(get_db)):
    # проверка, активен ли инструмент
    tool_stmt = select_response(Tool).where(Tool.id == new_repair.tool_id)
    tool: Tool | None = (await db.scalars(tool_stmt)).one_or_none()
    if tool is None:
        raise HTTPException(status_code=404, detail=f"Tool with id={new_repair.tool_id} not found or inactive")

    # на всякий случай проверка статуса инструмента, если забыли списать
    if tool.status == StatusEnum.WRITTEN_OFF:
        raise HTTPException(status_code=400, detail="The instrument's status is 'decommissioned'. It cannot be repaired.")

    # проверка в какой локации находится инструмент. Ремонт - location.id == 2:
    if tool.location_id != 2:
        raise HTTPException(status_code=400, detail=f"First, move the tool with id={new_repair.tool_id} to the 'repair' location")

    # создаем новую запись
    repair = Repair(**new_repair.model_dump(exclude_unset=True))
    db.add(repair)
    # возможно стоит эту логику перенести в другой эндпоинт.. но пока пусть будет тут
    # меняем статус инструмента на "сломался"
    tool.status = StatusEnum.BROKEN
    try:
        await db.commit()
    except:
        await db.rollback()
        raise
    await db.refresh(repair)
    return repair

@router.get("/", response_model=list[RepairResponse])
async def get_all_repairs(db: AsyncSession = Depends(get_db)):
    stmt = select(Repair)
    list_repairs = (await db.scalars(stmt)).all()
    return list_repairs

@router.get("/{repair_id}", response_model=RepairResponse)
async def get_repair_by_id(repair_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Repair).where(Repair.id == repair_id)
    repair: Repair | None = (await db.scalars(stmt)).one_or_none()
    if repair is None:
        raise HTTPException(status_code=404, detail=f"repair with id={repair_id} not found")

    return repair