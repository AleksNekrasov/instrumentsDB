from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from datetime import date

from app.enum_file import StatusEnum
from app.schemas_pydantic.tool_model_pydantic import ToolModelBase


class ToolBase(BaseModel):
    model_id: Annotated[int, Field(..., description="id модели инструмента")]
    serial_number: Annotated[str | None, Field(None, min_length=3, max_length=25,
                                               description="Серийный номер")] = None
    status: Annotated[StatusEnum, Field(..., description="статус инструмента")] = StatusEnum.ACTIVE
    # purchase_date: Annotated[date | None, Field(None, description="Дата покупки")] = None
    # location_id: Annotated[int, Field(..., description="id локации инструмента")]
    # employee_id: Annotated[int | None, Field(None, description="id сотрудника")] = None


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseModel):
    model_id: Annotated[int | None, Field(None, description="id модели инструмента")] = None
    serial_number: Annotated[str | None, Field(None, min_length=3, max_length=25,
                                               description="Серийный номер")] = None
    purchase_date: Annotated[date | None, Field(None, description="Дата покупки")] = None
    status: Annotated[StatusEnum | None, Field(None, description="статус инструмента")] = None
    location_id: Annotated[int | None, Field(None, description="id локации инструмента")] = None
    # employee_id: Annotated[int | None, Field(None, description="id сотрудника")] = None


class ToolResponse(ToolBase):
    """ Ответ API"""
    id: int
    tool_model: ToolModelBase

    model_config = ConfigDict(from_attributes=True)


class ToolShortResponse(BaseModel):
    id: int
    serial_number: str
    status: StatusEnum

    model_config = ConfigDict(from_attributes=True)


class ToolFilter(BaseModel):
    search: str | None = Field(None, description="Поиск по серийному номеру")
    is_active: bool | None = Field(None, description="Фильтр (списан/не списан) инструмент")
    has_serial: bool | None = Field(None, description="Фильтр по наличию серийного номера(есть/нет)")
    has_repairs: bool | None = Field(None, description="Фильтр ремонтных инструментов(ремонтировался/нет)")
    brand: str | None = Field(None, description="Бренд")
    category: str | None = Field(None, description="Категория инструмента")
    status: StatusEnum | None = Field(None, description="Статус")
    model_id: int | None = Field(None, description="Поиск по модели инструмента")
    location_id: int | None = Field(None, description="Поиск по локации")
    employee_id: int | None = Field(None, description="поиск по сотруднику")
    purchase_date_from: date | None = Field(None, description="По дате с какого числа куплен")
    purchase_date_to: date | None = Field(None, description="По дате по какое число куплено")

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class ListToolResponse(BaseModel):
    items: list[ToolResponse]
    total: int
    page: int
    page_size: int
