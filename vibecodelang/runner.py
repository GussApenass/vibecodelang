from __future__ import annotations

from pathlib import Path

from .config import VibeConfig
from .interpreter import interpret_source


def run_file(path: str | Path, config: VibeConfig | None = None) -> None:
    file_path = Path(path)
    source = file_path.read_text(encoding="utf-8")
    cfg = config or VibeConfig()
    interpret_source(
        source,
        str(file_path),
        strict_mode=cfg.strict_mode,
        allow_implicit_types=cfg.allow_implicit_types,
    )
