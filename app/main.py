"""
Основной модуль FastAPI приложения.
Содержит эндпоинты API и настройки приложения.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from .database import async_session, init_db
from .services.parser import WikipediaParser
from .services.llm import MistralAI
from .services.database import DatabaseService
from .schemas import Article, Summary
import asyncio

# Создание экземпляра FastAPI приложения
app = FastAPI(
    title="Wikipedia Parser API",
    description="API для парсинга статей Википедии и генерации summary",
    version="1.0.0"
)

# Настройка CORS (Cross-Origin Resource Sharing)
# Разрешаем запросы со всех доменов (*)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # в продакшене следует указать конкретные домены
    allow_methods=["*"],  # разрешаем все HTTP методы
    allow_headers=["*"],  # разрешаем все заголовки
)


@app.on_event("startup")
async def startup():
    """
    Функция, выполняемая при старте приложения.
    Инициализирует базу данных.
    """
    await init_db()
    print("Application started")


async def get_db() -> AsyncSession:
    """
    Dependency для получения сессии БД.
    Гарантирует закрытие сессии после завершения запроса.
    """
    async with async_session() as session:
        yield session


@app.post("/parse/", response_model=Article)
async def parse_wiki_article(url: str, db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для парсинга статьи Википедии.
    Принимает URL статьи, парсит ее и вложенные статьи (до 5 уровня вложенности),
    сохраняет в БД и генерирует summary для основной статьи.
    """
    db_service = DatabaseService(db)

    # Проверяем, не парсили ли мы уже эту статью
    existing_article = await db_service.get_article_by_url(url)
    if existing_article:
        raise HTTPException(
            status_code=400,
            detail="Article already exists in database"
        )

    # Создаем парсер и парсим статью
    parser = WikipediaParser()
    article_data = await parser.parse_article(url)
    if not article_data:
        raise HTTPException(
            status_code=400,
            detail="Failed to parse article from Wikipedia"
        )

    async def save_article(article: dict, parent_id: int = None) -> Article:
        """
        Вложенная функция для рекурсивного сохранения статей в БД.
        """
        article_create = ArticleCreate(
            url=article["url"],
            title=article["title"],
            content=article["content"],
            level=article["level"]
        )
        # Сохраняем статью в БД
        db_article = await db_service.create_article(article_create, parent_id)

        # Рекурсивно сохраняем дочерние статьи
        for child in article["children"]:
            await save_article(child, db_article.id)

        return db_article

    # Сохраняем основную статью и все вложенные
    main_article = await save_article(article_data)

    # Генерируем summary для основной статьи с помощью Mistral AI
    llm = MistralAI()
    summary_content = await llm.generate_summary(main_article.content)

    if summary_content:
        # Сохраняем summary в БД
        await db_service.create_summary(SummaryCreate(
            content=summary_content,
            article_id=main_article.id
        ))

    return main_article


@app.get("/summary/", response_model=Summary)
async def get_article_summary(url: str, db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для получения summary статьи по ее URL.
    Возвращает ранее сгенерированное summary или ошибку 404.
    """
    db_service = DatabaseService(db)

    # Ищем статью по URL
    article = await db_service.get_article_by_url(url)
    if not article:
        raise HTTPException(
            status_code=404,
            detail="Article not found in database"
        )

    # Ищем summary для статьи
    summary = await db_service.get_summary_for_article(article.id)
    if not summary:
        raise HTTPException(
            status_code=404,
            detail="Summary not found for this article"
        )

    return summary