from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from datetime import datetime

class ToolMovementBase(BaseModel):

    tool_id: Annotated[int, Field(..., description="id инструмента")]
    movement_date: Annotated[datetime | None, Field(None, description="дата перемещения")] = None
    employee_id: Annotated[int, Field(..., description="id сотрудника")]
    from_location_id: Annotated[int | None, Field(None, description="id локации, откуда перемещается инструмент")] = None
    to_location_id: Annotated[int | None, Field(None, description="id локации, куда перемещается инструмент")] = None

class ToolMovementCreate(ToolMovementBase):
    pass

class ToolMovementUpdate(BaseModel):
    tool_id: Annotated[int | None, Field(None, description="id инструмента")] = None
    movement_date: Annotated[datetime | None, Field(None, description="дата перемещения")] = None
    employee_id: Annotated[int | None, Field(None, description="id сотрудника")] = None
    from_location_id: Annotated[int | None, Field(None, description="id локации, откуда перемещается инструмент")] = None
    to_location_id: Annotated[int | None, Field(None, description="id локации, куда перемещается инструмент")] = None

class ToolMovementResponse(ToolMovementBase):
    """Ответ API"""

    id: int
    model_config = ConfigDict(from_attributes=True)
