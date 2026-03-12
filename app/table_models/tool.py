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
                                               default=StatusEnum.ACTIVE,
                                               nullable=False,
                                               )
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    employee_id: Mapped[int |None] = mapped_column(Integer, ForeignKey("employees.id"), default=None)

    tool_model: Mapped["ToolModel"] = relationship("ToolModel",
                                                   back_populates="tools")
    repairs: Mapped[list["Repair"]] = relationship("Repair",
                                                   back_populates="tool")
    location: Mapped["Location"] = relationship("Location",
                                                back_populates="tools")
    employee: Mapped["Employee"] = relationship("Employee",
                                                back_populates="tools")
    tool_movements: Mapped[list["ToolMovement"]] = relationship("ToolMovement",
                                                                back_populates="tool")

    tool_issues: Mapped[list["ToolIssue"]] = relationship("ToolIssue",back_populates="tool")

