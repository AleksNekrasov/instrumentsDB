from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database_depends import get_db

from app.table_models.table_tool_issue import ToolIssue
from app.table_models.table_tool import Tool
from app.table_models.table_employee import Employee
from app.schemas_pydantic.tool_issue_pydantic import (ToolIssueCreate,
                                                      ToolIssueUpdate,
                                                      ToolIssueResponse)
from app.helpers import (correct_name,
                         select_response,
                         update_model,
                         create_model,
                         soft_delete_model)

router = APIRouter(prefix='/tool-issues', tags=["ToolIssues"])

@router.post('/', status_code=201, response_model=ToolIssueResponse)
async def create_tool_issue(new_tool_issue: ToolIssueCreate, db: AsyncSession = Depends(get_db)):
    # Проверка ID tool_id
    tool_stmt = select_response(Tool).where(Tool.id == new_tool_issue.tool_id)
    tool = (await db.scalar(tool_stmt))
    if tool is None:
        raise HTTPException(status_code=404, detail="tool not found or inactive")

    #Проверка employee_id
    employee_stmt = select_response(Employee).where(Employee.id == new_tool_issue.employee_id)
    employee = (await db.scalar(employee_stmt))
    if employee is None:
        raise HTTPException(status_code=404, detail="employee not found or inactive")

    #записываем новую запись выдачи:
    # data = new_tool_issue.model_dump(exclude_unset=True)
    # tool_issue = ToolIssue(**data)
    # db.add(tool_issue)
    # await db.commit()
    # await db.refresh(tool_issue)
    # return tool_issue
    tool_issue = await create_model(ToolIssue, new_tool_issue, db)
    return tool_issue
