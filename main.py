from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

app = FastAPI(title="DeepSeek Orchestrator 1 Pro + 8 Flash")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    time_ms: int

@app.get("/")
async def root():
    return {"message": "DeepSeek Orchestrator работает! Отправьте POST запрос на /ask"}

@app.post("/ask", response_model=QueryResponse)
async def ask_question(req: QueryRequest):
    start = time.time()
    
    # Временный ответ (потом заменим на полную логику с 8 Flash)
    answer = f"Ваш вопрос: {req.question}\n\n✅ Оркестратор работает! Позже здесь будет ответ от 1 Pro + 8 Flash."
    
    elapsed_ms = int((time.time() - start) * 1000)
    return QueryResponse(answer=answer, time_ms=elapsed_ms)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
