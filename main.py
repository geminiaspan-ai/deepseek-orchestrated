from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import os
import asyncio
from orchestrator import plan_query
from workers import run_all_flashes
from synthesizer import synthesize

app = FastAPI(title="DeepSeek Orchestrator 1 Pro + 9 Flash")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Получаем 9 ключей из переменных окружения
FLASH_KEYS = [
    os.getenv("FLASH_KEY_1"),
    os.getenv("FLASH_KEY_2"),
    os.getenv("FLASH_KEY_3"),
    os.getenv("FLASH_KEY_4"),
    os.getenv("FLASH_KEY_5"),
    os.getenv("FLASH_KEY_6"),
    os.getenv("FLASH_KEY_7"),
    os.getenv("FLASH_KEY_8"),
    os.getenv("FLASH_KEY_9"),
]

PRO_KEY = os.getenv("PRO_KEY", FLASH_KEYS[0])  # Pro использует первый ключ

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    time_ms: int
    workers_successful: int

@app.get("/")
async def root(response: Response):
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return {
        "status": "online",
        "message": "DeepSeek Orchestrator 1 Pro + 9 Flash работает!",
        "workers": len([k for k in FLASH_KEYS if k]),
        "endpoints": {
            "GET /": "Информация о сервере",
            "POST /ask": "Отправить вопрос"
        }
    }

@app.post("/ask", response_model=QueryResponse)
async def ask_question(req: QueryRequest):
    start = time.time()
    
    # Шаг 1: Pro планирует
    prompts = await plan_query(req.question, PRO_KEY)
    
    # Шаг 2: 9 Flash параллельно
    flash_responses = await run_all_flashes(FLASH_KEYS, prompts)
    
    # Шаг 3: Pro синтезирует
    final_answer = await synthesize(req.question, flash_responses, PRO_KEY)
    
    # Считаем успешных воркеров
    successful = sum(1 for r in flash_responses if "response" in r)
    
    elapsed_ms = int((time.time() - start) * 1000)
    
    return QueryResponse(
        answer=final_answer,
        time_ms=elapsed_ms,
        workers_successful=successful
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
