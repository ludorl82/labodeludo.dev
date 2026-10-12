#!/usr/bin/env python3
"""The public allowlist over a list of strings, for the Node gates.

Reads JSON on stdin and writes JSON on stdout.

  scan-lines.py           in: ["text", …]
                          out: [[index, kind], …] for every string that fails
  scan-lines.py --redact  in: {"texts": [...], "suffix": [...]}
                          out: the texts with redact() applied
  scan-lines.py --suffix  in: {"texts": [...], "suffix": [...]}
                          out: like the first form, with extra allowed suffixes

`kind` is the leak message cut before its first quote ("non-documentation
IPv4"), never the value itself: the caller may be printing into a public CI
log.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from allowlist import Leak, redact, scan  # noqa: E402

mode = sys.argv[1] if len(sys.argv) > 1 else ""
data = json.load(sys.stdin)
if mode in ("--redact", "--suffix"):
    texts, suffix = data["texts"], tuple(s.lower() for s in data.get("suffix", []))
else:
    texts, suffix = data, ()

if mode == "--redact":
    json.dump([redact(t, suffix) for t in texts], sys.stdout)
    sys.exit(0)

out = []
for i, text in enumerate(texts):
    try:
        scan(text, "", suffix)
    except Leak as e:
        out.append([i, str(e).split("'", 1)[0].split('"', 1)[0].strip()])
json.dump(out, sys.stdout)
