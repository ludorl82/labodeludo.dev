#!/usr/bin/env python3
"""Stamp the drift-check verification state into architecture.json.

Usage: fetch-drift.py <kuma-base-url> [architecture.json]

Queries the public Uptime Kuma status page `iac-drift` (the three nightly
drift monitors: aws-iac, nixos-iac, cloudflare-iac — each asserts its repo
still matches the real infrastructure) and writes a `verified` block into
the joined architecture.json. This is the page's honesty mechanism: the
diagram is trustworthy exactly when the drift checks are green, and the
badge says which it is.

Fail-open to UNKNOWN, never to green: any fetch/parse problem writes
status "unknown" (replacing whatever verified block was there — a stale
green is the one lie this file must never tell) and exits 0 so the build
continues with an honest badge rather than failing the night.
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

if len(sys.argv) not in (2, 3):
    print("usage: fetch-drift.py <kuma-base-url> [architecture.json]",
          file=sys.stderr)
    sys.exit(1)
base = sys.argv[1].rstrip("/")
arch_path = sys.argv[2] if len(sys.argv) == 3 else os.path.join(
    os.path.dirname(__file__), "..", "..", "src", "data", "architecture.json")

SLUG = "iac-drift"

def fetch(url):
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.load(r)

verified = {"status": "unknown", "checkedAt": None, "monitors": []}
try:
    page = fetch(f"{base}/api/status-page/{SLUG}")
    beats = fetch(f"{base}/api/status-page/heartbeat/{SLUG}")
    names = {str(m["id"]): m["name"]
             for g in page.get("publicGroupList", [])
             for m in g.get("monitorList", [])}
    if not names:
        raise ValueError("status page has no monitors")
    statuses = []
    for mid, name in names.items():
        heart = (beats.get("heartbeatList", {}).get(mid) or [])
        last = heart[-1] if heart else None
        up = bool(last and last.get("status") == 1)
        statuses.append(up)
        verified["monitors"].append({
            # keep the output shape boring: names are display-only and
            # clamped to a safe charset before entering the public file
            "name": re.sub(r"[^A-Za-z0-9 ._-]", "", name),
            "up": up,
            "time": (last or {}).get("time"),
        })
    verified["status"] = "ok" if all(statuses) else "drift"
    verified["checkedAt"] = datetime.now(timezone.utc).isoformat(
        timespec="seconds")
except Exception as e:  # noqa: BLE001 — any failure means "unknown"
    print(f"fetch-drift: {e} -> verified=unknown", file=sys.stderr)
    verified = {"status": "unknown", "checkedAt": None, "monitors": []}

arch = json.load(open(arch_path, encoding="utf-8"))
arch["verified"] = verified
with open(arch_path, "w", encoding="utf-8") as f:
    json.dump(arch, f, indent=2, sort_keys=True)
    f.write("\n")
print(f"fetch-drift: verified={verified['status']} "
      f"({len(verified['monitors'])} monitors)")
