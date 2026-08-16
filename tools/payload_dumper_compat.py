#!/usr/bin/env python3
"""Run the installed payload_dumper module with unchanged CLI arguments."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    return subprocess.call([sys.executable, "-m", "payload_dumper", *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
