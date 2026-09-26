#!/usr/bin/env python3
"""Assemble the panel from its sources, and record which is which.

Usage: merge-openers.py [--fresh <fresh.json>] [--curated <curated.json>]
                        <kept.json> <written.json> <out.json> <timestamp>

The suggested questions come from three places: questions visitors really
asked, gated verbatim; questions Ludo curated by hand, gated only on whether
Bob can still answer them; and questions Bob wrote to fill what those leave
empty, gated against the vocabulary of the published articles. Each source is
checked on its own terms, so the only things decided here are the ones that
belong to none of them.

**Precedence: asked, then curated, then written.** A question somebody
actually asked is evidence about what people want to know. A curated one is a
person's judgement, which beats a guess. A written one is a guess, however
well grounded. When two sources offer a slot, the stronger claim wins.

**`--fresh` sits between asked and curated** (2026-09-26): a question Bob
wrote about an article published this week. Curated questions filled every
free button from 2026-09-20 on, so without a slot of its own a new article
never reached the panel unless a visitor asked about it first. It is still a
written question, gated the same way, and listed in `written` with the others.

`--curated` is optional and the positional form is unchanged, because this
same script also joins the written half's two languages — a call that has no
third source and must keep working.

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


def merge(real, written, max_per_lang, looks_english, curated=(), fresh=()):
    out, per = [], {True: 0, False: 0}
    for q in list(real) + list(fresh) + list(curated) + list(written):
        if q in out:
            continue
        en = looks_english(q)
        if per[en] >= max_per_lang:
            continue
        per[en] += 1
        out.append(q)
    return out


def main():
    argv = sys.argv[1:]
    opt = {}
    for flag in ("--curated", "--fresh"):
        if flag in argv:
            i = argv.index(flag)
            try:
                opt[flag] = argv[i + 1]
            except IndexError:
                print(f"merge-openers: {flag} needs a path", file=sys.stderr)
                return 1
            del argv[i:i + 2]
    curated_p, fresh_p = opt.get("--curated"), opt.get("--fresh")
    if len(argv) != 4:
        print("usage: merge-openers.py [--fresh <f>] [--curated <f>] <kept.json> "
              "<written.json> <out.json> <timestamp>", file=sys.stderr)
        return 1
    kept_p, written_p, out_p, stamp = argv
    co = _openers_gate()

    real, written = load(kept_p), load(written_p)
    curated = load(curated_p) if curated_p else []
    fresh = load(fresh_p) if fresh_p else []
    out = merge(real, written, co.MAX_PER_LANG, co.looks_english, curated, fresh)
    # Labels are assigned by PRECEDENCE, not by membership: the same string can
    # sit in two lists (a visitor may well ask what Ludo curated), and calling
    # it curated then would quietly shrink the count of real questions the
    # whole pipeline rests on. First source to claim it, keeps it.
    doc = {"generated": stamp, "openers": out,
           "curated": [q for q in out if q in curated and q not in real
                       and q not in fresh],
           "written": [q for q in out if q not in real
                       and (q in fresh or (q in written and q not in curated))]}

    with open(out_p, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")

    en = sum(1 for q in out if co.looks_english(q))
    print(f"merge-openers: {len(out)} question(s) — {en} en, {len(out) - en} fr; "
          f"{len(real)} asked, {len(doc['curated'])} curated, "
          f"{len(doc['written'])} written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
