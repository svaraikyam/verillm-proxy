# VeriLLM Proxy (v0.1)

VeriLLM Proxy is a deterministic and auditable middleware layer for LLM inference systems.

It intercepts OpenAI-compatible inference requests, enforces deterministic parameters,
generates cryptographic hashes, and stores tamper-evident session records.

## Features (v0.1)

- Reverse proxy for OpenAI-compatible LLM APIs
- Deterministic execution enforcement
- Prompt & response hashing (SHA256)
- Session fingerprint generation
- SQLite-based audit storage
- Replay endpoint (stub)

## Architecture

Client → VeriLLM Proxy → vLLM → Response  
VeriLLM logs prompt, parameters, response, and session hash.

## Local Setup

### 1. Install dependencies

