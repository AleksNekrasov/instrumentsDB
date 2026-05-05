from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.database_depends import get_db
from app.table_models import Tool

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

from app.enum_file import StatusEnum

router = APIRouter(prefix='/tool-issues', tags=["ToolIssues"])

@router.post('/', status_code=201, response_model=ToolIssueResponse)
async def create_tool_issue(new_tool_issue: ToolIssueCreate, db: AsyncSession = Depends(get_db)):
    """ДОДЕЛАТЬ!! СЕЙЧАС ПРИ ВЫДАЧЕ ИНСТРУМЕНТА ПО ФАКТУ ИНСТРУМЕНТ ОСТАЕТСЯ В ПЕРЖНЕЙ ЛОКАЦИИ"""
    # Проверка  tool_id существует ли инструмент
    tool_stmt = (select_response(Tool)
                 .where(Tool.id == new_tool_issue.tool_id)
                 .options(selectinload(Tool.location))
                 )
    tool: Tool| None = (await db.scalar(tool_stmt))
    if tool is None:
        raise HTTPException(status_code=404, detail="tool not found or inactive")

    # Проверка выдан ли инструмент
    # ищем инструмент по id у которого в графе возврата стоит None
    stmt_issue = (
        select(ToolIssue)
        .where(
            ToolIssue.tool_id == new_tool_issue.tool_id,
            ToolIssue.return_date.is_(None)
        )
    )
    tool_issue: ToolIssue | None = (await db.scalars(stmt_issue)).one_or_none()
    if tool_issue is not None: # если такой инструмент найден
        raise HTTPException(status_code=400, detail="Инструмент уже выдан и не возвращён")

    # проверка статуса инструмента
    if tool.status !=StatusEnum.ACTIVE:
        raise HTTPException(status_code=400, detail="Инструмент в неисправном состоянии")


    # проверка локации, где находится инструмент
    if tool.location is None:
        raise HTTPException(400, "У инструмента нет локации")

    #if tool.location_id != 1: # id = 1 это локация-склад
    if tool.location.name != "Склад":
        raise HTTPException(status_code=400, detail="Инструмент должен находиться на складе")

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
    #tool_issue = await create_model(ToolIssue, new_tool_issue, db)
    tool.location_id = 4
    tool_issue = ToolIssue(**new_tool_issue.model_dump())

    db.add(tool)
    db.add(tool_issue)

    try:
        await db.commit()
    except:
        await db.rollback()
        raise

    await db.refresh(tool_issue)

    return tool_issue
