"""Starts the LLTH web app: python -m llth."""

import json
import sys

import uvicorn

from llth.app import app
from llth.paths import SETTINGS_DIR
from llth.servers import port_is_free


def main() -> None:
    settings = json.loads((SETTINGS_DIR / "app.json").read_text(encoding="utf-8"))
    port = settings["port"]
    if not port_is_free(port):
        sys.exit(f"Port {port} is already in use.")
    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
