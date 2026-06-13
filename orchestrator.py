import aiohttp
import asyncio
import os

API_URL = "https://api.deepseek.com/v1/chat/completions"

async def plan_query(question: str, api_key: str) -> list[str]:
    """Pro #1 разбивает вопрос на 9 подзадач для Flash"""
    
    system_prompt = """
Ты — архитектор ИИ-системы. Разбей вопрос пользователя на 9 РАЗНЫХ подзадач.
Каждая подзадача будет отдана отдельному агенту-эксперту.

Распредели роли:
1. Фактчекер — проверяет данные и цифры
2. Аналитик — ищет причинно-следственные связи
3. Креативщик — генерирует нестандартные идеи
4. Критик — ищет слабые места и риски
5. Стратег — предлагает долгосрочные решения
6. Реалист — оценивает выполнимость
7. Исследователь данных — ищет скрытые паттерны
8. Прагматик — предлагает конкретные шаги
9. Резонёр — оценивает логическую непротиворечивость

Ответь ТОЛЬКО списком из 9 промптов, каждый с новой строки.
Промпты должны быть конкретными и самодостаточными.
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
        async with session.post(
            API_URL,
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"}
        ) as resp:
            data = await resp.json()
            response = data["choices"][0]["message"]["content"]
            prompts = [p.strip() for p in response.split("\n") if p.strip()]
            return prompts[:9]
