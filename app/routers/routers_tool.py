

from fastapi import APIRouter, Depends, HTTPException
from pydantic_settings.sources.providers import aws
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, exists, func
from sqlalchemy.orm import selectinload, with_loader_criteria

from app.table_models.table_repair import Repair
from app.table_models.table_tool_model import ToolModel
from app.table_models.table_location import Location
from app.table_models.table_user import User
from app.table_models.table_tool_issue import ToolIssue

from app.enum_file import StatusEnum

from app.database_depends import get_async_db
from app.table_models.table_tool import Tool
from app.schemas_pydantic.tool_pydantic import (ToolResponse,
                                                ToolCreate,
                                                ToolUpdate,
                                                ToolShortResponse,
                                                ToolFilter,
                                                ListToolResponse)

from app.helpers import (correct_name,
                         select_response,
                         update_model,
                         create_model,
                         get_by_id,
                         soft_delete_model)

from app.core.security import get_current_manager, get_current_storekeeper, get_current_admin

router = APIRouter(prefix="/tools", tags=["Tools"])


@router.post("/", status_code=201, response_model=ToolResponse)
async def create_tool(new_tool: ToolCreate,
                      _: User = Depends(get_current_manager), # проверка, что только менеджер или админ могут создавать инструмент
                      db: AsyncSession = Depends(get_async_db)):
    # сначала приводим строки к корректному виду:
    new_tool = correct_name(pydantic_model=new_tool)

    # проверка на то, есть ли в базе такая модель инструмента
    db_tool_model = await get_by_id(model_class=ToolModel, obj_id=new_tool.model_id, db=db)

    if db_tool_model is None:
        raise HTTPException(status_code=404, detail="Нет такой модели инструмента, создайте сначала модель инструмента")

    # проверяем существует ли такая локация:
    db_location = await get_by_id(model_class=Location, obj_id=new_tool.location_id, db=db)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Нет такой локации, создайте сначала локацию")

    tool = await create_model(model_class=Tool, pydantic_schema=new_tool, db=db)
    stmt = select_response(Tool).where(Tool.id == tool.id).options(selectinload(Tool.tool_model))

    return await db.scalar(stmt)


