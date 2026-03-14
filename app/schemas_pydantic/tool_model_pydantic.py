from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated

class ToolModelBase(BaseModel):

    name: Annotated[str, Field(..., max_length=20,
                               description="тип инструмента")]
    brand: Annotated[str, Field(..., max_length=20,
                               description="производитель")]
    model: Annotated[str, Field(..., max_length=20,
                               description="модель производителя")]

class ToolModelCreate(ToolModelBase):
    pass

class ToolModelUpdate(BaseModel):
    name: Annotated[str | None, Field(None, max_length=20,
                               description="тип инструмента")] = None
    brand: Annotated[str | None, Field(None, max_length=20,
                               description="производитель")] = None
    model: Annotated[str | None, Field(None, max_length=20,
                               description="модель производителя")] = None

class ToolModelResponse(ToolModelBase):
    """Ответ API"""

    id: int
    model_config = ConfigDict(from_attributes=True)

