from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass

from datetime import datetime, UTC

from sqlalchemy import String, Boolean, DateTime, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database_engine import Base

from app.enum_file import UserRole

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False,unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(UTC))

