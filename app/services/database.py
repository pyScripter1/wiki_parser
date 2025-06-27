"""
Модуль с CRUD операциями для работы с базой данных.
Содержит методы для создания и чтения статей и summary.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Article, Summary
from ..schemas import ArticleCreate, SummaryCreate


class DatabaseService:
    """
    Сервис для работы с базой данных.
    Инкапсулирует все операции с БД.
    """

    def __init__(self, session: AsyncSession):
        """Инициализация с сессией SQLAlchemy"""
        self.session = session

    async def get_article_by_url(self, url: str) -> Article | None:
        """
        Находит статью по URL.
        :param url: URL статьи
        :return: объект Article или None если не найдено
        """
        result = await self.session.execute(select(Article).where(Article.url == url))
        return result.scalars().first()  # возвращаем первый результат или None

    async def create_article(self, article_data: ArticleCreate, parent_id: int = None) -> Article:
        """
        Создает новую статью в БД.
        :param article_data: данные статьи из схемы ArticleCreate
        :param parent_id: ID родительской статьи (опционально)
        :return: созданный объект Article
        """
        article = Article(
            url=article_data.url,
            title=article_data.title,
            content=article_data.content,
            level=article_data.level,
            parent_id=parent_id
        )
        self.session.add(article)  # добавляем статью в сессию
        await self.session.commit()  # сохраняем изменения
        await self.session.refresh(article)  # обновляем объект из БД
        return article

    async def create_summary(self, summary_data: SummaryCreate) -> Summary:
        """
        Создает summary для статьи.
        :param summary_data: данные summary из схемы SummaryCreate
        :return: созданный объект Summary
        """
        summary = Summary(
            content=summary_data.content,
            article_id=summary_data.article_id
        )
        self.session.add(summary)
        await self.session.commit()
        await self.session.refresh(summary)
        return summary

    async def get_summary_for_article(self, article_id: int) -> Summary | None:
        """
        Находит summary по ID статьи.
        :param article_id: ID статьи
        :return: объект Summary или None если не найдено
        """
        result = await self.session.execute(select(Summary).where(Summary.article_id == article_id))
        return result.scalars().first()