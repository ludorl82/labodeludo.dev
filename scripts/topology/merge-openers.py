#!/usr/bin/env python3
"""Assemble the panel from its two sources, and record which is which.

Usage: merge-openers.py <kept.json> <written.json> <out.json> <timestamp>

The suggested questions come from two places now: questions visitors really
asked, gated verbatim, and questions Bob wrote to fill the buttons those leave
empty, gated against the vocabulary of the published articles. Each half is
checked on its own terms, so the only things decided here are the three that
belong to neither half.

**Real questions come first.** A question somebody actually asked is evidence
about what people want to know; a written one is a guess, however well
grounded. When both are available for the same slot, the evidence wins.

**The per-language cap applies to the MERGE.** Each gate caps its own output,
and nothing else stands between two capped halves and a panel of eight French
buttons. The panel shows one language at a time, four at a time.

**`written` says which ones Bob wrote.** No visitor can tell, and no visitor
needs to — but the whole pipeline rests on the claim that these are real
questions published verbatim, and that claim stops being true for the file the
day this list is non-empty. Writing it down is what keeps the commit message
honest, and it costs one array.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _openers_gate():
    spec = importlib.util.spec_from_file_location(
        "co", os.path.join(HERE, "check-openers.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load(path):
    """A missing or unreadable half is an empty half, not a crash.

    Either half legitimately produces nothing — a quiet fortnight, a morning
    where the panel was already full — and the caller runs them independently
    so that one failing never takes the other down with it.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            return [q for q in json.load(fh).get("openers", []) if isinstance(q, str)]
    except (OSError, ValueError, AttributeError):
        return []


def merge(real, written, max_per_lang, looks_english):
    out, per = [], {True: 0, False: 0}
    for q in list(real) + list(written):
        if q in out:
            continue
        en = looks_english(q)
        if per[en] >= max_per_lang:
            continue
        per[en] += 1
        out.append(q)
    return out


def main():
    if len(sys.argv) != 5:
        print("usage: merge-openers.py <kept.json> <written.json> <out.json> <timestamp>",
              file=sys.stderr)
        return 1
    kept_p, written_p, out_p, stamp = sys.argv[1:5]
    co = _openers_gate()

    real, written = load(kept_p), load(written_p)
    out = merge(real, written, co.MAX_PER_LANG, co.looks_english)
    doc = {"generated": stamp, "openers": out,
           "written": [q for q in out if q in written and q not in real]}

    with open(out_p, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")

    en = sum(1 for q in out if co.looks_english(q))
    print(f"merge-openers: {len(out)} question(s) — {en} en, {len(out) - en} fr; "
          f"{len(real)} asked, {len(doc['written'])} written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
