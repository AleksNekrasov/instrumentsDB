from sqlalchemy import String, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database_engine import Base


class Location(Base):
    """Таблица мест где может находиться инструмент"""
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    # инструменты находящиеся в этой локации
    tools: Mapped[list["Tool"]] = relationship("Tool",
                                               back_populates="location")

    # перемещения ИЗ этой локации
    movements_from: Mapped[list["ToolMovement"]] = relationship("ToolMovement",
                                                                 back_populates="from_location",
                                                                 foreign_keys="[ToolMovement.from_location_id]")
    # перемещения В эту локацию
    movements_to: Mapped[list["ToolMovement"]] = relationship("ToolMovement",
                                                              back_populates="to_location",
                                                              foreign_keys="[ToolMovement.to_location_id]")
