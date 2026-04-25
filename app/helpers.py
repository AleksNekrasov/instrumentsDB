from typing import Any, Type
from pydantic import BaseModel

from sqlalchemy import Select, select, update, and_
from sqlalchemy.orm import selectinload, with_loader_criteria, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession

from app.table_models.table_employee import Employee
from app.table_models.table_tool import Tool
from app.table_models.table_tool_model import ToolModel
from app.table_models.table_tool_issue import ToolIssue
from app.table_models.table_location import Location


from app.enum_file import StatusEnum

async def create_model(model_class: Type[DeclarativeBase], pydantic_schema: BaseModel, db: AsyncSession):
    obj = model_class(**pydantic_schema.model_dump(exclude_unset=True))
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

def update_model(obj, data: dict):
    """Функция обновления объекта новыми значениями"""
    for key, value in data.items():
        if value is not None and hasattr(obj, key):           # если у объекта есть атрибут с именем key (если есть ключ - key)
            setattr(obj, key, value)    # то этому ключу key в объекте obj присваивается значение value

async def soft_delete_model(obj, db):
    """Мягкое удаление объекта"""
    obj.is_active = False
    await db.commit()


def correct_name(pydantic_model: BaseModel) -> BaseModel:
    """Возвращает объект pydantic полями в которых первая буква заглавная остальные строчные"""
    data = pydantic_model.model_dump()

    for key, value in data.items():
        if isinstance(value, str): # если значение является строкой:
            data[key] = value.strip().capitalize()

    return pydantic_model.__class__(**data)

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

