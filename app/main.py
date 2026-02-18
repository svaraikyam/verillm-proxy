from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.proxy import router as proxy_router
from app.replay import router as replay_router
from app.db import init_db
from app.dashboard import router as dashboard_router

app = FastAPI(title="VeriLLM Proxy")

init_db()

app.include_router(proxy_router)
app.include_router(replay_router)
app.include_router(dashboard_router)

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")