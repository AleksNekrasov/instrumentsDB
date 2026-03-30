from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database_depends import get_db
from app.table_models.table_employee import Employee
from app.schemas_pydantic.employee_pydantic import EmployeeCreate, EmployeeResponse

router = APIRouter(prefix='/employees', tags=["Employees"])

@router.post("/", response_model=EmployeeResponse)
async def create_employee(employee_in: EmployeeCreate, db: AsyncSession = Depends(get_db)):
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



