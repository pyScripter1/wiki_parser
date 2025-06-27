"""
Модуль для работы с API Mistral AI.
Генерирует краткие содержания (summary) для текстов статей.
"""

import httpx
import os
from typing import Optional

# API ключ Mistral AI
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "7gLe94Fi7MTy98eKg1pZkTHknigu3TMP")


class MistralAI:
    """
    Класс для взаимодействия с API Mistral AI.
    Реализует генерацию summary для текстов статей.
    """

    def __init__(self):
        """Инициализация клиента Mistral AI"""
        self.api_key = MISTRAL_API_KEY
        self.base_url = "https://api.mistral.ai/v1"  # базовый URL API

    async def generate_summary(self, text: str) -> Optional[str]:
        """
        Генерирует краткое содержание (summary) для заданного текста.
        :param text: исходный текст статьи
        :return: сгенерированное summary или None при ошибке
        """
        # Формируем промпт с инструкцией для нейросети
        prompt = (
            "Создай краткое содержание (summary) следующего текста на русском языке, "
            "выдели основные идеи:\n\n"
            f"{text}"
        )

        try:
            async with httpx.AsyncClient() as client:
                # Отправляем POST запрос к API Mistral
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mistral-tiny",  # используем самую легкую модель
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7  # параметр "творчества" (от 0 до 1)
                    },
                    timeout=30.0  # таймаут запроса в секундах
                )

                if response.status_code == 200:
                    # Извлекаем сгенерированный текст из ответа
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    print(f"Mistral API error: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            print(f"Error calling Mistral AI: {e}")
            return None