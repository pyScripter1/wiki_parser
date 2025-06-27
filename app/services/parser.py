"""
Модуль для парсинга статей Википедии.
Использует BeautifulSoup для разбора HTML и aiohttp для асинхронных HTTP запросов.
"""

from bs4 import BeautifulSoup
import aiohttp
from urllib.parse import urljoin
from typing import Optional
import re


class WikipediaParser:
    """
    Парсер статей Википедии с рекурсивным обходом связанных статей.
    Поддерживает ограничение по уровню вложенности.
    """

    def __init__(self, base_url: str = "https://ru.wikipedia.org"):
        """Инициализация парсера"""
        self.base_url = base_url  # базовый URL Википедии
        self.visited_urls = set()  # множество посещенных URL (чтобы избежать циклов)

    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Асинхронно загружает HTML страницы по URL.
        Возвращает текст страницы или None при ошибке.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    async def parse_article(self, url: str, level: int = 0, max_level: int = 5) -> Optional[dict]:
        """
        Рекурсивно парсит статью и связанные статьи.
        :param url: URL статьи для парсинга
        :param level: текущий уровень вложенности (0 для корневой статьи)
        :param max_level: максимальный уровень вложенности
        :return: словарь с данными статьи и вложенных статей или None
        """
        # Проверяем, не превышен ли максимальный уровень или уже посещали URL
        if level > max_level or url in self.visited_urls:
            return None

        self.visited_urls.add(url)  # отмечаем URL как посещенный
        html = await self.fetch_page(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')  # создаем объект BeautifulSoup

        # Извлекаем заголовок статьи (h1 с id="firstHeading")
        title = soup.find("h1", {"id": "firstHeading"}).text

        # Находим основной контент статьи (div с id="mw-content-text")
        content_div = soup.find("div", {"id": "mw-content-text"})

        # Извлекаем все параграфы и объединяем их текст
        paragraphs = content_div.find_all("p")
        content = "\n".join([p.text for p in paragraphs if p.text.strip()])

        # Удаляем сноски вида [1], [2] и т.д. из текста
        content = re.sub(r'\[\d+\]', '', content)

        # Формируем структуру данных статьи
        article_data = {
            "url": url,
            "title": title,
            "content": content,
            "level": level,
            "children": []  # список для вложенных статей
        }

        # Если не достигли максимального уровня, ищем и парсим связанные статьи
        if level < max_level:
            # Находим все ссылки в основном контенте
            links = content_div.find_all("a", href=True)
            wiki_links = set()  # используем set для уникальных URL

            for link in links:
                href = link["href"]
                # Фильтруем только ссылки на другие статьи Википедии
                if href.startswith("/wiki/") and ":" not in href:  # исключаем служебные страницы
                    full_url = urljoin(self.base_url, href)
                    wiki_links.add(full_url)

            # Парсим первые 3 дочерние статьи (для ограничения нагрузки)
            for child_url in list(wiki_links)[:3]:
                child_article = await self.parse_article(child_url, level + 1, max_level)
                if child_article:
                    article_data["children"].append(child_article)

        return article_data