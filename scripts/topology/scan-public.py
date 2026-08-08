#!/usr/bin/env python3
"""Gate arbitrary files against the public allowlist.

Usage: scan-public.py <file> [<file> ...]

Used by the nightly diagram job before committing anything an automated
author wrote for the public site: every line of every named file must pass
the same positive allowlist join-topology.py applies to architecture.json
(documentation IPs and example-family domains only — see allowlist.py).
Exit 1 on the first violation, printing what and where. Nothing is ever
modified; this is a read-only gate.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from allowlist import Leak, scan  # noqa: E402

if len(sys.argv) < 2:
    print("usage: scan-public.py <file> [<file> ...]", file=sys.stderr)
    sys.exit(1)

for path in sys.argv[1:]:
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        print(f"scan-public: cannot read {path}: {e}", file=sys.stderr)
        sys.exit(1)
    for lineno, line in enumerate(text.splitlines(), 1):
        try:
            scan(line, f"{path}:{lineno}")
        except Leak as e:
            print(f"scan-public: LEAK {e}", file=sys.stderr)
            sys.exit(1)
print(f"scan-public: {len(sys.argv) - 1} file(s) clean")
