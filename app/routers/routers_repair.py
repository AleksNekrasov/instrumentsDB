from fastapi import APIRouter, Depends, HTTPException

from app.database_depends import get_async_db

from app.schemas_pydantic.repair_pydantic import (RepairCreate,
                                                  RepairUpdate,
                                                  RepairResponse,
                                                  RepairFilter,
                                                  ListRepairResponse, )

from app.table_models.table_repair import Repair
from app.table_models.table_user import User

from app.helpers import *
from sqlalchemy import select, exists, func

from app.core.security import get_current_storekeeper

router = APIRouter(prefix="/repairs", tags=["Repairs"])


@router.post("/", status_code=201, response_model=RepairResponse)
async def create_new_repair(new_repair: RepairCreate,
                            storekeeper: User = Depends(get_current_storekeeper),
                            db: AsyncSession = Depends(get_async_db)):
    # проверка, активен ли инструмент
    tool_stmt = select_response(Tool).where(Tool.id == new_repair.tool_id)
    tool: Tool | None = (await db.scalars(tool_stmt)).one_or_none()
    if tool is None:
        raise HTTPException(status_code=404, detail=f"Tool with id={new_repair.tool_id} not found or inactive")

    # на всякий случай проверка статуса инструмента, если списанный, но не удаленный
    if tool.status == StatusEnum.WRITTEN_OFF:
        raise HTTPException(status_code=400,
                            detail="The instrument's status is 'decommissioned'. It cannot be repaired.")

    # проверка в какой локации находится инструмент. Ремонт - location.id == 2:
    if tool.location_id != 2:
        raise HTTPException(status_code=400,
                            detail=f"First, move the tool with id={new_repair.tool_id} to the 'repair' location")

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


@router.get("/", response_model=ListRepairResponse)
async def get_all_repairs(filters: RepairFilter = Depends(),
                          db: AsyncSession = Depends(get_async_db)):
    """фильтрация ремонта"""
    filters_list = []

    # поиск
    if filters.search is not None:
        search_value = filters.search.strip()
        if search_value:
            filters_list.append(Repair.description.ilike(f"%{search_value}%"))

    # поиск инструмента по id
    if filters.tool_id is not None:
        filters_list.append(Repair.tool_id == filters.tool_id)

    # date
    if filters.date_from and filters.date_to and filters.date_from > filters.date_to:
        raise HTTPException(status_code=400, detail="Дата 'date_to' не может быть позже даты 'date_from'")

    # date_from
    if filters.date_from is not None:
        filters_list.append(Repair.repair_date >= filters.date_from)

    # date_to
    if filters.date_to is not None:
        filters_list.append(Repair.repair_date <= filters.date_to)

    # min max
    if filters.min_cost is not None and filters.max_cost is not None and filters.min_cost > filters.max_cost:
        raise HTTPException(status_code=400,
                            detail="минимальное значение цены не может превышать максимальное значение цены")

    # min
    if filters.min_cost is not None:
        filters_list.append(Repair.cost >= filters.min_cost)

    # max
    if filters.max_cost is not None:
        filters_list.append(Repair.cost <= filters.max_cost)

    # есть ли цена у ремонта
    if filters.has_cost is not None:
        filters_list.append(
            Repair.cost.is_not(None)
            if filters.has_cost
            else Repair.cost.is_(None)
        )

    # tolal подсчет
    total_stmt = select(func.count()).select_from(Repair).where(*filters_list)
    total = await db.scalar(total_stmt) or 0

    # применение фильтров, пагинация и запрос в бд
    stmt = (
        select(Repair)
        .where(*filters_list)
        .order_by(Repair.repair_date.desc())
        .offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
    )
    items = (await db.scalars(stmt)).all()

    return {
        "items": items,
        "total": total,
        "page": filters.page,
        "page_size": filters.page_size
    }


@router.get("/{repair_id}", response_model=RepairResponse)
async def get_repair_by_id(repair_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(Repair).where(Repair.id == repair_id)
    repair: Repair | None = (await db.scalars(stmt)).one_or_none()
    if repair is None:
        raise HTTPException(status_code=404, detail=f"repair with id={repair_id} not found")

    return repair
