#!/usr/bin/env python3
"""Build what the generation prompt writes from, and what the gate checks against.

Usage: openers-corpus.py <grounding.json> <kept.json> <content-dir> <out-dir>

Files come out for two readers that need different things:

  corpus.json      — small, attached to the prompt: the article index, the
                     fleet names, this morning's real questions, and how many
                     are missing per language.
  corpus-fr.json   — the same, asking for French only.
  corpus-en.json   — the same, asking for English only.
  vocabulary.json  — ~14k words, never shown to a model: every word the site
                     actually publishes, per language, from the article bodies.

ONE LANGUAGE PER CALL is why the two single-language variants exist. Asked for
both at once, the model on 2026-09-15 wrote four good French questions and no
English one in three runs out of four — it can write well or satisfy two
simultaneous quotas, not both. Splitting the ask costs a second call of about
three seconds and removes the juggling entirely.

WHY THE BODIES AND NOT THE TITLES. The first version of this built the
vocabulary from titles, slugs and device names, and it refused « Comment
Frigate écrit ses images dans S3 ? » — Frigate is the subject of four articles
and the answer to a suggested question already live on the panel, but the word
appears in no title. A gate that refuses what the site demonstrably documents
is not strict, it is broken. The bodies are also what Bob's own retrieval
searches, so the two agree by construction.

`kept.json` is what survived the real-question path this morning. What comes
out is the gap, per language, capped at the panel's four buttons: a morning
where four real French questions survived asks for zero French. The generated
ones fill a gap; they never compete with a question somebody really asked.
"""
import json
import os
import pathlib
import re
import sys

TARGET = 4
WORD = re.compile(r"[\w'’-]+")

# The site's own layout: the English tree is what an English question may draw
# on, everything is what a French one may.
FR_DIRS = ["blog", "casts", "pages"]
EN_DIRS = ["blog-en", "casts-en"]


def _load_openers_module():
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("co", os.path.join(here, "check-openers.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def words_under(root, names):
    bag = set()
    for name in names:
        d = pathlib.Path(root) / name
        if not d.is_dir():
            continue
        for f in d.rglob("*.md*"):
            try:
                bag |= set(WORD.findall(f.read_text(encoding="utf-8").lower()))
            except OSError:
                continue
    return bag


def parse_table(block, fields):
    """The grounding ships its tables as pipe-delimited lines with a header
    naming the columns, so the shape is read from the data rather than assumed:
    a column added upstream shifts nothing here."""
    names = [f.strip() for f in (fields or "").split("|")]
    rows = []
    for line in (block or "").splitlines():
        if not line.strip():
            continue
        parts = line.split("|")
        rows.append({names[i]: parts[i].strip() for i in range(min(len(names), len(parts)))})
    return rows


def main():
    if len(sys.argv) != 5:
        print("usage: openers-corpus.py <grounding.json> <kept.json> <content-dir> <out-dir>",
              file=sys.stderr)
        return 1
    grounding_path, kept_path, content_dir, out_dir = sys.argv[1:5]

    grounding = json.load(open(grounding_path, encoding="utf-8"))
    try:
        kept = [q for q in json.load(open(kept_path, encoding="utf-8")).get("openers", [])
                if isinstance(q, str)]
    except (OSError, ValueError):
        kept = []

    rows = parse_table(grounding.get("corpus"), grounding.get("corpusFields"))
    articles = [
        {"slug": r.get("slug", ""), "date": r.get("date", ""),
         "title": r.get("title", ""), "en": bool(r.get("en"))}
        for r in rows if r.get("kind") == "article" and r.get("slug")
    ]
    # The fleet arrives as prose lines; the name is the part a question could
    # legitimately quote, and the specification after it is not.
    fleet = [line.split("|")[0].strip()
             for line in (grounding.get("fleet") or "").splitlines() if line.strip()]

    fr_words = words_under(content_dir, FR_DIRS)
    en_words = words_under(content_dir, EN_DIRS)
    if len(fr_words) < 500:
        print(f"openers-corpus: only {len(fr_words)} French words found under "
              f"{content_dir} — refusing to build a vocabulary that would pass "
              "almost nothing", file=sys.stderr)
        return 1
    fleet_words = set()
    for name in fleet:
        fleet_words |= set(WORD.findall(name.lower())) | {name.lower()}

    co = _load_openers_module()
    have_en = sum(1 for q in kept if co.looks_english(q))
    have_fr = len(kept) - have_en
    need = {"fr": max(0, TARGET - have_fr), "en": max(0, TARGET - have_en)}
    if not any(a["en"] for a in articles):
        need["en"] = 0

    os.makedirs(out_dir, exist_ok=True)
    corpus = {
        "articles": articles,
        "fleet": fleet,
        "taken": kept,
        "need": need,
        "generated": grounding.get("generated"),
    }
    def write(name, doc):
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2)
            fh.write("\n")

    write("corpus.json", corpus)
    write("corpus-fr.json", {**corpus, "need": {"fr": need["fr"], "en": 0}})
    write("corpus-en.json", {**corpus, "need": {"fr": 0, "en": need["en"]}})
    with open(os.path.join(out_dir, "vocabulary.json"), "w", encoding="utf-8") as fh:
        json.dump({"fr": sorted(fr_words | fleet_words),
                   "en": sorted(en_words | fleet_words)}, fh, ensure_ascii=False)
        fh.write("\n")

    print(f"openers-corpus: {len(articles)} article(s), {len(fleet)} device(s), "
          f"{len(fr_words)} fr / {len(en_words)} en words; "
          f"kept {have_fr} fr + {have_en} en, need {need['fr']} fr + {need['en']} en")
    # Nothing missing is a good morning, and the caller skips the model call
    # entirely rather than asking for zero questions.
    return 0 if (need["fr"] or need["en"]) else 3


if __name__ == "__main__":
    sys.exit(main())
