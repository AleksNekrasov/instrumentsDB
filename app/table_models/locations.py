from sqlalchemy import String, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database_engine import Base

class Location(Base):
    """Таблица мест где может находиться инструмент"""
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

    tools: Mapped[list["Tool"]] = relationship("Tool",
                                               back_populates="location")
    tool_movements: Mapped[list["ToolMovement"]] = relationship("ToolMovement",
                                                          back_populates="location")