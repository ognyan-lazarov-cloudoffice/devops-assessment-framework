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


def to_openai_tools(tools: list) -> list:
    """Convert Anthropic tool definitions to OpenAI/Ollama format."""
    result = []
    for tool in tools:
        result.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
            },
        })
    return result


def to_openai_messages(body: dict) -> list:
    """Convert Anthropic messages payload to OpenAI/Ollama messages list.

    Handles:
      - Plain text content (string or text blocks)
      - tool_use blocks in assistant messages → OpenAI tool_calls
      - tool_result blocks in user messages  → OpenAI role=tool messages
    """
    messages = []
    if "system" in body:
        messages.append({"role": "system", "content": extract_text(body["system"])})

    for msg in body.get("messages", []):
        role = msg["role"]
        content = msg["content"]

        # ── string content ────────────────────────────────────────────────────
        if isinstance(content, str):
            messages.append({"role": role, "content": content})
            continue

        # ── list content ──────────────────────────────────────────────────────
        if not isinstance(content, list):
            continue

        # tool_result blocks → role=tool messages (one per result)
        tool_results = [b for b in content if b.get("type") == "tool_result"]
        if tool_results:
            for tr in tool_results:
                tr_content = tr.get("content", "")
                if isinstance(tr_content, list):
                    tr_content = extract_text(tr_content)
                elif not isinstance(tr_content, str):
                    tr_content = str(tr_content)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tr["tool_use_id"],
                    "content": tr_content,
                })
            continue

        # tool_use blocks → assistant message with tool_calls
        tool_uses = [b for b in content if b.get("type") == "tool_use"]
        if tool_uses:
            text_blocks = [b for b in content if b.get("type") == "text"]
            text_content = "".join(b.get("text", "") for b in text_blocks) or None
            tool_calls = []
            for tu in tool_uses:
                tool_calls.append({
                    "id": tu["id"],
                    "type": "function",
                    "function": {
                        "name": tu["name"],
                        "arguments": json.dumps(tu.get("input", {})),
                    },
                })
            messages.append({
                "role": "assistant",
                "content": text_content,
                "tool_calls": tool_calls,
            })
            continue

        # plain text blocks
        messages.append({"role": role, "content": extract_text(content)})

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
    tools = body.get("tools")
    extra = {"tools": to_openai_tools(tools)} if tools else {}

    if stream:

        async def sse():
            yield (
                "event: message_start\n"
                f"data: {json.dumps({'type': 'message_start', 'message': {'id': 'msg_ollama', 'type': 'message', 'role': 'assistant', 'content': [], 'model': model, 'stop_reason': None, 'usage': {'input_tokens': 0, 'output_tokens': 0}}})}\n\n"
            )
            yield 'event: ping\ndata: {"type":"ping"}\n\n'

            out_tokens = 0
            block_index = -1
            text_started = False
            # tc_index → {block_index, id, name}
            tool_blocks: dict = {}
            finish_reason = None

            ollama_stream = await ollama.chat.completions.create(
                model=model, messages=messages, max_tokens=max_tokens, stream=True,
                **extra
            )

            async for chunk in ollama_stream:
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                delta = choice.delta
                if choice.finish_reason:
                    finish_reason = choice.finish_reason

                # ── text content ──────────────────────────────────────────────
                if delta.content:
                    if not text_started:
                        block_index += 1
                        text_started = True
                        yield (
                            "event: content_block_start\n"
                            f"data: {json.dumps({'type': 'content_block_start', 'index': block_index, 'content_block': {'type': 'text', 'text': ''}})}\n\n"
                        )
                    out_tokens += 1
                    yield (
                        "event: content_block_delta\n"
                        f"data: {json.dumps({'type': 'content_block_delta', 'index': block_index, 'delta': {'type': 'text_delta', 'text': delta.content}})}\n\n"
                    )

                # ── tool call deltas ──────────────────────────────────────────
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        tc_idx = tc.index

                        if tc_idx not in tool_blocks:
                            # Close text block if open
                            if text_started:
                                yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': block_index})}\n\n"
                                text_started = False
                            block_index += 1
                            tc_id = tc.id or f"toolu_{tc_idx}"
                            tc_name = (tc.function.name if tc.function else "") or ""
                            tool_blocks[tc_idx] = {
                                "block_index": block_index,
                                "id": tc_id,
                                "name": tc_name,
                            }
                            yield (
                                "event: content_block_start\n"
                                f"data: {json.dumps({'type': 'content_block_start', 'index': block_index, 'content_block': {'type': 'tool_use', 'id': tc_id, 'name': tc_name, 'input': {}}})}\n\n"
                            )

                        if tc.function and tc.function.arguments:
                            bi = tool_blocks[tc_idx]["block_index"]
                            yield (
                                "event: content_block_delta\n"
                                f"data: {json.dumps({'type': 'content_block_delta', 'index': bi, 'delta': {'type': 'input_json_delta', 'partial_json': tc.function.arguments}})}\n\n"
                            )

            # ── close open blocks ─────────────────────────────────────────────
            if text_started:
                yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': block_index})}\n\n"
            for tb in sorted(tool_blocks.keys()):
                yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': tool_blocks[tb]['block_index']})}\n\n"

            stop_reason = "tool_use" if finish_reason == "tool_calls" else "end_turn"
            yield (
                "event: message_delta\n"
                f"data: {json.dumps({'type': 'message_delta', 'delta': {'stop_reason': stop_reason, 'stop_sequence': None}, 'usage': {'output_tokens': out_tokens}})}\n\n"
            )
            yield 'event: message_stop\ndata: {"type":"message_stop"}\n\n'

        return StreamingResponse(sse(), media_type="text/event-stream")

    # ── non-streaming ─────────────────────────────────────────────────────────
    resp = await ollama.chat.completions.create(
        model=model, messages=messages, max_tokens=max_tokens, **extra
    )
    msg = resp.choices[0].message

    if msg.tool_calls:
        content = []
        if msg.content:
            content.append({"type": "text", "text": msg.content})
        for tc in msg.tool_calls:
            try:
                tc_input = json.loads(tc.function.arguments)
            except (json.JSONDecodeError, TypeError):
                tc_input = {}
            content.append({
                "type": "tool_use",
                "id": tc.id,
                "name": tc.function.name,
                "input": tc_input,
            })
        stop_reason = "tool_use"
    else:
        content = [{"type": "text", "text": msg.content or ""}]
        stop_reason = "end_turn"

    return Response(
        content=json.dumps({
            "id": "msg_ollama",
            "type": "message",
            "role": "assistant",
            "content": content,
            "model": model,
            "stop_reason": stop_reason,
            "stop_sequence": None,
            "usage": {
                "input_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                "output_tokens": resp.usage.completion_tokens if resp.usage else 0,
            },
        }),
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
