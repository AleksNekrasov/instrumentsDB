from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from datetime import datetime

class ToolIssueBase(BaseModel):

    tool_id: Annotated[int, Field(..., description="id инструмента")]
    employee_id: Annotated[int, Field(..., description="id работника")]
    issue_date: Annotated[datetime | None, Field(None, description="Дата выдачи")] = None
    return_date: Annotated[datetime | None, Field(None, description="Дата возврата")] = None

class ToolIssueCreate(ToolIssueBase):
    pass

class ToolIssueUpdate(BaseModel):
    tool_id: Annotated[int | None, Field(None, description="id инструмента")] = None
    employee_id: Annotated[int | None, Field(None, description="id работника")] = None
    issue_date: Annotated[datetime | None, Field(None, description="Дата выдачи")] = None
    return_date: Annotated[datetime | None, Field(None, description="Дата возврата")] = None

class ToolIssueResponse(ToolIssueBase):
    """Ответ API"""

    id: int
    model_config = ConfigDict(from_attributes=True)
