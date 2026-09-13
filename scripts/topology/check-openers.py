#!/usr/bin/env python3
"""Gate the suggested questions before any visitor sees them.

Usage: check-openers.py <openers.json> <candidates.json>

These are the only strings on this site that a stranger wrote. Everything else
— articles, diagrams, Bob's own answers — is either authored here or derived
from data that is. So this file is the whole trust boundary, and it is
deliberately paranoid: over-rejecting costs one fewer suggestion, and
under-rejecting puts someone else's words on a page with Ludo's name on it.

Four rules, in the order they matter:

1. **Verbatim.** Every published question must appear character-for-character
   in the candidate list the Worker produced. The session selects; it does not
   write, improve or merge. A question nobody asked cannot get through, and
   neither can a real question with a word quietly changed.
2. **Shape.** A question, in the length a button can hold, ending in a question
   mark, no newlines, no markup, no addresses.
3. **Vocabulary.** A blocklist of the obvious, because "obscene" has no
   mechanical definition and pretending otherwise would be worse than saying
   what this actually checks.
4. **Volume.** At most four PER LANGUAGE, eight in all. The panel shows one
   language at a time — a visitor sees the four buttons that match their
   browser — so a night that picked eight English questions would leave every
   French visitor with the hand-written fallbacks. The split is checked here
   rather than trusted: the session is asked for a balance, and this is what
   makes the ask real.

What this cannot do is judge intent. A perfectly clean sentence can still be
someone using the suggestion slot as a billboard. That is why the session that
selects has instructions to reject anything that is not a question about this
homelab, why the result is a commit rather than a live write, and why the
commit is small enough to read.
"""
import json
import re
import sys

MAX_OPENERS = 8
MAX_PER_LANG = 4
# floor per language, applied only when the candidates make it possible
MIN_PER_LANG = 2
MIN_TO_EXPECT = 3
MIN_LEN, MAX_LEN = 12, 70

# The same two word lists as the Worker and as BobTerminal.astro: function
# words, majority wins, French on a tie because French is the house. Coarse on
# purpose — a question is short — and used here only to check the BALANCE, not
# to decide anything a visitor reads. The panel sorts them again at build time
# with the same rule, so what this counts is what will be shown.
FR_WORDS = re.compile(
    r"\b(le|la|les|un|une|des|du|est|pas|que|qui|pour|dans|avec|c'est|ça|mais|tu|je|sur"
    r"|au|aux|ce|son|sa|et|moi|toi|tes|mes|ses|ne|comment|pourquoi|quoi|sans|chez|vers"
    r"|entre|depuis|maintenant|ton|ta|quel|quels|quelle)\b",
    re.IGNORECASE,
)
EN_WORDS = re.compile(
    r"\b(the|and|you|is|are|that|this|with|for|it|he|she|got|there|was|but|of|to|my"
    r"|your|not|what|do|did|how|why|where|which)\b",
    re.IGNORECASE,
)


def looks_english(q):
    return len(EN_WORDS.findall(q)) > len(FR_WORDS.findall(q))

# Deliberately short and blunt. This is a coarse net for the unmistakable; the
# session's judgment and the commit review are what catch everything subtler.
BLOCKED = re.compile(
    r"\b(fuck|shit|bitch|cunt|nigg|faggot|rape|porn|xxx|viagra|casino|crypto\s*giveaway"
    r"|osti|tabarnak|calisse|criss|estie|salope|encul)",
    re.IGNORECASE,
)
ADDRESSY = re.compile(r"(https?://|www\.|@|\+?\d[\d\s().-]{6,})", re.IGNORECASE)
MARKUP = re.compile(r"[<>{}\[\]\\|`]")
# words that carry no subject on their own, in either language
STOPWORDS = {"have", "link", "another", "there", "which", "what", "when", "does", "dont", "don't",
             "about", "some", "more", "other", "quoi", "c'est", "cest", "est-ce", "as-tu", "t'as",
             "tas", "encore", "autre", "plus", "avez", "vous", "quel", "quelle", "quels", "quelles",
             "comment", "pourquoi", "quand", "combien", "peux", "peut", "fait", "faire", "roules", "rouler"}


