from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from datetime import datetime, UTC

from app.database_depends import get_db

from app.table_models.table_tool_movement import ToolMovement
from app.schemas_pydantic.tool_movement_pydantic import (ToolMovementCreate,
                                                         ToolMovementResponse)

from app.table_models.table_tool import Tool
from app.table_models.table_employee import Employee
from app.table_models.table_location import Location

from app.helpers import (select_response,
                         )


router = APIRouter(prefix='/tool-movements', tags=["ToolMovements"])

@router.post("/", status_code=201, response_model=ToolMovementResponse)
async def create_new_tool_movement(new_tool_movement: ToolMovementCreate, db: AsyncSession = Depends(get_db)):

    # Проверяем, существует ли перемещаемый инструмент,
    tool_stmt = select_response(Tool).where(Tool.id == new_tool_movement.tool_id)
    tool: Tool | None = (await db.scalars(tool_stmt)).one_or_none()
    if tool is None:
        raise HTTPException(status_code=404, detail=f"tool with id={new_tool_movement.tool_id} not found or inactive")

    # Проверяем Человек, которому перемещается инструмент,
    employee_stmt = select_response(Employee).where(Employee.id == new_tool_movement.employee_id)
    employee: Employee | None = (await db.scalars(employee_stmt)).one_or_none()
    if employee is None:
        raise HTTPException(status_code=404, detail=f"Employee with id={new_tool_movement.employee_id} not found or inactive")

    # загружаем id всех существующих True локаций
    all_locations_stmt = select(Location.id).where(Location.is_active.is_(True))
    id_list_all_locations = (await db.scalars(all_locations_stmt)).all()

    # проверка локации, откуда перемещается товар:
    if new_tool_movement.from_location_id not in id_list_all_locations:
        raise HTTPException(status_code=404, detail=f"from_location with id={new_tool_movement.from_location_id}not found or inactive")

    # проверка локации, куда перемещается товар:
    if new_tool_movement.to_location_id not in id_list_all_locations:
        raise HTTPException(status_code=404, detail=f"to_location with id={new_tool_movement.to_location_id}not found or inactive")

    # Проверим, совпадает ли локация, в которой сейчас находится инструмент с локацией new_tool_movement.from_location_id
    if tool.location_id != new_tool_movement.from_location_id:
        raise HTTPException(status_code=404, detail="tool.location_id != new_tool_movement.from_location_id")

    # создаем новую запись
    tool_movement = ToolMovement(**new_tool_movement.model_dump(exclude_unset=True))
    # добавляем запись в базу
    db.add(tool_movement)
    # меняем локацию в таблице с инструментом
    tool.location_id = new_tool_movement.to_location_id
    # теперь коммитим все в базе
    await db.commit()
    await db.refresh(tool_movement)

    return tool_movement

@router.get("/", response_model=list[ToolMovementResponse])
async def get_all_tool_movements(db: AsyncSession = Depends(get_db)):
    tool_movements = (await db.scalars(select(ToolMovement))).all()
    return tool_movements

@router.get("/tool_movement_id", response_model=ToolMovementResponse)
async def get_tool_movement_by_id(tool_movement_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(ToolMovement).where(ToolMovement.id == tool_movement_id)
    tool_movement: ToolMovement | None = (await db.scalars(stmt)).one_or_none()
    if tool_movement is None:
        raise HTTPException(status_code=404, detail=f"tool movement with id={tool_movement_id} not found")

    return tool_movement

