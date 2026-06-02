from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from datetime import datetime
from decimal import Decimal

class RepairBase(BaseModel):
    tool_id: Annotated[int, Field(..., description="id инструмента")]
    repair_date: Annotated[datetime |None, Field(None, description="дата ремонта")]
    description: Annotated[str, Field(...,max_length=200, description="Описание ремонта")]
    cost: Annotated[Decimal | None, Field(description="Цена ремонта")] = None

class RepairCreate(RepairBase):
    pass

class RepairUpdate(BaseModel):
    tool_id: Annotated[int | None, Field(None, description="id инструмента")] = None
    repair_date: Annotated[datetime | None, Field(None, description="дата ремонта")] = None
    description: Annotated[str | None, Field(None, max_length=200, description="Описание ремонта")] = None
    cost: Annotated[Decimal | None, Field(None, description="Цена ремонта")] = None

class RepairFilter(BaseModel):
    search: str | None = None
    tool_id: int | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    min_cost: Decimal | None = Field(None, ge=0)
    max_cost: Decimal | None = Field(None, ge=0)
    has_cost: bool | None = None

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class RepairResponse(BaseModel):
    """Ответ API"""
    id: int
    tool_id: int
    repair_date: datetime | None
    description: str
    cost: Decimal | None

    model_config = ConfigDict(from_attributes=True)

class ListRepairResponse(BaseModel):
    items: list[RepairResponse]
    total: int
    page: int
    page_size: int


