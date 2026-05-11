from __future__ import annotations

import shlex
import sys
from pathlib import Path

from .config import load_config
from .errors import VibeCodeError, RuntimeVibeError
from .runner import run_file


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        config = load_config(Path.cwd())
        if not args:
            print("Usage: vibecoded <file>.vb | vibecoded run <command>", file=sys.stderr)
            return 2
        if args[0] == "run":
            if len(args) != 2:
                raise RuntimeVibeError("CLI error", "Usage: vibecoded run <command>")
            command = config.commands.get(args[1])
            if command is None:
                raise RuntimeVibeError("CLI error", f"Unknown configured command '{args[1]}'")
            return _run_configured_command(command, config)
        if len(args) != 1:
            raise RuntimeVibeError("CLI error", "Usage: vibecoded <file>.vb")
        run_file(args[0], config)
        return 0
    except FileNotFoundError as exc:
        print(RuntimeVibeError("File error", str(exc)).format(), file=sys.stderr)
        return 1
    except VibeCodeError as exc:
        print(exc.format(), file=sys.stderr)
        return 1


def _run_configured_command(command: str, config) -> int:
    parts = shlex.split(command)
    if len(parts) != 2 or parts[0] != "vibecoded":
        raise RuntimeVibeError(
            "Config error",
            "Configured commands must be shaped like 'vibecoded <file>.vb'",
        )
    run_file(parts[1], config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
