from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import os
from orchestrator import plan_query
from workers import run_all_flashes
from synthesizer import synthesize

app = FastAPI(title="DeepSeek Orchestrator 1 Pro + 8 Flash")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

FLASH_KEYS = [os.getenv(f"FLASH_KEY_{i}") for i in range(1, 9)]
PRO_KEY = os.getenv("PRO_KEY")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    time_ms: int
    workers_ok: int

@app.get("/")
async def root(response: Response):
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return {"status": "online", "message": "1 Pro + 8 Flash работает", "workers": 8}

@app.post("/ask", response_model=QueryResponse)
async def ask(req: QueryRequest):
    start = time.time()
    prompts = await plan_query(req.question, PRO_KEY)
    flash_responses = await run_all_flashes(FLASH_KEYS, prompts)
    answer = await synthesize(req.question, flash_responses, PRO_KEY)
    ok = sum(1 for r in flash_responses if "response" in r)
    return QueryResponse(answer=answer, time_ms=int((time.time()-start)*1000), workers_ok=ok)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
