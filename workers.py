import aiohttp
import asyncio

API_URL = "https://api.deepseek.com/v1/chat/completions"

async def ask_flash(key: str, prompt: str, worker_id: int) -> dict:
    """Один Flash работает над своей подзадачей"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 4000
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                API_URL,
                json=payload,
                headers={"Authorization": f"Bearer {key}"},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "worker_id": worker_id,
                        "response": data["choices"][0]["message"]["content"],
                        "tokens": data["usage"]["total_tokens"]
                    }
                else:
                    error_text = await resp.text()
                    return {"worker_id": worker_id, "error": f"HTTP {resp.status}: {error_text}"}
    except Exception as e:
        return {"worker_id": worker_id, "error": str(e)}

async def run_all_flashes(api_keys: list[str], prompts: list[str]) -> list[dict]:
    """Запускает 9 Flash параллельно"""
    
    tasks = []
    for i, (key, prompt) in enumerate(zip(api_keys, prompts)):
        tasks.append(ask_flash(key, prompt, i+1))
    
    results = await asyncio.gather(*tasks)
    return results
