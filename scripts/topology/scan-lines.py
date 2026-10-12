#!/usr/bin/env python3
"""The public allowlist over a list of strings, for check-public-leaks.mjs.

Reads a JSON array of strings on stdin and writes a JSON array of
[index, kind] for every string that fails allowlist.scan(). `kind` is the
leak message cut before its first quote — "non-documentation IPv4", never
the value itself, because the caller may be printing into a public CI log.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from allowlist import Leak, scan  # noqa: E402

out = []
for i, text in enumerate(json.load(sys.stdin)):
    try:
        scan(text, "")
    except Leak as e:
        out.append([i, str(e).split("'", 1)[0].split('"', 1)[0].strip()])
json.dump(out, sys.stdout)
