from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///instruments.db"
engine = create_engine(url=DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)


#---------Асинхронное подключение к PostgreSQL----------------------
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

# Строка подключения для PostgresSQL
DATABASE_URL = settings.database_url

# Создаем Асинхронный движок
async_engine = create_async_engine(url=DATABASE_URL, echo=True)

# Настраиваем фабрику сеансов(сессий)
async_session_maker = async_sessionmaker(bind=async_engine,expire_on_commit=False, class_=AsyncSession)

# Создаем базовый класс
class Base(DeclarativeBase):
    pass

