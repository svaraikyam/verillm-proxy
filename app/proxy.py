from fastapi import APIRouter, Request
import httpx
import uuid
import json
from datetime import datetime
from app.hashing import sha256_text, compute_session_hash
from app.db import save_session
from app.kms_signing import sign_hash

router = APIRouter()

VLLM_URL = "http://localhost:8000/v1/chat/completions"

@router.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    body = await request.json()

    # Deterministic enforcement
    body["temperature"] = 0.0
    body["seed"] = 42

    async with httpx.AsyncClient() as client:
        response = await client.post(VLLM_URL, json=body)
        result = response.json()

    prompt_text = json.dumps(body.get("messages", ""))
    response_text = json.dumps(result)
    assistant_content = result["choices"][0]["message"]["content"]

    prompt_hash = sha256_text(prompt_text)
    response_hash = sha256_text(assistant_content)
    param_hash = sha256_text(json.dumps(body))

    session_hash = compute_session_hash(prompt_hash, response_hash, param_hash)
    session_id = str(uuid.uuid4())
    signature = sign_hash(session_hash)
    print("DEBUG SIGNATURE:", signature)

    
    save_session((
        session_id,
        body.get("model"),
        prompt_text,
        json.dumps(body),
        response_text,
        prompt_hash,
        response_hash,
        session_hash,
        datetime.utcnow().isoformat(),
        None,  
        signature
    ))

    return result
