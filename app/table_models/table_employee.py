from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database_engine import Base


class Employee(Base):
    """Таблица сотрудников"""
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    position: Mapped[str] = mapped_column(String(30), nullable=False)  # должность
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # tools: Mapped[list["Tool"]] = relationship("Tool",
    #                                            back_populates="employee")
    tool_movements: Mapped[list["ToolMovement"]] = relationship("ToolMovement",
                                                                back_populates="employee")

    tool_issues: Mapped[list["ToolIssue"]] = relationship("ToolIssue", back_populates="employee")
