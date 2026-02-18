from fastapi import APIRouter
import sqlite3
import json
import httpx
from app.hashing import sha256_text

router = APIRouter()

VLLM_URL = "http://localhost:8000/v1/chat/completions"

@router.get("/replay/{session_id}")
async def replay(session_id: str):
    conn = sqlite3.connect("verillm.db")
    c = conn.cursor()
    c.execute("""
        SELECT parameters, response_hash
        FROM sessions
        WHERE id=?
    """, (session_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return {"error": "Session not found"}

    parameters_json, original_hash = row
    parameters = json.loads(parameters_json)

    # Re-run inference
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(VLLM_URL, json=parameters)
        new_result = response.json()

    if "choices" not in new_result:
        return {"error": "Replay inference failed"}

    assistant_content = new_result["choices"][0]["message"]["content"]
    new_hash = sha256_text(assistant_content)

    conn = sqlite3.connect("verillm.db")
    c = conn.cursor()
    c.execute(
        "UPDATE sessions SET integrity_status=? WHERE id=?",
        (str(original_hash == new_hash).lower(), session_id)
    )
    conn.commit()
    conn.close()

    return {
        "session_id": session_id,
        "original_response_hash": original_hash,
        "new_response_hash": new_hash,
        "match": original_hash == new_hash
    }
