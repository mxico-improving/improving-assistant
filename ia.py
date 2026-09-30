#!/usr/bin/env python3
"""Run the improving-assistant CLI without installing anything (stdlib only).

Usage: python3 ia.py <command> [...]   (on Windows: py ia.py <command>)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from improving_assistant.cli import main  # noqa: E402

raise SystemExit(main())
