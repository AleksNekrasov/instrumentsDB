from sqlalchemy import String, Integer, ForeignKey, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database_engine import Base


class ToolMovement(Base):
    """Таблица перемещений инструмента"""
    __tablename__ = "tool_movements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tool_id: Mapped[int] = mapped_column(Integer, ForeignKey("tools.id"), nullable=False)
    movement_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)

    from_location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("locations.id"))
    to_location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("locations.id"))

    from_location: Mapped["Location"] = relationship(
        "Location",
        foreign_keys=[from_location_id],
        back_populates="movements_from"
    )
    to_location: Mapped["Location"] = relationship(
        "Location",
        foreign_keys=[to_location_id],
        back_populates="movements_to"
    )

    tool: Mapped["Tool"] = relationship("Tool",
                                        back_populates="tool_movements")
    employee: Mapped["Employee"] = relationship("Employee",
                                                back_populates="tool_movements")


