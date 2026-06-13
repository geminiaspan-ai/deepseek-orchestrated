import aiohttp

API_URL = "https://api.deepseek.com/v1/chat/completions"

async def synthesize(question: str, flash_responses: list[dict], api_key: str) -> str:
    context = ""
    successful = 0
    for r in flash_responses:
        if "response" in r:
            context += f"\n[Эксперт {r['worker_id']}]:\n{r['response']}\n"
            successful += 1
        else:
            context += f"\n[Эксперт {r['worker_id']}]: ОШИБКА\n"
    
    system_prompt = f"""
Ты — синтезатор. Объедини {successful} экспертных мнений.
Формат ответа:
## Краткий ответ
## Детальный анализ
## Рекомендации
## Уверенность (1-10)
"""
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json={
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Вопрос: {question}\n\nМнения экспертов:{context}"}
            ],
            "temperature": 0.6,
            "max_tokens": 8000
        }, headers={"Authorization": f"Bearer {api_key}"}) as resp:
            data = await resp.json()
            return data["choices"][0]["message"]["content"]
