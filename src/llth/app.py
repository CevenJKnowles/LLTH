"""The LLTH web app: serves the page and the API behind it."""
import subprocess
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
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


experts = load_experts()
state = State(load_server_settings(), experts, next(iter(experts)))

app = FastAPI()


@app.get("/")
def index() -> FileResponse:
    """Serve the interface page."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/state")
def get_state() -> dict:
    """What the page needs to draw itself: experts, current mode, server status."""
    current = state.experts[state.current]
    return {
        "current": state.current,
        "experts": [
            {"key": key, "name": expert.name, "description": expert.description}
            for key, expert in state.experts.items()
        ],
        "server": state.settings.servers[current.server].short,
        "running": state.process is not None and state.process.poll() is None,
    }


def ensure_server(server_key: str) -> None:
    """Run the server for server_key; stop a different one first."""
    if state.process is not None and state.process.poll() is None:
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


@app.post("/api/mode")
def set_mode(key: str) -> dict:
    """Switch the expert, swapping the server if it needs a different one."""
    if key not in state.experts:
        raise HTTPException(status_code=404, detail=f"Unknown expert: {key}")
    try:
        ensure_server(state.experts[key].server)
    except (RuntimeError, TimeoutError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    state.current = key
    return get_state()
