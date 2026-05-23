import jwt
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database_depends import get_async_db
from app.schemas_pydantic.token_pydantic import RefreshTokenRequest, AccessTokenRequest
from app.table_models.table_user_model import UserModel
from app.schemas_pydantic.user_pydantic import UserCreate, UserResponse
from app.core.security import (hash_password,
                               verify_password,
                               create_access_token,
                               create_refresh_token,
                               get_current_admin, get_current_user,
                               )

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
    """
    Аутентифицирует пользователя и возвращает JWT с email, role и id.
    """
    stmt = select(UserModel).where(UserModel.email == form_data.username,
                                   UserModel.is_active.is_(True))
    user: UserModel | None = (await db.scalars(stmt)).one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@router.post("/admin/createuser", status_code=201, response_model=UserResponse)
async def register_user(user: UserCreate,
                        db: AsyncSession = Depends(get_async_db),
                        current_admin: UserModel = Depends(get_current_admin)):
    """регистрация нового пользователя"""
    # проверка email
    stmt = select(UserModel).where(UserModel.email == user.email)
    result = (await db.scalars(stmt)).one_or_none()
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    # создание нового пользователя
    new_user = UserModel(username=user.username,
                         email=user.email,
                         hashed_password=hash_password(user.password),
                         role=user.role)

    # сохранение пользователя
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")

@router.get("/me", response_model=UserResponse)
async def me(current_user: UserModel = Depends(get_current_user)):
    """Эндпоинт проверки токена"""
    return current_user

router.post("/refresh-token")
async def refresh_token(body: RefreshTokenRequest,
                        db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет refresh-токен, принимая старый refresh-токен в теле запроса.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    settings =  get_settings()
    old_refresh_token = body.refresh_token
    # декодируем
    try:
        payload = jwt.decode(old_refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        email: str | None = payload.get('sub')
        token_type: str | None = payload.get('token_type')
        # проверяем
        if email is None or token_type != "refresh":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        # refresh-токен истёк
        raise credentials_exception
    except jwt.PyJWTError:
        # подпись неверна или токен повреждён
        raise credentials_exception

    # проверяем что пользователь есть и он активный
    stmt = select(UserModel).where(UserModel.email == email, UserModel.is_active.is_(True))
    user: UserModel | None = (await db.scalars(stmt)).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found or inactive")

    # генерируем новый рефреш токен
    new_refresh_token = create_refresh_token(
        data={"sub": user.email,"role": user.role.value,"id": user.id}
    )
    return {
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }

@router.post("/access_token")
async def access_token(body: RefreshTokenRequest,
                       db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет access-токен, принимая старый refresh-токен в теле запроса.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    settings = get_settings()
    refresh_token = body.refresh_token
    # декодируем
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        if email is None or token_type != "refresh":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        # refresh-токен истёк
        raise credentials_exception
    except jwt.PyJWTError:
        # подпись неверна или токен повреждён
        raise credentials_exception

    # проверяем что пользователь есть и он активный
    stmt = select(UserModel).where(UserModel.email == email, UserModel.is_active.is_(True))
    user: UserModel | None = (await db.scalars(stmt)).one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found or inactive")
    # генерируем новый access token
    new_access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value, "id": user.id}
    )
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }



