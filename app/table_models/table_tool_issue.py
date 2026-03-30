from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime

from app.database_engine import Base

class ToolIssue(Base):
    """Таблица выдачи инструмента"""
    __tablename__ = "tool_issues"

    # добавляем индекс в таблицу
    __table_args__ = (
        Index("ix_tool_issues_tool_return", "tool_id", "return_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tool_id: Mapped[int] = mapped_column(Integer, ForeignKey("tools.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    issue_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    return_date: Mapped[datetime | None] = mapped_column(DateTime, default=None)

    tool: Mapped["Tool"] = relationship(back_populates="tool_issues")
    employee: Mapped["Employee"] = relationship(back_populates="tool_issues")
