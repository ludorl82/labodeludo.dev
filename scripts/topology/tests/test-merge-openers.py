#!/usr/bin/env python3
"""Tests for merge-openers.py — the three decisions that belong to neither half.

Each half of the panel is gated on its own terms elsewhere. What is decided
here is precedence, the cap on the merged list, and the provenance record, and
each of those is a place where a silent mistake looks exactly like success: a
panel of eight French buttons renders fine, and a `written` list that quietly
omits a written question makes the commit message a lie without any test going
red.

Offline, no fixtures on disk beyond two small JSON files.

  python3 scripts/topology/tests/test-merge-openers.py
"""
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
MERGE = HERE.parent / "merge-openers.py"

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  \033[32mok\033[0m   {label}")
    else:
        failed += 1
        print(f"  \033[31mFAIL\033[0m {label}: got {got!r}, wanted {want!r}")


def run(real, written, tmp, skip_written=False):
    d = pathlib.Path(tmp)
    (d / "kept.json").write_text(json.dumps({"openers": real}, ensure_ascii=False),
                                 encoding="utf-8")
    wp = d / "written.json"
    if skip_written:
        wp.unlink(missing_ok=True)
    else:
        wp.write_text(json.dumps({"openers": written}, ensure_ascii=False), encoding="utf-8")
    out = d / "out.json"
    r = subprocess.run([sys.executable, str(MERGE), str(d / "kept.json"), str(wp),
                        str(out), "2026-09-15T04:30:00Z"], capture_output=True, text=True)
    if r.returncode != 0:
        return r.returncode, None
    return 0, json.loads(out.read_text(encoding="utf-8"))


FR = [f"Comment roule le nœud numéro {i} chez vous ?" for i in range(6)]
EN = [f"How does node number {i} run at your place?" for i in range(6)]

with tempfile.TemporaryDirectory() as tmp:
    print("\033[1m== real questions come first\033[0m")
    rc, d = run(FR[:1], FR[1:3], tmp)
    check("exit 0", rc, 0)
    check("the asked one leads", d["openers"][0], FR[0])
    check("the written ones follow", d["openers"][1:], FR[1:3])
    check("and only the written ones are recorded as written", d["written"], FR[1:3])

    print("\n\033[1m== the cap applies to the MERGE, not to each half\033[0m")
    # Four real French plus two written French is six questions for four
    # buttons. Each half was within its own cap; only this step sees both.
    rc, d = run(FR[:4], FR[4:6], tmp)
    check("four French survive", len([q for q in d["openers"] if "roule" in q]), 4)
    check("the written ones are the ones dropped", d["written"], [])
    rc, d = run(FR[:2] + EN[:2], FR[2:4] + EN[2:4], tmp)
    check("each language is capped on its own", len(d["openers"]), 8)
    check("four French", len([q for q in d["openers"] if "roule" in q]), 4)
    check("four English", len([q for q in d["openers"] if "node number" in q]), 4)

    print("\n\033[1m== provenance is recorded exactly\033[0m")
    rc, d = run([], EN[:3], tmp)
    check("all three are written", sorted(d["written"]), sorted(EN[:3]))
    check("written is a subset of what is published",
          set(d["written"]) <= set(d["openers"]), True)
    # A question that BOTH halves produced was really asked, so it is not
    # written — claiming otherwise would understate the panel's evidence.
    rc, d = run(FR[:1], FR[:1], tmp)
    check("a question in both halves appears once", d["openers"], FR[:1])
    check("and counts as asked, not written", d["written"], [])

    print("\n\033[1m== a missing half is an empty half, not a crash\033[0m")
    rc, d = run(FR[:2], [], tmp, skip_written=True)
    check("exit 0 with no written.json at all", rc, 0)
    check("the real questions still publish", d["openers"], FR[:2])
    rc, d = run([], [], tmp)
    check("both empty is still a valid file", (rc, d["openers"]), (0, []))

    print("\n\033[1m== the timestamp is the caller's, not the clock's\033[0m")
    rc, d = run(FR[:1], [], tmp)
    check("stamped as given", d["generated"], "2026-09-15T04:30:00Z")

print(f"\n\033[1m{passed} passed, {failed} failed\033[0m")
sys.exit(1 if failed else 0)
