from fastapi import APIRouter
import sqlite3

router = APIRouter()

@router.get("/replay/{session_id}")
def replay(session_id: str):
    conn = sqlite3.connect("verillm.db")
    c = conn.cursor()
    c.execute("SELECT response_hash FROM sessions WHERE id=?", (session_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return {"error": "Session not found"}

    return {
        "session_id": session_id,
        "stored_response_hash": row[0],
        "status": "Replay stub ready"
    }
