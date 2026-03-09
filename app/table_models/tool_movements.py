from sqlalchemy import String, Integer, ForeignKey, func, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from app.database_engine import Base

class ToolMovement(Base):
    """Таблица перемещений инструмента"""
    __tablename__ = "tool_movements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tool_id: Mapped[int] = mapped_column(Integer,  ForeignKey("tools.id"), nullable=False)
    from_locations: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    to_locations: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    movement_date: Mapped[date] = mapped_column(Date, nullable=False, default=func.now)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)