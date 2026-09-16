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


def run(real, written, tmp, skip_written=False, curated=None):
    d = pathlib.Path(tmp)
    (d / "kept.json").write_text(json.dumps({"openers": real}, ensure_ascii=False),
                                 encoding="utf-8")
    wp = d / "written.json"
    if skip_written:
        wp.unlink(missing_ok=True)
    else:
        wp.write_text(json.dumps({"openers": written}, ensure_ascii=False), encoding="utf-8")
    out = d / "out.json"
    extra = []
    if curated is not None:
        cp = d / "curated.json"
        cp.write_text(json.dumps({"openers": curated}, ensure_ascii=False), encoding="utf-8")
        extra = ["--curated", str(cp)]
    r = subprocess.run([sys.executable, str(MERGE), *extra, str(d / "kept.json"), str(wp),
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

    print("\n\033[1m== the curated source sits between asked and written\033[0m")
    # Ludo's own questions are a person's judgement: stronger than a guess,
    # weaker than evidence that somebody really asked.
    rc, d = run(FR[:1], FR[2:3], tmp, curated=FR[1:2])
    check("exit 0", rc, 0)
    check("asked, curated, written — in that order", d["openers"], FR[:3])
    check("curated is labelled", d["curated"], FR[1:2])
    check("and is not counted as written", d["written"], FR[2:3])

    print("\n\033[1m== a string in two sources keeps the STRONGER claim\033[0m")
    # A visitor may well ask exactly what Ludo curated. Calling it curated then
    # would quietly shrink the count of real questions the pipeline rests on.
    rc, d = run(FR[:1], [], tmp, curated=FR[:1])
    check("it appears once", d["openers"], FR[:1])
    check("and stays asked, not curated", d["curated"], [])
    rc, d = run([], FR[:1], tmp, curated=FR[:1])
    check("curated beats written for the same string", d["curated"], FR[:1])
    check("and it is not double-counted", d["written"], [])

    print("\n\033[1m== curated questions obey the per-language cap too\033[0m")
    # Five curated French for four buttons: the cap is the merge's, and a
    # source that ignored it would render a panel of five French questions.
    rc, d = run([], [], tmp, curated=FR[:5])
    check("four survive", len(d["openers"]), 4)
    check("all of them curated", len(d["curated"]), 4)

    print("\n\033[1m== no --curated is the old behaviour, exactly\033[0m")
    # The same script joins the written half's two languages, a call that has
    # no third source. Breaking that signature breaks a path nothing else
    # covers.
    rc, d = run(FR[:1], FR[1:2], tmp)
    check("exit 0 without the flag", rc, 0)
    check("curated is present and empty", d["curated"], [])
    check("written is unchanged", d["written"], FR[1:2])

    print("\n\033[1m== the timestamp is the caller's, not the clock's\033[0m")
    rc, d = run(FR[:1], [], tmp)
    check("stamped as given", d["generated"], "2026-09-15T04:30:00Z")

print(f"\n\033[1m{passed} passed, {failed} failed\033[0m")
sys.exit(1 if failed else 0)
