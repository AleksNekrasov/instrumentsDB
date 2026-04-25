from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database_depends import get_db

from app.table_models.table_tool_model import ToolModel
from app.schemas_pydantic.tool_model_pydantic import (ToolModelCreate,
                                                      ToolModelUpdate,
                                                      ToolModelResponse)
from app.helpers import (correct_name,
                         select_response,
                         update_model,
                         create_model,
                         soft_delete_model)

router = APIRouter(prefix='/tool-models', tags=["ToolModels"])


@router.post("/", status_code=201, response_model=ToolModelResponse)
async def post_tool_model(new_model: ToolModelCreate, db: AsyncSession = Depends(get_db)):
    # немного корректируем строки(чтобы начинались с Большой буквы)
    new_model = correct_name(pydantic_model=new_model)

    # поиск уже существующей модели
    stmt = (select_response(model=ToolModel)
            .where(ToolModel.category == new_model.category,
                   ToolModel.model == new_model.model,
                   ToolModel.brand == new_model.brand)
            )
    result = (await db.scalars(stmt)).one_or_none()

    if result is not None:
        raise HTTPException(status_code= 409, detail="This tool model already exists")

    # ✅ создаём нового
    tool_model = await create_model(model_class=ToolModel, pydantic_schema=new_model, db=db)
    return  tool_model

@router.get("/", response_model=list[ToolModelResponse])
async def get_all_tool_models(db: AsyncSession = Depends(get_db)):
    stmt = select_response(ToolModel)
    all_tool_models = (await db.scalars(stmt)).all()
    return all_tool_models

@router.get("/{model_id}", response_model=ToolModelResponse)
async def get_tool_model_by_id(model_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select_response(ToolModel).where(ToolModel.id == model_id)
    tool_model = (await db.scalars(stmt)).one_or_none()
    if tool_model is None:
        raise HTTPException(status_code=404, detail="Tool Model not found")

    return tool_model

@router.patch("/{model_id}", response_model=ToolModelResponse)
async def put_tool_model(model_id: int, new_data: ToolModelUpdate, db: AsyncSession = Depends(get_db)):
    # немного корректируем строки(чтобы начинались с Большой буквы)
    new_data = correct_name(pydantic_model=new_data)
    stmt = select_response(model=ToolModel).where(ToolModel.id == model_id)
    tool_model = (await db.scalars(stmt)).one_or_none()

    if tool_model is None:
        raise HTTPException(status_code=404, detail="Tool Model not found")

    # распаковка в словарь
    data = new_data.model_dump(exclude_unset=True)
    # запись в базу (обновляем наш объект новыми значениями)
    update_model(obj=tool_model, data=data)

    await db.commit()
    await db.refresh(tool_model)
    return tool_model

@router.delete("/{tool_model_id}", response_model=ToolModelResponse)
async def del_tool_model_by_id(tool_model_id: int, db: AsyncSession = Depends(get_db)):
    # ищем нужную модель
    stmt = select_response(model=ToolModel).where(ToolModel.id == tool_model_id)
    tool_model = (await  db.scalars(stmt)).one_or_none()

    if  tool_model is None:
        raise HTTPException(status_code=404, detail="Tool Model not found")

    # мягко удаляем
    await soft_delete_model(tool_model, db=db)
    await db.refresh(tool_model)
    return tool_model





