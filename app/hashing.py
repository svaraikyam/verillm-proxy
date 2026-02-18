import hashlib

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def compute_session_hash(prompt_hash: str, response_hash: str, param_hash: str) -> str:
    combined = prompt_hash + response_hash + param_hash
    return sha256_text(combined)