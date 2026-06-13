import aiohttp

API_URL = "https://api.deepseek.com/v1/chat/completions"

async def synthesize(question: str, flash_responses: list[dict], api_key: str) -> str:
    """Pro #2 объединяет 9 ответов в один"""
    
    # Собираем все ответы Flash в один контекст
    context = ""
    successful = 0
    for resp in flash_responses:
        if "response" in resp:
            context += f"\n[Эксперт {resp['worker_id']}]:\n{resp['response']}\n"
            successful += 1
        else:
            context += f"\n[Эксперт {resp['worker_id']}]: ОШИБКА - {resp['error']}\n"
    
    system_prompt = f"""
Ты — главный синтезатор. Получил 9 экспертных мнений по вопросу пользователя.
Успешно отработали {successful} из 9 экспертов.

Задача:
1. Найди консенсус и противоречия
2. Отбрось слабые аргументы
3. Собери сильные стороны всех экспертов
4. Ответь пользователю максимально полно и структурированно

Используй формат:
## 📌 Краткий ответ
## 🔍 Детальный анализ
## 💡 Рекомендации
## 🎯 Оценка уверенности (1-10)
"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Вопрос: {question}\n\nМнения экспертов:{context}"}
        ],
        "temperature": 0.6,
        "max_tokens": 8000
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            API_URL,
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"}
        ) as resp:
            data = await resp.json()
            return data["choices"][0]["message"]["content"]
