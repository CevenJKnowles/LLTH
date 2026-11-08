"""Sends messages to llama-server and yields the reply as it arrives."""

import json
from collections.abc import AsyncIterator

import httpx

from llth.servers import ServerSettings

USAGE_KEYS = ("prompt_tokens", "completion_tokens")


async def stream_reply(
    settings: ServerSettings, messages: list[dict]
) -> AsyncIterator[dict]:
    """Yield {"text": ...} for each piece of the reply, then {"usage": ...}."""
    url = f"http://127.0.0.1:{settings.port}/v1/chat/completions"
    body = {
        "messages": messages,
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    async with (
        httpx.AsyncClient(timeout=None) as client,
        client.stream("POST", url, json=body) as response,
    ):
        response.raise_for_status()
        async for line in response.aiter_lines():
            if not line.startswith("data: ") or line == "data: [DONE]":
                continue
            chunk = json.loads(line.removeprefix("data: "))
            if chunk["choices"]:
                text = chunk["choices"][0]["delta"].get("content")
                if text:
                    yield {"text": text}
            if "usage" in chunk:
                usage = chunk["usage"]
                yield {"usage": {key: usage[key] for key in USAGE_KEYS}}
