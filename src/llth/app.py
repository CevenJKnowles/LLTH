"""The LLTH web app: serves the page and the API behind it."""

import json
import subprocess
import threading
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from llth.chat import stream_reply
from llth.experts import Expert, load_experts
from llth.paths import STATIC_DIR
from llth.servers import (
    ServerSettings,
    load_server_settings,
    start_server,
    stop_server,
    wait_until_ready,
)


@dataclass
class State:
    settings: ServerSettings
    experts: dict[str, Expert]
    current: str
    process: subprocess.Popen | None = None
    running_key: str | None = None
    loading_since: float | None = None
    load_error: str | None = None


experts = load_experts()
state = State(load_server_settings(), experts, next(iter(experts)))


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Start the current expert's server at launch; stop the server at exit."""
    begin_switch(state.experts[state.current].server)
    yield
    if server_running():
        stop_server(state.process)


app = FastAPI(lifespan=lifespan)


@app.get("/")
def index() -> FileResponse:
    """Serve the interface page."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/state")
def get_state() -> dict:
    """What the page needs to draw itself: experts, current mode, server status."""
    server = state.settings.servers[state.experts[state.current].server]
    loading = None
    if state.loading_since is not None:
        elapsed = time.monotonic() - state.loading_since
        loading = {"elapsed": round(elapsed, 1), "total": server.load_seconds}
    return {
        "current": state.current,
        "experts": [
            {"key": key, "name": expert.name, "description": expert.description}
            for key, expert in state.experts.items()
        ],
        "server": server.short,
        "running": server_running() and state.loading_since is None,
        "loading": loading,
        "error": state.load_error,
    }


def server_running() -> bool:
    """True when a model server process is alive."""
    return state.process is not None and state.process.poll() is None


def ensure_server(server_key: str) -> None:
    """Run the server for server_key; stop a different one first."""
    if server_running():
        if state.running_key == server_key:
            return
        stop_server(state.process)
    state.process = start_server(state.settings, server_key)
    state.running_key = server_key
    try:
        wait_until_ready(state.settings, state.process)
    except (RuntimeError, TimeoutError):
        stop_server(state.process)
        state.process = state.running_key = None
        raise


def begin_switch(server_key: str) -> None:
    """Mark the state as loading and run ensure_server in a background thread."""
    state.loading_since = time.monotonic()
    state.load_error = None
    threading.Thread(target=run_switch, args=(server_key,), daemon=True).start()


def run_switch(server_key: str) -> None:
    """Run ensure_server; keep a failure in the state; always end the loading."""
    try:
        ensure_server(server_key)
    except (RuntimeError, TimeoutError) as error:
        state.load_error = str(error)
    finally:
        state.loading_since = None


async def to_lines(events: AsyncIterator[dict]) -> AsyncIterator[str]:
    """Turn events into one JSON object per line."""
    async for event in events:
        yield json.dumps(event) + "\n"


@app.post("/api/mode")
def set_mode(key: str) -> dict:
    """Switch the expert; swap the server in the background if it needs one."""
    if key not in state.experts:
        raise HTTPException(status_code=404, detail=f"Unknown expert: {key}")
    if state.loading_since is not None:
        raise HTTPException(status_code=409, detail="A server swap is already running.")
    state.current = key
    server_key = state.experts[key].server
    if not server_running() or state.running_key != server_key:
        begin_switch(server_key)
    return get_state()


@app.post("/api/chat")
def chat(messages: Annotated[list[dict], Body(embed=True)]) -> StreamingResponse:
    """Stream the reply to the conversation, one JSON object per line."""
    if state.loading_since is not None:
        raise HTTPException(status_code=503, detail="The model is loading.")
    if not server_running():
        raise HTTPException(status_code=503, detail="No model server is running.")
    instructions = state.experts[state.current].instructions
    if instructions:
        messages = [{"role": "system", "content": instructions}, *messages]
    events = stream_reply(state.settings, messages)
    return StreamingResponse(to_lines(events), media_type="application/x-ndjson")
