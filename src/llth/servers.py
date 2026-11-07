"""Reads the server settings and runs llama-server."""
import json
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
