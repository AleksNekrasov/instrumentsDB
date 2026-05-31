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

class LocationFilters(BaseModel):
    search: str | None = None
    is_active: bool | None = None
    has_tools: bool | None = None

    page: int = Field(1,ge=1)
    page_size: int = Field(20, ge=1, le=100)

class LocationResponse(BaseModel):
    """Ответ API"""
    id: int
    name: str
    is_active: bool
    tools_count: int

    model_config = ConfigDict(from_attributes=True)

class ListLocationResponse(BaseModel):
    items: list[LocationResponse]
    total: int
    page: int
    page_size: int


