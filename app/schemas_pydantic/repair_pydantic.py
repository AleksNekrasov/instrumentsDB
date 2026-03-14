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

class RepairResponse(RepairBase):
    """Ответ API"""

    id: int
    model_config = ConfigDict(from_attributes=True)

