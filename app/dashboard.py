from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import sqlite3
import httpx
from fastapi.responses import JSONResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
def dashboard(request: Request):
    conn = sqlite3.connect("verillm.db")
    c = conn.cursor()
    c.execute("""
        SELECT id, model, created_at, integrity_status
        FROM sessions
        ORDER BY created_at DESC
    """)
    rows = c.fetchall()
    conn.close()

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "sessions": rows}
    )


@router.get("/dashboard/session/{session_id}")
async def session_detail(request: Request, session_id: str):

    conn = sqlite3.connect("verillm.db")
    c = conn.cursor()
    c.execute("""
        SELECT prompt, response, response_hash, session_hash, created_at
        FROM sessions
        WHERE id=?
    """, (session_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return {"error": "Session not found"}

    return templates.TemplateResponse(
        "session_detail.html",
        {
            "request": request,
            "session_id": session_id,
            "prompt": row[0],
            "response": row[1],
            "response_hash": row[2],
            "session_hash": row[3],
            "created_at": row[4],
            "replay_result": None
        }
    )


@router.post("/dashboard/replay/{session_id}")
async def replay_from_dashboard(request: Request, session_id: str):

    async with httpx.AsyncClient() as client:
        replay_response = await client.get(
            f"http://localhost:8001/replay/{session_id}"
        )
        replay_result = replay_response.json()

    conn = sqlite3.connect("verillm.db")
    c = conn.cursor()
    c.execute("""
        SELECT prompt, response, response_hash, session_hash, created_at
        FROM sessions
        WHERE id=?
    """, (session_id,))
    row = c.fetchone()
    conn.close()

    return templates.TemplateResponse(
        "session_detail.html",
        {
            "request": request,
            "session_id": session_id,
            "prompt": row[0],
            "response": row[1],
            "response_hash": row[2],
            "session_hash": row[3],
            "created_at": row[4],
            "replay_result": replay_result
        }
    )
@router.get("/dashboard/export/{session_id}")
def export_session(session_id: str):

    conn = sqlite3.connect("verillm.db")
    c = conn.cursor()
    c.execute("SELECT * FROM sessions WHERE id=?", (session_id,))
    row = c.fetchone()
    columns = [description[0] for description in c.description]
    conn.close()

    if not row:
        return {"error": "Session not found"}

    data = dict(zip(columns, row))

    return JSONResponse(content=data)