#!/usr/bin/env python3
"""Tests for openers-curated.py — which slice of Ludo's list ships tonight.

This source runs no model, so everything it decides is decided here: the
rotation, the per-language cap, and what it does when the list is shorter than
the panel or missing altogether. Each of those fails quietly if it is wrong —
a rotation stuck on its first element renders a perfectly good panel that
never changes, and nothing goes red.

  python3 scripts/topology/tests/test-openers-curated.py
"""
import datetime
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PICK = HERE.parent / "openers-curated.py"

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  \033[32mok\033[0m   {label}")
    else:
        failed += 1
        print(f"  \033[31mFAIL\033[0m {label}: got {got!r}, wanted {want!r}")


def run(doc, tmp, per_lang=4, offset=0, write=True):
    d = pathlib.Path(tmp)
    src = d / "curated.json"
    if write:
        src.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    else:
        src.unlink(missing_ok=True)
    out = d / "out.json"
    out.unlink(missing_ok=True)
    r = subprocess.run([sys.executable, str(PICK), str(src), str(out),
                        str(per_lang), str(offset)], capture_output=True, text=True)
    got = json.loads(out.read_text(encoding="utf-8"))["openers"] if out.exists() else None
    return r.returncode, got


FR = [f"Question française numéro {i} ?" for i in range(6)]
EN = [f"English question number {i}?" for i in range(6)]

with tempfile.TemporaryDirectory() as tmp:
    print("\033[1m== the slice moves with the day\033[0m")
    rc, day0 = run({"fr": FR, "en": EN}, tmp, 2, 0)
    check("exit 0", rc, 0)
    check("two per language", len(day0), 4)
    _, day1 = run({"fr": FR, "en": EN}, tmp, 2, 1)
    check("a different slice tomorrow", day1 != day0, True)
    _, day0_again = run({"fr": FR, "en": EN}, tmp, 2, 0)
    check("and the same slice for the same day", day0_again, day0)

    print("\n\033[1m== the rotation wraps, and never repeats inside one slice\033[0m")
    # Offset past the end must wrap rather than run out, or the last days of
    # every cycle would ship a short panel.
    _, wrapped = run({"fr": FR[:3], "en": []}, tmp, 3, 2)
    check("three from a three-item list", len(wrapped), 3)
    check("all distinct", len(set(wrapped)), 3)
    check("starting where asked", wrapped[0], FR[2])

    print("\n\033[1m== a list shorter than the panel gives what it has\033[0m")
    # Not an error: the other two sources fill the rest, which is the whole
    # point of having three.
    rc, short = run({"fr": FR[:2], "en": []}, tmp, 4, 0)
    check("exit 0", rc, 0)
    check("two questions, not four", len(short), 2)
    check("and no duplicates to pad it out", len(set(short)), 2)

    print("\n\033[1m== each language is capped on its own\033[0m")
    _, both = run({"fr": FR, "en": EN}, tmp, 4, 0)
    check("four French", len([q for q in both if "française" in q]), 4)
    check("four English", len([q for q in both if "English" in q]), 4)

    print("\n\033[1m== an empty or missing list is a normal state\033[0m")
    rc, empty = run({"fr": [], "en": []}, tmp, 4, 0)
    check("empty list: exit 0", rc, 0)
    check("and an empty panel share", empty, [])
    rc, gone = run(None, tmp, 4, 0, write=False)
    check("missing file: exit 0", rc, 0)
    check("and still writes a valid file", gone, [])

    print("\n\033[1m== junk entries are dropped, not shipped\033[0m")
    rc, mixed = run({"fr": ["Vraie question ?", "", "   ", None, 42], "en": []}, tmp, 4, 0)
    check("only the real one survives", mixed, ["Vraie question ?"])

    print("\n\033[1m== the day key is the ordinal date\033[0m")
    # Reproducible from the date alone: two machines the same night agree, and
    # a re-run the same day is idempotent.
    sys.path.insert(0, str(PICK.parent))
    import importlib.util
    spec = importlib.util.spec_from_file_location("oc", PICK)
    oc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oc)
    check("today", oc.day_offset(datetime.date(2026, 9, 16)),
          datetime.date(2026, 9, 16).toordinal())
    check("tomorrow is exactly one more",
          oc.day_offset(datetime.date(2026, 9, 17)) -
          oc.day_offset(datetime.date(2026, 9, 16)), 1)

print(f"\n\033[1m{passed} passed, {failed} failed\033[0m")
sys.exit(1 if failed else 0)
