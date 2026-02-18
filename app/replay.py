from fastapi import APIRouter
import sqlite3
import json
import httpx
from app.hashing import sha256_text
from app.kms_signing import verify_signature

router = APIRouter()

VLLM_URL = "http://localhost:8000/v1/chat/completions"


@router.get("/replay/{session_id}")
async def replay(session_id: str):

    print("\n=== REPLAY START ===")

    # Fetch session data
    conn = sqlite3.connect("verillm.db")
    c = conn.cursor()
    c.execute("""
        SELECT parameters, response_hash, session_hash, signature, response
        FROM sessions
        WHERE id=?
    """, (session_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        print("Session not found")
        return {"error": "Session not found"}

    parameters_json, original_response_hash, stored_session_hash, signature, stored_response_json = row

    print("Stored Response Hash:", original_response_hash)
    print("Stored Session Hash:", stored_session_hash)
    print("Stored Signature Length:", len(signature) if signature else None)

    # 🔐 Step 1 — Verify KMS Signature
    if not signature:
        print("No signature present")
        return {"error": "No signature found for session."}

    signature_valid = verify_signature(stored_session_hash, signature)
    print("Signature Valid:", signature_valid)

    if not signature_valid:
        return {
            "error": "Signature verification failed. Session may be tampered.",
            "signature_valid": False
        }

    # Extract original assistant text
    stored_response = json.loads(stored_response_json)
    original_text = stored_response["choices"][0]["message"]["content"]

    print("ORIGINAL TEXT REPR:", repr(original_text))

    # 🔁 Step 2 — Deterministic Replay
    parameters = json.loads(parameters_json)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(VLLM_URL, json=parameters)
        new_result = response.json()

    if "choices" not in new_result:
        print("Replay inference failed:", new_result)
        return {"error": "Replay inference failed"}

    assistant_content = new_result["choices"][0]["message"]["content"]
    print("REPLAY TEXT REPR:", repr(assistant_content))

    new_response_hash = sha256_text(assistant_content)

    print("New Response Hash:", new_response_hash)

    match = original_response_hash == new_response_hash
    print("HASH MATCH:", match)

    # 🔄 Step 3 — Update Integrity Status
    conn = sqlite3.connect("verillm.db")
    c = conn.cursor()
    c.execute(
        "UPDATE sessions SET integrity_status=? WHERE id=?",
        (str(match).lower(), session_id)
    )
    conn.commit()
    conn.close()

    print("=== REPLAY END ===\n")

    return {
        "session_id": session_id,
        "signature_valid": True,
        "original_response_hash": original_response_hash,
        "new_response_hash": new_response_hash,
        "match": match
    }
