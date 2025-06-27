"""
Модуль для работы с базой данных PostgreSQL.
Содержит настройки подключения и инициализации БД.
Использует asyncpg для асинхронного доступа к PostgreSQL.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Base  # импорт моделей SQLAlchemy
import os

# URL подключения к БД
DATABASE_URL = os.getenv("DB_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/wiki_parser")

# Создание асинхронного движка SQLAlchemy
# echo=True включает логирование SQL запросов (полезно для отладки)
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание фабрики сессий для работы с БД
# expire_on_commit=False - отключает expire объектов после коммита
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession  # используем асинхронные сессии
)

async def init_db():
    """
    Инициализация базы данных - создание всех таблиц.
    Вызывается при старте приложения.
    """
    async with engine.begin() as conn:
        # Создаем все таблицы, определенные в моделях Base
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully")