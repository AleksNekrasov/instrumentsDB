from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, func
from sqlalchemy.orm import selectinload

from app.database_depends import get_async_db
from app.table_models import Tool
from app.table_models.table_employee import Employee
from app.table_models.table_user import User
from app.table_models.table_tool_issue import ToolIssue
from app.schemas_pydantic.employee_pydantic import (EmployeeCreate,
                                                    EmployeeResponse,
                                                    EmployeeUpdate,
                                                    EmployeeFilter,
                                                    EmployeeDelete,
                                                    ListEmployeeResponse,
                                                    )

from app.core.security import get_current_operator

from app.helpers import (populate_employee_tools,
                         select_true_employee,
                         soft_delete_model,
                         update_model,
                         create_model
                         )

router = APIRouter(prefix='/employees', tags=["Employees"])


@router.post("/", status_code=201, response_model=EmployeeResponse)
async def create_employee(employee_in: EmployeeCreate,
                          _: User = Depends(get_current_operator),
                          db: AsyncSession = Depends(get_async_db)):
    """Создание нового сотрудника"""
    # 🔍 ищем сотрудника
    stmt = select(Employee).where(
        Employee.name == employee_in.name,
        Employee.position == employee_in.position
    )
    result = await db.execute(stmt)
    existing_employee = result.scalar_one_or_none()

    #  если уже есть активный
    if existing_employee and existing_employee.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="сотрудник уже существует и он работает"
                            )

    #  если есть, но неактивный — восстанавливаем
    if existing_employee and existing_employee.is_active == False:
        existing_employee.is_active = True
        await db.commit()
        await db.refresh(existing_employee)
        return existing_employee

    #  создаём нового
    new_employee = await create_model(model_class=Employee, pydantic_schema=employee_in, db=db)
    # employee = Employee(**employee_in.model_dump())
    # db.add(employee)
    # await db.commit()
    # await db.refresh(employee)

    return new_employee


@router.get("/", status_code=200, response_model=ListEmployeeResponse)
async def get_all_employees(filters: EmployeeFilter = Depends(),
                            db: AsyncSession = Depends(get_async_db)):
    """фильтрация сотрудников"""
    stmt = (select(Employee)
            .options(selectinload(Employee.tool_issues)
                     .selectinload(ToolIssue.tool)
                     .selectinload(Tool.tool_model)
                     )
            .order_by(Employee.id)
            )

    # для подсчета общего количества фильтрованных сотрудников
    total_stmt = select(func.count()).select_from(Employee)

    # поиск
    if filters.search:
        search_value = filters.search.strip()  # убираем пробелы
        if search_value:
            stmt = stmt.where(Employee.name.ilike(f"%{search_value}%"))
            total_stmt = total_stmt.where(Employee.name.ilike(f"%{search_value}%"))

    # должность
    if filters.position:
        stmt = stmt.where(Employee.position == filters.position)
        total_stmt = total_stmt.where(Employee.position == filters.position)

    # работает / не работает
    if filters.is_active is not None:
        stmt = stmt.where(Employee.is_active.is_(filters.is_active))
        total_stmt = total_stmt.where(Employee.is_active.is_(filters.is_active))
    # наличие инструмента (есть / нет)
    if filters.has_tools is not None:
        # выборка всех сотрудников с инструментом
        tool_exists = exists().where(ToolIssue.employee_id == Employee.id, ToolIssue.return_date.is_(None))
        #
        if filters.has_tools:
            stmt = stmt.where(tool_exists)
            total_stmt = total_stmt.where(tool_exists)
        else:
            stmt = stmt.where(~tool_exists)
            total_stmt = total_stmt.where(~tool_exists)

    """пагинация"""
    stmt = stmt.offset((filters.page - 1) * filters.page_size).limit(filters.page_size)

    # total
    total = await db.scalar(total_stmt) or 0
    employees = (await db.scalars(stmt)).all()

    if filters.has_tools:
        for employee in employees:
            populate_employee_tools(employee)  # в функции добавляем каждому сотруднику его инструмент

    return {
        "items": employees,
        "total": total,
        "page": filters.page,
        "page_size": filters.page_size
    }


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee_by_id(
        employee_id: int,
        db: AsyncSession = Depends(get_async_db)
):
    stmt = select_true_employee().where(Employee.id == employee_id)
    result = (await db.scalars(stmt)).one_or_none()

    if result is None:
        raise HTTPException(status_code=404, detail="Employee is not found(Сотрудник не найден)")

    # отправляем в функцию сотрудника, функция возвращает его с инструментом
    employee = populate_employee_tools(result)

    return employee


@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def put_employee_by_id(employee_id: int,
                             new_data: EmployeeUpdate,
                             _: User = Depends(get_current_operator),
                             db: AsyncSession = Depends(get_async_db)):
    """ сырая функция обновления сотрудника (Нужно доработать)"""
    emp_stmt = select_true_employee().where(Employee.id == employee_id)
    employee = (await db.scalars(emp_stmt)).unique().one_or_none()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found (сотрудник не найден)")

    # await db.execute(
    #     update(Employee)
    #     .where(Employee.id == employee_id)
    #     .values(**new_data.model_dump(exclude_unset=True))
    # )
    data = new_data.model_dump(exclude_unset=True)  # распаковка объекта в словарь
    update_model(obj=employee, data=data)  # обновление объекта новыми данными

    await db.commit()
    employee = populate_employee_tools(employee)  # тут пока так, для корректного возврата EmployeeResponse
    return employee


@router.delete("/{employee_id}", response_model=EmployeeDelete, status_code=200)
async def del_employee_by_id(employee_id: int,
                             _: User = Depends(get_current_operator),
                             db: AsyncSession = Depends(get_async_db)):
    stmt = select_true_employee().where(Employee.id == employee_id)
    employee = (await db.scalars(stmt)).unique().one_or_none()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee is not found(Сотрудник не найден)")

    # проверка на наличие инструмента
    tool_exist_stmt = select(
        exists().where(ToolIssue.employee_id == employee_id,
                       ToolIssue.return_date.is_(None))
    )
    has_active_tools = await db.scalar(tool_exist_stmt)

    if has_active_tools:
        raise HTTPException(status_code=403, detail="Нельзя удалить сотрудника, пока за ним числится инструмент")

    await soft_delete_model(obj=employee, db=db)
    await db.refresh(employee)
    return employee
