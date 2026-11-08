"""Locations of LLTH's code and data; the only module that builds paths."""
from pathlib import Path

HOME = Path(__file__).resolve().parents[2]
POINTER = HOME / ".llth-root"


def read_data_root() -> Path:
    """The path in the pointer file, else HOME/data."""
    if POINTER.is_file():
        line = POINTER.read_text(encoding="utf-8").strip()
        if line:
            return Path(line)
    return HOME / "data"


DATA_ROOT = read_data_root()
EXPERTS_DIR = DATA_ROOT / "LLTH" / "experts"
SETTINGS_DIR = DATA_ROOT / "LLTH" / "settings"
STATIC_DIR = HOME / "src" / "llth" / "static"
