from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated

from  app.schemas_pydantic.tool_model_pydantic import ToolModelResponse

class EmployeeBase(BaseModel):
    name: Annotated[str, Field(..., min_length=3, max_length=30,
                               description="ФИО сотрудника(3-30 символов)")]
    position: Annotated[str, Field(..., min_length=3, max_length=30,
                                   description="Должность (3-30 символов)")]


class EmployeeCreate(EmployeeBase):
    """Используется при создании сотрудника"""
    pass


class EmployeeUpdate(BaseModel):
    # нужно ли давать менять имя при обновлении сотрудника?
    # но пусть пока будет
    """Обновление данных о сотруднике"""
    name: Annotated[str | None, Field(min_length=3, max_length=30,
                                      description="ФИО сотрудника(3-30 символов)")] = None
    position: Annotated[str | None, Field(min_length=3, max_length=30,
                                          description="Должность (3-30 символов)")] = None


class EmployeeResponse(EmployeeBase):
    """Ответ API"""

    id: int
    tools: list[ToolModelResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class EmployeeDelete(BaseModel):
    """Ответ API после мягкого удаления сотрудника"""
    id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

