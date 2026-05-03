from fastapi import APIRouter, Depends, HTTPException
from pydantic_settings.sources.providers import aws
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload, with_loader_criteria

from app.table_models.table_tool_model import ToolModel
from app.table_models.table_location import Location
from app.table_models.table_employee import Employee

from app.enum_file import StatusEnum

from app.database_depends import get_db
from app.table_models.table_tool import Tool
from app.schemas_pydantic.tool_pydantic import (ToolResponse,
                                                ToolCreate,
                                                ToolUpdate,
                                                ToolShortResponse)

from app.helpers import (correct_name,
                         select_response,
                         update_model,
                         create_model,
                         get_by_id,
                         soft_delete_model)

router = APIRouter(prefix="/tools", tags=["Tools"])


@router.post("/", status_code=201, response_model=ToolResponse)
async def create_tool(new_tool: ToolCreate, db: AsyncSession = Depends(get_db)):
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

    # проверим сотрудника, если передали его ID:
    # if new_tool.employee_id is not None:
    #     db_employee = await get_by_id(model_class=Employee, obj_id=new_tool.employee_id, db=db)
    #     if db_employee is None:
    #         raise HTTPException(status_code=404, detail="Нет такого сотрудника, сначала создайте сотрудника")

    # создаем инструмент
    # tool = Tool(**new_tool.model_dump(exclude_unset=True))
    # db.add(tool)
    # await db.commit()
    # await db.refresh(tool)
    # return tool
    tool = await create_model(model_class=Tool, pydantic_schema=new_tool, db=db)
    stmt = select_response(Tool).where(Tool.id == tool.id).options(selectinload(Tool.tool_model))

    return await db.scalar(stmt)


@router.get("/", response_model=list[ToolResponse])
async def get_all_tools(db: AsyncSession = Depends(get_db)):
    stmt = (select_response(Tool)
            .options(selectinload(Tool.tool_model)
                     )
            )

    tools = (await db.scalars(stmt)).all()

    return tools


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool_by_id(tool_id: int, db: AsyncSession = Depends(get_db)):
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
async def patch_tool(tool_id: int, new_patch: ToolUpdate, db: AsyncSession = Depends(get_db)):
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
async def del_tool(tool_id: int, db: AsyncSession = Depends(get_db)):
    """пока не знаю как правильно удалять инструмент.
    В какой локации он должен находиться для списания и можно ли списывать когда инструмент у сотрудника,
    или сначала переместить его на склад, забрать у сотрудника, потом списать"""


    """Переделать полностью. через options подгружаем локацию, проверяем на is_active и чтобы name == склад"""
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





