from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database_engine import Base

class ToolModel(Base):
    """Таблица моделей инструмента"""
    __tablename__ = "tool_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    brand: Mapped[str] = mapped_column(String(20), nullable=False)
    model: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tools: Mapped[list["Tool"]] =  relationship("Tool",
                                          back_populates="tool_model",
                                                     )