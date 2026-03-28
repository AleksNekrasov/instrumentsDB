from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.database_engine import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронная зависимость для получения сессии базы данных.
    Создаёт новую сессию для каждого запроса и автоматически закрывает её.
    """
    async with async_session_maker() as session:
        yield session
