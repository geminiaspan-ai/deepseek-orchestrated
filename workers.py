import aiohttp

API_URL = "https://api.deepseek.com/v1/chat/completions"

async def ask_flash(key: str, prompt: str, worker_id: int) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens": 4000
            }, headers={"Authorization": f"Bearer {key}"}, timeout=60) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {"worker_id": worker_id, "response": data["choices"][0]["message"]["content"]}
                return {"worker_id": worker_id, "error": f"HTTP {resp.status}"}
    except Exception as e:
        return {"worker_id": worker_id, "error": str(e)}

async def run_all_flashes(api_keys: list[str], prompts: list[str]) -> list[dict]:
    import asyncio
    tasks = [ask_flash(key, prompt, i+1) for i, (key, prompt) in enumerate(zip(api_keys, prompts))]
    return await asyncio.gather(*tasks)
