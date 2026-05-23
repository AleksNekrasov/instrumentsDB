import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.table_models import UserModel
from app.schemas_pydantic.user_pydantic import UserRole
from app.core.security import hash_password  # ← адаптируй путь!

"""Запуск скрипта
python -m app.scripts.create_admin"""


async def create_admin():
    settings = get_settings()

    # 1. Создаём движок (только для этого скрипта!)
    engine = create_async_engine(settings.database_url, echo=True)

    # 2. Создаём фабрику сессий (если её нет в твоём проекте)
    from sqlalchemy.ext.asyncio import async_sessionmaker
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with async_session_maker() as db:
            # 3. Проверяем, существует ли админ
            stmt = select(UserModel).where(UserModel.email == "admin@mail.com")
            result = (await db.scalars(stmt)).one_or_none()

            if result:
                print("⚠️ Админ уже существует!")
                return

            # 4. Создаём админа
            admin = UserModel(
                username="admin",
                email="admin@mail.com",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            )

            db.add(admin)
            await db.commit()  # ← фиксируем транзакцию
            print("✅ Админ создан!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        # Транзакция автоматически откатится при выходе из with при ошибке
    finally:
        # 5. Обязательно закрываем движок
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin())



