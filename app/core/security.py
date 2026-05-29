from jwt import ExpiredSignatureError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.enum_file import UserRole
from app.table_models.table_user import User
from app.config import get_settings
from app.database_depends import get_async_db


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")




def hash_password(password: str) -> str:
    """Функция хеширования"""
    return password_context.hash(secret=password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Функция проверки пароля"""
    return password_context.verify(secret=plain_password, hash=hashed_password)

def create_access_token(data: dict):
    """
    Создаёт JWT с payload (sub, role, id, exp).
    """
    to_encode = data.copy()
    settings = get_settings()

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update(
        {
            "exp": expire,
            "token_type": "access",
        }
    )
    return jwt.encode(payload=to_encode, key=settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data: dict):
    """
    Создаёт refresh-токен с длительным сроком действия и token_type="refresh".
    """
    to_encode = data.copy()
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update(
        {
            "exp": expire,
            "token_type": "refresh"
        }
    )
    return jwt.encode(payload=to_encode, key=settings.secret_key, algorithm=settings.algorithm)

# user
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)):
    """
    Проверяет JWT и возвращает пользователя из базы.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    settings = get_settings()
    # расшифровка
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        if email is None or token_type != "access":
            raise credentials_exception
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception

    stmt = select(User).where(User.email == email, User.is_active.is_(True))
    user = (await db.scalars(stmt)).one_or_none()
    if user is None:
        raise credentials_exception

    return user

# admin
async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    return current_user

#manager
async def get_current_manager(current_user: User = Depends(get_current_user)):
    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    return current_user

# storekeeper
async def get_current_storekeeper(current_user: User = Depends(get_current_user)):
    if current_user.role not in (UserRole.STOREKEEPER, UserRole.ADMIN):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    return current_user

#operator
async def get_current_operator(current_user: User = Depends(get_current_user)):
    if current_user.role not in (UserRole.OPERATOR, UserRole.ADMIN):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    return current_user
