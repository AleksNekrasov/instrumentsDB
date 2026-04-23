from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database_depends import get_db

from app.table_models.table_tool_model import ToolModel
from app.schemas_pydantic.tool_model_pydantic import (ToolModelCreate,
                                                      ToolModelUpdate,
                                                      ToolModelResponse)
from app.helpers import (correct_name,
                         select_response,)

router = APIRouter(prefix='/tool-models', tags=["ToolModels"])


@router.post("/", status_code=201, response_model=ToolModelResponse)
async def post_tool_model(new_model: ToolModelCreate, db: AsyncSession = Depends(get_db)):
    # немного корректируем строки(чтобы начинались с Большой буквы)
    new_model.name = correct_name(new_model.name)
    new_model.model = correct_name(new_model.model)
    new_model.brand = correct_name(new_model.brand)

    # поиск уже существующей модели
    stmt = (select_response(model=ToolModel)
            .where(ToolModel.name == new_model.name,
                   ToolModel.model == new_model.model,
                   ToolModel.brand == new_model.brand)
            )
    result = (await db.scalars(stmt)).one_or_none()

    if result is not None:
        raise HTTPException(status_code= 409, detail="This tool model already exists")

    # ✅ создаём нового
    tool_model = ToolModel(**new_model.model_dump())
    db.add(tool_model)
    await db.commit()
    await db.refresh(tool_model)
    return  tool_model


