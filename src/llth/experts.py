"""Reads the expert files from EXPERTS_DIR."""

import json
from dataclasses import dataclass

from llth.paths import EXPERTS_DIR


@dataclass(frozen=True)
class Expert:
    name: str
    order: int
    server: str
    effort: str
    description: str
    instructions: str


def load_experts() -> dict[str, Expert]:
    """Load the experts from the EXPERTS_DIR."""
    experts = {}
    for path in sorted(EXPERTS_DIR.glob("*.json")):
        try:
            expert = Expert(**json.loads(path.read_text(encoding="utf-8")))
        except (ValueError, TypeError) as error:
            raise ValueError(f"{path.name}: {error}") from error
        experts[path.stem] = expert
    return dict(sorted(experts.items(), key=lambda item: item[1].order))
