"""Platform-specific user data paths and high-score persistence."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def user_data_file(filename: str) -> Path:
    """Return a writable per-user data path on every supported platform."""
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        directory = root / "FruitSlash"
    elif sys.platform == "darwin":
        directory = Path.home() / "Library" / "Application Support" / "FruitSlash"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        directory = root / "fruit-slash"
    return directory / filename


def load_highscore(path: Path) -> int:
    """Read the saved high score, falling back to zero when unavailable."""
    try:
        return int(path.read_text().strip())
    except (OSError, ValueError):
        return 0


def save_highscore(path: Path, score: int) -> None:
    """Persist the high score and silently ignore storage failures."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(score))
    except OSError:
        pass

