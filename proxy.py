#!/usr/bin/env python3
"""
Routing proxy for Claude Code (Pro plan — no API key required).

  claude-* models  →  transparent passthrough to api.anthropic.com
                       (Pro plan OAuth token forwarded as-is)
  Ollama models    →  translated to Ollama OpenAI-compat API at localhost:11434

Usage:
  pip install fastapi uvicorn httpx openai
  python proxy.py

Then start Claude Code with:
  claude --settings proxy.settings.json
"""

import json
import logging

import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI

log = logging.getLogger("proxy")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI()

ANTHROPIC_API = "https://api.anthropic.com"
OLLAMA_BASE = "http://localhost:11434/v1"

SKIP_HEADERS = {"host", "content-length", "transfer-encoding", "connection"}

# Add Ollama model names here as needed
OLLAMA_MODELS = {
    "qwen3-coder:30b-a3b-q8_0",
}

ollama = AsyncOpenAI(base_url=OLLAMA_BASE, api_key="ollama", timeout=600.0)


# ── helpers ───────────────────────────────────────────────────────────────────


def extract_text(content) -> str:
    """Normalize Anthropic content (plain string or content-block list) to str."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") for block in content if block.get("type") == "text"
        )
    return ""


def to_openai_messages(body: dict) -> list:
    """Convert Anthropic messages payload to OpenAI/Ollama messages list."""
    messages = []
    if "system" in body:
        messages.append({"role": "system", "content": extract_text(body["system"])})
    for msg in body.get("messages", []):
        messages.append({"role": msg["role"], "content": extract_text(msg["content"])})
    return messages


# ── Anthropic passthrough ─────────────────────────────────────────────────────


async def passthrough(request: Request, path: str, body_bytes: bytes):
    headers = {
        k: v for k, v in request.headers.items() if k.lower() not in SKIP_HEADERS
    }
    async with httpx.AsyncClient(timeout=600.0) as client:
        resp = await client.request(
            method=request.method,
            url=f"{ANTHROPIC_API}/{path}",
            content=body_bytes,
            headers=headers,
        )
    resp_headers = {
        k: v
        for k, v in resp.headers.items()
        if k.lower() not in {"content-length", "transfer-encoding"}
    }
    if "text/event-stream" in resp.headers.get("content-type", ""):
        return StreamingResponse(
            resp.aiter_bytes(),
            status_code=resp.status_code,
            headers=resp_headers,
            media_type="text/event-stream",
        )
    return Response(
        content=resp.content, status_code=resp.status_code, headers=resp_headers
    )


# ── Ollama routing ────────────────────────────────────────────────────────────


async def route_ollama(body: dict):
    model = body["model"]
    messages = to_openai_messages(body)
    max_tokens = body.get("max_tokens", 4096)
    stream = body.get("stream", False)

    if stream:

        async def sse():
            yield (
                "event: message_start\n"
                f"data: {json.dumps({'type': 'message_start', 'message': {'id': 'msg_ollama', 'type': 'message', 'role': 'assistant', 'content': [], 'model': model, 'stop_reason': None, 'usage': {'input_tokens': 0, 'output_tokens': 0}}})}\n\n"
            )
            yield (
                "event: content_block_start\n"
                f"data: {json.dumps({'type': 'content_block_start', 'index': 0, 'content_block': {'type': 'text', 'text': ''}})}\n\n"
            )
            yield 'event: ping\ndata: {"type":"ping"}\n\n'

            out_tokens = 0
            ollama_stream = await ollama.chat.completions.create(
                model=model, messages=messages, max_tokens=max_tokens, stream=True
            )
            async for chunk in ollama_stream:
                text = chunk.choices[0].delta.content or ""
                if text:
                    out_tokens += 1
                    yield (
                        "event: content_block_delta\n"
                        f"data: {json.dumps({'type': 'content_block_delta', 'index': 0, 'delta': {'type': 'text_delta', 'text': text}})}\n\n"
                    )

            yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': 0})}\n\n"
            yield (
                "event: message_delta\n"
                f"data: {json.dumps({'type': 'message_delta', 'delta': {'stop_reason': 'end_turn', 'stop_sequence': None}, 'usage': {'output_tokens': out_tokens}})}\n\n"
            )
            yield 'event: message_stop\ndata: {"type":"message_stop"}\n\n'

        return StreamingResponse(sse(), media_type="text/event-stream")

    # Non-streaming
    resp = await ollama.chat.completions.create(
        model=model, messages=messages, max_tokens=max_tokens
    )
    text = resp.choices[0].message.content or ""
    return Response(
        content=json.dumps(
            {
                "id": "msg_ollama",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": text}],
                "model": model,
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {
                    "input_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                    "output_tokens": resp.usage.completion_tokens if resp.usage else 0,
                },
            }
        ),
        media_type="application/json",
    )


# ── model state ──────────────────────────────────────────────────────────────

_MODEL_STATE_FILE = "/tmp/cc-proxy-model"


def _write_model_state(model: str) -> None:
    """Write the last routed model to a temp file for the status line to read."""
    try:
        with open(_MODEL_STATE_FILE, "w") as f:
            f.write(model)
    except OSError:
        pass


# ── router ────────────────────────────────────────────────────────────────────


@app.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route(request: Request, path: str):
    body_bytes = await request.body()
    try:
        body = json.loads(body_bytes) if body_bytes else {}
    except json.JSONDecodeError:
        body = {}

    model = body.get("model", "<no-model>")
    if model in OLLAMA_MODELS:
        log.info("ROUTE  ollama   model=%s path=%s", model, path)
        _write_model_state(model)
        return await route_ollama(body)
    log.info("ROUTE  anthropic model=%s path=%s", model, path)
    _write_model_state(model)
    return await passthrough(request, f"v1/{path}", body_bytes)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4000, log_level="info")
