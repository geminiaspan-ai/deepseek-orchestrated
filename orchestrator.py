import aiohttp
import os

API_URL = "https://api.deepseek.com/v1/chat/completions"

async def plan_query(question: str, api_key: str) -> list[str]:
    system_prompt = """
Ты — архитектор ИИ. Разбей вопрос на 8 подзадач для 8 экспертов.
Роли экспертов:
1. Фактчекер — проверяет данные
2. Аналитик — ищет причины и следствия
3. Креативщик — генерирует идеи
4. Критик — ищет слабые места
5. Стратег — предлагает долгосрочные решения
6. Реалист — оценивает выполнимость
7. Исследователь — ищет скрытые паттерны
8. Прагматик — предлагает конкретные шаги

Ответь ТОЛЬКО списком из 8 промптов, каждый с новой строки.
"""
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload, headers={"Authorization": f"Bearer {api_key}"}) as resp:
            data = await resp.json()
            response = data["choices"][0]["message"]["content"]
            return [p.strip() for p in response.split("\n") if p.strip()][:8]
