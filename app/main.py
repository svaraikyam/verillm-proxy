from fastapi import FastAPI
from app.proxy import router as proxy_router
from app.replay import router as replay_router
from app.db import init_db

app = FastAPI(title="VeriLLM Proxy")

init_db()

app.include_router(proxy_router)
app.include_router(replay_router)
