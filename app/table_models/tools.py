from sqlalchemy import String, Integer, ForeignKey, func, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date

from sqlalchemy import Enum as SQLEnum
from app.enum_file import StatusEnum

from app.database_engine import Base

class Tool(Base):
    """Таблица инструментов"""
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("tool_models.id"), nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(25), default=None)
    purchase_date: Mapped[date| None] = mapped_column(Date, default=None)
    status: Mapped[StatusEnum] = mapped_column(SQLEnum(StatusEnum),
                                               default=StatusEnum.IN_STOCK,
                                               nullable=False,
                                               )
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)