@router.get("/", response_model=ListToolResponse)
async def get_all_tools(filters: ToolFilter = Depends(),
                         db: AsyncSession = Depends(get_async_db)):
    """Фильтрация инструмента"""
    filters_list = []

    # поиск
    if filters.search is not None:
        search_value = filters.search.strip()
        if search_value:
            filters_list.append(Tool.serial_number.ilike(f"%{search_value}%"))

    # Списан/не списан
    if filters.is_active is not None:
        filters_list.append(Tool.is_active.is_(filters.is_active))

    # есть/нет серийного номера
    if filters.has_serial is not None:
        filters_list.append(
            Tool.serial_number.is_not(None)
            if filters.has_serial else
            Tool.serial_number.is_(None)
        )

    # ремонтировался/не ремонтировался когда-либо
    if filters.has_repairs is not None:
        repair_exists = exists().where(Tool.id == Repair.tool_id)
        filters_list.append(repair_exists
                            if filters.has_repairs else
                            ~repair_exists)

    # по бренду
    if filters.brand is not None:
        search_brand = filters.brand.strip()
        if search_brand:
            filters_list.append(
                Tool.tool_model.has(
                    ToolModel.brand.ilike(f"%{search_brand}%")
                )
            )

    # по категории
    if filters.category is not None:
        search_category = filters.category.strip()
        if search_category:
            filters_list.append(
                Tool.tool_model.has(
                    ToolModel.category.ilike(f"%{search_category}%")
                )
            )

    # по статусу
    if filters.status is not None:
        filters_list.append(Tool.status == filters.status)

    # по ID модели
    if filters.model_id is not None:
        filters_list.append(Tool.model_id == filters.model_id)

    # по ID локации
    if filters.location_id is not None:
        filters_list.append(Tool.location_id == filters.location_id)

    # по ID сотрудника
    if filters.employee_id is not None:
        filters_list.append(
            Tool.tool_issues.any(
                ToolIssue.employee_id == filters.employee_id,
                ToolIssue.return_date.is_(None),
            )
        )

    # проверка корректности дат:
    if (filters.purchase_date_from is not None and
            filters.purchase_date_to is not None
            and filters.purchase_date_from > filters.purchase_date_to
    ):
        raise HTTPException(status_code=400, detail="проверьте корректность указанных дат")

    # по дате покупки с какого числа
    if filters.purchase_date_from is not None:
        filters_list.append(Tool.purchase_date >= filters.purchase_date_from)

    # по дате покупки по какое число:
    if filters.purchase_date_to is not None:
        filters_list.append(Tool.purchase_date <= filters.purchase_date_to)

    # total подсчет
    total_stmt = select(func.count()).select_from(Tool).where(*filters_list)
    total = await db.scalar(total_stmt) or 0

    # применение фильтров, пагинация и запрос в бд
    stmt = (
        select(Tool)
        .options(
            selectinload(Tool.tool_model)
                 )
        .where(*filters_list)
        .order_by(Tool.id)
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




@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool_by_id(tool_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = (select_response(Tool)
            .where(Tool.id == tool_id)
            .options(selectinload(Tool.tool_model)
                     )
            )
    tool = (await db.scalars(stmt)).one_or_none()

    if tool is None:
        raise HTTPException(status_code=404, detail=f"tool with id={tool_id} not found")

    return tool


@router.patch("/{tool_id}", response_model=ToolResponse)
async def patch_tool(tool_id: int,
                     new_patch: ToolUpdate,
                     manager: User = Depends(get_current_manager), # только менеджер может обновить
                     db: AsyncSession = Depends(get_async_db)):
    tool = await get_by_id(Tool, tool_id, db=db)

    if tool is None:
        raise HTTPException(status_code=404, detail=f"tool with id={tool_id} not found")

    # переносим все в словарь
    data = new_patch.model_dump(exclude_unset=True)

    if not data:
        raise HTTPException(status_code=400, detail="You submitted an empty update request.")

    # Проверка на то, передавалось ли поле model_id. Если передавалось, проверяем есть ли в базе
    if "model_id" in data:
        tool_model = await get_by_id(ToolModel, data["model_id"], db)
        if tool_model is None:
            raise HTTPException(status_code=404, detail=f"tool_model with id={data['model_id']} not found")
    # Проверка на то, передавалась ли location_id. Если передавалось, проверка на наличие в базе
    if "location_id" in data:
        location = await get_by_id(Location, data["location_id"], db)
        if location is None:
            raise HTTPException(status_code=404, detail=f"location with id={data['location_id']} not found")

    # обновляем инструмент
    update_model(obj=tool, data=data)
    await db.commit()
    # Заново читаем обновленный объект. Нам нужно подгрузить модель инструмента для корректного ответа
    stmt = select_response(Tool).where(Tool.id == tool_id).options(selectinload(Tool.tool_model))
    updated_tool = (await db.scalar(stmt))
    return updated_tool

@router.delete("/{tool_id}")
async def del_tool(tool_id: int,
                   _: User = Depends(get_current_manager), # проверка на кладовщика
                   db: AsyncSession = Depends(get_async_db)):

    stmt = (select(Tool)
            .where(Tool.id == tool_id, Tool.is_active.is_(True))
            .options(selectinload(Tool.location),selectinload(Tool.tool_model))
            )
    tool: Tool | None = (await db.scalars(stmt)).one_or_none()

    if tool is None:
        raise HTTPException(404, "Инструмент не найден")

    if tool.location is None:
        raise HTTPException(400, "У инструмента нет локации")

    if not tool.location.is_active:
        raise HTTPException(400, "Локация неактивна")

    if tool.location.name != "Склад":
        raise HTTPException(
            400,
            f"Инструмент находится в '{tool.location.name}', а не на складе"
        )

    tool.status = StatusEnum.WRITTEN_OFF
    tool.is_active = False
    try:
        await db.commit()
    except:
        await db.rollback()
        raise

    return {
        "message": "Инструмент списан",
        "tool_id": tool.id
    }





