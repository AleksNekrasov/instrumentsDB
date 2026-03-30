from sqlalchemy import String, Integer, ForeignKey, DateTime, func, DECIMAL
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime
from app.database_engine import Base

class Repair(Base):
    """Таблица ремонтов"""
    __tablename__ = "repairs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tool_id: Mapped[int] = mapped_column(Integer, ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    repair_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    description: Mapped[str] = mapped_column(String(50), nullable=False)
    cost: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True, default=None)

    tool: Mapped["Tool"] = relationship("Tool",
                                        back_populates="repairs")
