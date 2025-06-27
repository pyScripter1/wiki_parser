"""
Модуль с моделями SQLAlchemy для базы данных.
Определяет структуру таблиц и отношения между ними.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Базовый класс для всех моделей SQLAlchemy
Base = declarative_base()


class Article(Base):
    """
    Модель статьи из Википедии.
    Содержит основные поля статьи и связи с другими статьями.
    """
    __tablename__ = "articles"  # имя таблицы в БД

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)  # URL статьи (уникальный)
    title = Column(String)  # заголовок статьи
    content = Column(Text)  # полный текст статьи
    parent_id = Column(Integer, ForeignKey("articles.id"))  # ссылка на родительскую статью
    level = Column(Integer)  # уровень вложенности (0 для корневой статьи)

    # Связь один-ко-многим: статья может иметь много дочерних статей
    children = relationship("Article", back_populates="parent")

    # Связь многие-к-одному: статья может иметь одну родительскую статью
    parent = relationship("Article", remote_side=[id], back_populates="children")

    # Связь один-к-одному: у статьи может быть одно краткое содержание
    summaries = relationship("Summary", back_populates="article", uselist=False)


class Summary(Base):
    """
    Модель краткого содержания (summary) статьи.
    Содержит сгенерированное нейросетью краткое описание.
    """
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)  # текст summary
    article_id = Column(Integer, ForeignKey("articles.id"))  # ссылка на статью

    # Связь многие-к-одному: summary принадлежит одной статье
    article = relationship("Article", back_populates="summaries")