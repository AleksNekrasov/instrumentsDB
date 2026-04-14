from typing import Any

from sqlalchemy import Select, select, update, and_
from sqlalchemy.orm import selectinload, with_loader_criteria

from app.table_models.table_employee import Employee
from app.table_models.table_tool import Tool
from app.table_models.table_tool_model import ToolModel
from app.table_models.table_tool_issue import ToolIssue

from app.enum_file import StatusEnum


def build_employee_tools(employee: Employee) -> Employee:
    """Возвращает сотрудника уже со списком инструментов"""
    employee.tools = [
        issue.tool.tool_model
        for issue in employee.tool_issues
        if issue.tool and issue.tool.tool_model
    ]
    return employee

def select_true_employee() -> Select[tuple[Any]]:
    """Возвращаем результат select-запроса работающих сотрудников"""
    stmt = (
        select(Employee)
        .where(Employee.is_active.is_(True))
        .options(
            selectinload(Employee.tool_issues)
            .selectinload(ToolIssue.tool)
            .selectinload(Tool.tool_model)
            , with_loader_criteria("ToolIssue",
                                   ToolIssue.return_date.is_(None),
                                   include_aliases=True)
            , with_loader_criteria("Tool",
                                   and_(
                                       Tool.status == StatusEnum.ACTIVE,
                                       Tool.is_active.is_(True)
                                   ),
                                   include_aliases=True)
            , with_loader_criteria("ToolModel",
                                   ToolModel.is_active.is_(True),
                                   include_aliases=True)
        )
    )
    return stmt