def fail(msg):
    print(f"check-openers: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print("usage: check-openers.py <openers.json> <candidates.json>", file=sys.stderr)
        sys.exit(1)

    openers = json.load(open(sys.argv[1], encoding="utf-8")).get("openers", [])
    candidates = json.load(open(sys.argv[2], encoding="utf-8")).get("candidates", [])
    allowed = {c["text"] for c in candidates if isinstance(c, dict) and "text" in c}

    if not isinstance(openers, list):
        fail("openers must be a list")
    if len(openers) > MAX_OPENERS:
        fail(f"{len(openers)} openers, at most {MAX_OPENERS} (four per language)")
    for lang, n in (
        ("english", sum(1 for q in openers if isinstance(q, str) and looks_english(q))),
        ("french", sum(1 for q in openers if isinstance(q, str) and not looks_english(q))),
    ):
        if n > MAX_PER_LANG:
            fail(f"{n} {lang} questions, at most {MAX_PER_LANG} — the panel shows one language at a time")
    if len(set(openers)) != len(openers):
        fail("the same question twice")

    # Balance is a REQUIREMENT when the candidates allow it, not a wish in the
    # prompt: on 2026-09-13 the model returned four English questions and no
    # French one while 24 French candidates sat in the list — the panel showed
    # its hand-written fallbacks to every French visitor while real questions
    # went unused. A language with at least MIN_TO_EXPECT eligible candidates
    # must get at least MIN_PER_LANG openers.
    def eligible(q):
        return (MIN_LEN <= len(q) <= MAX_LEN and q.rstrip().endswith("?")
                and not BLOCKED.search(q) and not ADDRESSY.search(q) and not MARKUP.search(q))
    pool_en = sum(1 for q in allowed if eligible(q) and looks_english(q))
    pool_fr = sum(1 for q in allowed if eligible(q) and not looks_english(q))
    got_en = sum(1 for q in openers if isinstance(q, str) and looks_english(q))
    got_fr = len([q for q in openers if isinstance(q, str)]) - got_en
    for lang, pool, got in (("french", pool_fr, got_fr), ("english", pool_en, got_en)):
        if pool >= MIN_TO_EXPECT and got < MIN_PER_LANG:
            fail(f"only {got} {lang} question(s) while {pool} eligible {lang} candidates exist — "
                 f"pick at least {MIN_PER_LANG} in {lang}")

    for q in openers:
        if not isinstance(q, str):
            fail(f"not a string: {q!r}")
        if q not in allowed:
            fail(f"{q!r} is not verbatim in the candidates — selected, not written, is the rule")
        if not (MIN_LEN <= len(q) <= MAX_LEN):
            fail(f"{q!r} is {len(q)} chars, outside {MIN_LEN}–{MAX_LEN}")
        if "\n" in q:
            fail(f"{q!r} contains a newline")
        if not q.rstrip().endswith("?"):
            fail(f"{q!r} is not a question")
        if BLOCKED.search(q):
            fail(f"{q!r} hits the blocklist")
        if ADDRESSY.search(q):
            fail(f"{q!r} looks like an address or a link")
        if MARKUP.search(q):
            fail(f"{q!r} contains markup characters")

    # Two judgement calls that turned out to be measurable (2026-09-13: the
    # hosted model published "Have a link?" and two variants of the NFS/SSD
    # question). A question that stands alone on a button names something —
    # so it has more than three words and at least one word that is not a
    # function word; and two openers about the same thing are one opener.
    def content_words(q):
        return {w for w in re.findall(r"[\w'’-]+", q.lower())
                if len(w) >= 3 and not FR_WORDS.fullmatch(w) and not EN_WORDS.fullmatch(w)
                and w not in STOPWORDS}
    for q in openers:
        words = re.findall(r"[\w'’-]+", q)
        if len(words) <= 3 or not content_words(q):
            fail(f"{q!r} does not stand on its own — it names nothing a visitor can recognise")
    seen = []
    for q in openers:
        cw = content_words(q)
        for prev, pcw in seen:
            if len(cw & pcw) >= 2:
                fail(f"{q!r} and {prev!r} are the same question twice (share {sorted(cw & pcw)})")
        seen.append((q, cw))

    en = sum(1 for q in openers if looks_english(q))
    print(
        f"check-openers: ok ({len(openers)} question(s) — {en} en, {len(openers) - en} fr — "
        f"all verbatim from {len(allowed)} candidates)"
    )


if __name__ == "__main__":
    main()
