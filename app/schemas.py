"""
Модуль с Pydantic схемами для валидации данных.
Используется для проверки входных/выходных данных API.
"""

from pydantic import BaseModel


class ArticleBase(BaseModel):
    """Базовая схема статьи (общие поля)"""
    url: str  # URL статьи
    title: str  # заголовок
    content: str  # содержимое
    level: int  # уровень вложенности


class ArticleCreate(ArticleBase):
    """Схема для создания статьи (добавляет parent_id)"""
    parent_id: int | None = None  # ID родительской статьи (может быть None)


class Article(ArticleBase):
    """Схема статьи для ответа API (добавляет id и parent_id)"""
    id: int  # ID статьи в БД
    parent_id: int | None  # ID родительской статьи

    class Config:
        # разрешает использовать ORM модели (не только dict)
        from_attributes = True


class SummaryBase(BaseModel):
    """Базовая схема краткого содержания"""
    content: str  # текст summary


class SummaryCreate(SummaryBase):
    """Схема для создания summary (добавляет article_id)"""
    article_id: int  # ID связанной статьи


class Summary(SummaryBase):
    """Схема summary для ответа API (добавляет id и article_id)"""
    id: int  # ID summary в БД
    article_id: int  # ID статьи

    class Config:
        from_attributes = True