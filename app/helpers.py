from typing import Any, Type

from sqlalchemy import Select, select, update, and_
from sqlalchemy.orm import selectinload, with_loader_criteria, DeclarativeBase

from app.table_models.table_employee import Employee
from app.table_models.table_tool import Tool
from app.table_models.table_tool_model import ToolModel
from app.table_models.table_tool_issue import ToolIssue
from app.table_models.table_location import Location


from app.enum_file import StatusEnum

def update_model(obj, data: dict):
    """Функция обновления объекта новыми значениями"""
    for key, value in data.items():
        if hasattr(obj, key):           # если у объекта есть атрибут с именем key (если есть ключ - key)
            setattr(obj, key, value)    # то этому ключу key в объекте obj присваивается значение value

async def soft_delete(obj, db):
    """Мягкое удаление объекта"""
    obj.is_active = False
    await db.commit()


def correct_name(name: str) -> str:
    """Возвращает строку в которой первая буква заглавная остальные строчные"""
    return name.capitalize()

def select_response(model: Type[DeclarativeBase], is_active: bool = True) -> Select:
    """Выборка - select запрос модели. (активных или мягко удаленных)
    по дефолту is_active = True, но можно передать в функцию False"""
    stmt = select(model).where(model.is_active.is_(is_active))
    return stmt



def populate_employee_tools(employee: Employee) -> Employee:
    """Заполняет атрибут tools сотрудника списком моделей инструментов из активных выдач"""
    employee.tools = [
        issue.tool.tool_model
        for issue in employee.tool_issues
        if issue.tool and issue.tool.tool_model
    ]
    return employee


def select_true_employee(is_active: bool = True) -> Select[tuple[Any]]:
    """Возвращаем результат select-запроса работающих сотрудников
    может принимать переменную is_active по умолчанию == True
    для сортировки работающих или неработающих(удаленных) сотрудников: is_active == False"""

    stmt = (
        select(Employee)
        .where(Employee.is_active.is_(is_active))
        .options(
            selectinload(Employee.tool_issues)
            .selectinload(ToolIssue.tool)
            .selectinload(Tool.tool_model)
            , with_loader_criteria(ToolIssue,
                                   ToolIssue.return_date.is_(None),
                                   include_aliases=True)
            , with_loader_criteria(Tool,
                                   and_(
                                       Tool.status == StatusEnum.ACTIVE,
                                       Tool.is_active.is_(True)
                                   ),
                                   include_aliases=True)
            , with_loader_criteria(ToolModel,
                                   ToolModel.is_active.is_(True),
                                   include_aliases=True)
        )
    )
    return stmt


def select_location_with_list_tools(location_id: int, is_active: bool = True) -> Select:
    """select - запрос на выборку всего инструмента(даже удаленного в этой локации)"""
    stmt = (select(Location)
            .where(Location.is_active.is_(is_active))
            .where(Location.id == location_id)
            .options(selectinload(Location.tools))
    )
    return stmt

