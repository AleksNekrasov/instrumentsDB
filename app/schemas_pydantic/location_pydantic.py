from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from app.schemas_pydantic.tool_pydantic import ToolShortResponse

class LocationBase(BaseModel):
    name: Annotated[str, Field(..., min_length=3, max_length=20,
                               description="Локация нахождения инструмента(3-20 символов)")]

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    name: Annotated[str | None, Field( min_length=3, max_length=20,
                               description="Локация нахождения инструмента(3-20 символов)")] = None

class LocationResponse(LocationBase):
    """Ответ API"""

    id: int

    model_config = ConfigDict(from_attributes=True)

class LocationWithToolsResponse(LocationBase):
    """Ответ API"""
    id: int
    tools: list[ToolShortResponse]

    model_config = ConfigDict(from_attributes=True)


class LocationDelete(BaseModel):
    """Ответ API"""
    id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)