"""Reads the server settings and runs llama-server."""
import json
import socket
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from llth.paths import HOME, SETTINGS_DIR


@dataclass(frozen=True)
class Server:
    label: str
    load_seconds: int
    args: tuple[str, ...]
    short: str


@dataclass(frozen=True)
class ServerSettings:
    port: int
    binary: str
    temperature_stop_c: int
    servers: dict[str, Server]


def load_server_settings() -> ServerSettings:
    """Load servers.json, with $LLTH_HOME replaced by the repository folder."""
    path = SETTINGS_DIR / "servers.json"
    text = path.read_text(encoding="utf-8").replace("$LLTH_HOME", str(HOME))
    try:
        data = json.loads(text)
        return ServerSettings(
            port=data["port"],
            binary=data["binary"],
            temperature_stop_c=data["temperature_stop_c"],
            servers={
                key: Server(**{**server, "args": tuple(server["args"])})
                for key, server in data["servers"].items()
            },
        )
    except (ValueError, TypeError, KeyError) as error:
        raise ValueError(f"{path.name}: {error}") from error


def port_is_free(port: int) -> bool:
    """True when nothing is listening on 127.0.0.1 at the port."""
    with socket.socket() as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def start_server(settings: ServerSettings, key: str) -> subprocess.Popen:
    """Start llama-server for the given server key; refuse if the port is taken."""
    if not port_is_free(settings.port):
        raise RuntimeError(f"Port {settings.port} is already in use.")
    command = [
        settings.binary,
        *settings.servers[key].args,
        "--host", "127.0.0.1",
        "--port", str(settings.port),
    ]
    return subprocess.Popen(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def stop_server(process: subprocess.Popen) -> None:
    """Ask the process to end; kill it if it has not ended after five seconds."""
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def wait_until_ready(
    settings: ServerSettings, process: subprocess.Popen, timeout: float = 60
) -> None:
    """Return when /health answers 200; raise if the process ends or time runs out."""
    url = f"http://127.0.0.1:{settings.port}/health"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("llama-server ended before it was ready.")
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            pass
        time.sleep(0.5)
    raise TimeoutError(f"llama-server was not ready after {timeout} seconds.")
