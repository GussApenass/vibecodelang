from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .errors import RuntimeVibeError


@dataclass
class VibeConfig:
    commands: dict[str, str] = field(default_factory=dict)
    strict_mode: bool = True
    allow_implicit_types: bool = False


def load_config(start: Path | None = None) -> VibeConfig:
    root = start or Path.cwd()
    config_path = root / "vbconfigs.json"
    if not config_path.exists():
        return VibeConfig()
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeVibeError("Config error", str(exc), str(config_path), exc.lineno, exc.colno)
    return VibeConfig(
        commands=dict(data.get("commands", {})),
        strict_mode=bool(data.get("strictMode", True)),
        allow_implicit_types=bool(data.get("allowImplicitTypes", False)),
    )
