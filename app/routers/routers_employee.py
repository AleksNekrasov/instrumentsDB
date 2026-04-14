from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from sqlalchemy.orm import selectinload, with_loader_criteria

from app.database_depends import get_db
from app.table_models.table_tool_issue import ToolIssue
from app.table_models.table_employee import Employee
from app.table_models.table_tool import Tool
from app.table_models.table_tool_model import ToolModel
from app.schemas_pydantic.employee_pydantic import EmployeeCreate, EmployeeResponse, EmployeeUpdate

from app.enum_file import StatusEnum
from app.helpers import build_employee_tools, select_true_employee

router = APIRouter(prefix='/employees', tags=["Employees"])

@router.post("/",status_code=201, response_model=EmployeeResponse)
async def create_employee(employee_in: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    """Создание нового сотрудника"""
    # 🔍 ищем сотрудника
    stmt = select(Employee).where(
        Employee.name == employee_in.name,
        Employee.position == employee_in.position
    )
    result = await db.execute(stmt)
    existing_employee = result.scalar_one_or_none()

    # ❌ если уже есть активный
    if existing_employee and existing_employee.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="сотрудник уже существует и он работает"
                            )

    # ♻️ если есть, но неактивный — восстанавливаем
    if existing_employee and existing_employee.is_active == False:
        existing_employee.is_active = True
        await db.commit()
        await db.refresh(existing_employee)
        return existing_employee

    # ✅ создаём нового
    employee = Employee(**employee_in.model_dump())
    db.add(employee)
    await db.commit()
    await db.refresh(employee)

    return employee

@router.get("/", status_code=200, response_model=list[EmployeeResponse])
async def get_all_employees(db: AsyncSession = Depends(get_db)):
    """Получение списка всех активных сотрудников и их инструмента"""
    stmt = select_true_employee()
    result = (await db.scalars(stmt)).all()

    # создаем список сотрудников с инструментами.
    # в функцию отправляем сотрудника, функция возвращает сотрудника уже со списком инструментов
    # все записываем в новый список list[EmployeeResponse]
    employees = [build_employee_tools(emp) for emp in result]

    return employees

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee_by_id(
        employee_id: int,
        db: AsyncSession = Depends(get_db)
):
    stmt = select_true_employee().where(Employee.id == employee_id)
    result = (await db.scalars(stmt)).one_or_none()

    if result is None:
        raise HTTPException(status_code=404, detail="Employee is not found(Сотрудник не найден)")

    # отправляем в функцию сотрудника, функция возвращает его с инструментом
    employee = build_employee_tools(result)

    return employee

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def put_employee_by_id(employee_id: int,
                             new_data: EmployeeUpdate,
                             db: AsyncSession=Depends(get_db)):
    """ сырая функция обновления сотрудника(Нужно доработать)"""
    emp_stmt = select_true_employee()
    employee = (await db.scalars(emp_stmt)).one_or_none()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found (сотрудник не найден)")

    await db.execute(
        update(Employee)
        .where(Employee.id == employee_id)
        .values(**new_data.model_dump(exclude_unset=True))
    )
    await db.commit()
    employee = build_employee_tools(employee) # тут пока так, для корректного возврата EmployeeResponse
    return employee








# @router.get("/{employee_id}", response_model=EmployeeWithToolsResponse)
# async def get_employee_by_id(
#     employee_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     # 🔍 получаем сотрудника
#     stmt = (
#         select(Employee)
#         .where(
#             Employee.id == employee_id,
#             Employee.is_active.is_(True)
#         )
#         .options(selectinload(Employee.tool_issues).selectinload(ToolIssue.tool))
#     )
#
#     result = await db.execute(stmt)
#     employee = result.scalar_one_or_none()
#
#     if not employee:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Сотрудник не найден"
#         )
#
#     # 🎯 берём только актуальные инструменты
#     current_tools = [
#         issue.tool
#         for issue in employee.tool_issues
#         if issue.return_date is None
#     ]
#
#     # 👇 добавляем динамическое поле
#     employee.tools = current_tools
#
#     return employee


