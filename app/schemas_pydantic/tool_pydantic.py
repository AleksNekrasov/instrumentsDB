from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from datetime import date

from app.enum_file import StatusEnum


class ToolBase(BaseModel):
    model_id: Annotated[int, Field(..., description="id модели инструмента")]
    serial_number: Annotated[str | None, Field(None, min_length=3, max_length=25,
                                               description="Серийный номер")] = None
    purchase_date: Annotated[date | None, Field(None, description="Дата покупки")] = None
    status: Annotated[StatusEnum, Field(..., description="статус инструмента")] = StatusEnum.ACTIVE
    location_id: Annotated[int, Field(..., description="id локации инструмента")]
    employee_id: Annotated[int | None, Field(None, description="id сотрудника")] = None

class ToolCreate(ToolBase):
    pass

class ToolUpdate(BaseModel):
    model_id: Annotated[int | None, Field(None, description="id модели инструмента")] = None
    serial_number: Annotated[str | None, Field(None, min_length=3, max_length=25,
                                               description="Серийный номер")] = None
    purchase_date: Annotated[date | None, Field(None, description="Дата покупки")] = None
    status: Annotated[StatusEnum | None, Field(None, description="статус инструмента")] = None
    location_id: Annotated[int | None, Field(None, description="id локации инструмента")] = None
    employee_id: Annotated[int | None, Field(None, description="id сотрудника")] = None

class ToolResponse(ToolBase):
    """ Ответ API"""
    id: int

    model_config = ConfigDict(from_attributes=True)

class ToolShortResponse(BaseModel):
    id: int
    serial_number: str
    status: StatusEnum

    model_config = ConfigDict(from_attributes=True)

