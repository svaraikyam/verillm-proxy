from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import sqlite3

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
def dashboard(request: Request):
    conn = sqlite3.connect("verillm.db")
    c = conn.cursor()
    c.execute("""
        SELECT id, model, created_at
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
def session_detail(request: Request, session_id: str):
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
        }
    )
