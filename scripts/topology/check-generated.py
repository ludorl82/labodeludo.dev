#!/usr/bin/env python3
"""Gate the suggested questions Bob writes himself.

Usage: check-generated.py <openers.json> <corpus.json> <vocabulary.json>

WHY A SECOND GATE. check-openers.py rests on one rule that does all the work:
a published question must appear character-for-character in the list of what
visitors actually asked. The session selects, it never writes. That rule is the
trust boundary, because those are the only strings on this site a stranger
wrote.

When too few real questions survive, the panel falls back to four sentences
hand-written in July — already invented content, just frozen, and steadily
less true as the site moves. Generating them instead removes the verbatim rule,
and with it the risk it guarded: a question Bob wrote is his own words on his
own site, so there is no stranger's billboard to fear.

What replaces it is the opposite risk. The verbatim rule made invention
impossible; without it, invention is the ONLY failure mode left. So this gate
checks the thing check-openers never had to: that what the question names
actually exists.

FOUR RULES, in the order they matter:

1. **Grounding.** EVERY word carrying subject matter must be a word this site
   actually publishes, and the vocabulary is built from the article bodies —
   the same text Bob's own retrieval searches. « Pourquoi avoir quitté
   Proxmox ? » is refused because "proxmox" appears in none of the sixty
   articles; « Comment Frigate écrit ses images dans S3 ? » passes because
   Frigate is the subject of four. Every word, not merely one: with a
   body-sized vocabulary an "at least one" rule is satisfied by the ordinary
   French around the invented noun, which is precisely the case that matters.

   This proves EXISTENCE and nothing more. A well-formed question about
   something real that Bob still cannot answer passes here, and
   check-answerable.py is what removes it. Two gates, because a string check
   that tried to judge answerability would be the keyword check this project
   has already been burned by four times in one night.
2. **English is checked against the English tree only.** An English question
   may only use words from `blog-en`/`casts-en` and the fleet names. Sending an
   English visitor toward an article that exists only in French is the same
   dead end this panel exists to avoid, one step further along.
3. **Shape and volume**, imported wholesale from check-openers.py rather than
   restated: the length a button holds, the question mark, the blocklist, the
   four-per-language cap, and its definition of two questions being the same
   question. One definition, two callers.
4. **Not the prompt's own examples.** On 2026-09-13 the model handed the other
   prompt its own counter-example back as a suggestion — the false premise it
   was being shown in order to reject it. A prompt that teaches by example can
   have its examples published, so every example in openers-generate.md is
   refused by name.

It also refuses two things a reading of the output showed the model doing:

  * repeating one of this morning's real questions — the written list FILLS a
    gap, so a near-duplicate of one somebody actually asked is a wasted button;
  * handing back an article TITLE with a question mark on it. « Quand personne
    ne joue le cluster ramasse les cartes ? » is a headline, not something a
    visitor would type, and « Comment j'ai appris à chercher sur internet ? »
    is a headline in Bob's own first person — the prompt asks for the visitor's
    voice and the gate can check the clearest half of that: a question that is
    a run of words lifted out of a title.
"""
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"),
                                                  os.path.join(HERE, name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The shape rules, the language split and the duplicate rule all live in
# check-openers.py and are imported, never restated. If the button gets wider,
# it gets wider for both sources on the same day.
CO = _load("check-openers.py")

PROMPT = os.path.join(HERE, "prompts", "openers-generate.md")

# Hostname-shaped tokens, the same net check-dispatch.py casts over the nightly
# dispatch: kebab-case, or letters followed by digits. These are how hosts,
# nodes and article slugs are named here, so this is where an invented name
# would show up looking exactly like a real one.
NAMEISH = re.compile(r"\b(?:[a-z][a-z0-9]*(?:-[a-z0-9]+)+|[a-z]{2,}[0-9]+)\b")

# French hyphenates its inverted questions, and that looks exactly like a
# kebab-case hostname: « Comment Bob a-t-il réglé ça ? » was refused on
# 2026-09-15 for naming a machine called `a-t-il`. These are the pronouns that
# can follow the hyphen — a closed grammatical set, not an open vocabulary, so
# stripping them opens no hole: `gpu-01` has no pronoun to strip and stays
# whole.
CLITIC = re.compile(
    r"-(?:t-)?(?:il|elle|on|ils|elles|je|tu|nous|vous|ce|ci|là|la|le|les|moi|toi|y|en)$",
    re.IGNORECASE)


def destress(word):
    """`a-t-il` -> `a`; `gpu-01` -> `gpu-01`. Applied only when the whole token
    is unknown, so it can rescue French grammar without excusing a hostname."""
    prev = None
    while prev != word:
        prev, word = word, CLITIC.sub("", word)
    return word

# Words too common to prove anything about grounding. A question containing
# only these names nothing, whatever the corpus happens to contain.
UNREVEALING = {"article", "articles", "question", "questions", "site", "blogue",
               "blog", "page", "pages", "post", "posts", "chose", "choses",
               "truc", "trucs", "affaire", "affaires", "thing", "things",
               "stuff", "setup", "machine", "machines"}


# The visitor asks about Ludo's lab, so « mes sessions » and "my sessions" are
# Ludo's words, not a visitor's. On 2026-09-26 the 27B wrote exactly that in
# two tries out of eight, with the prompt telling it not to; a rule it cannot
# talk its way past is the fix, and the driver's one correction round lets it
# rewrite the question in the visitor's voice.
FIRST_PERSON = re.compile(r"(?<![\w'’-])(?:mes|mon|ma|my|mine)(?![\w'’-])", re.IGNORECASE)
PUNCT = re.compile(r"[^\w\s]", re.UNICODE)


def flatten(text):
    """Lowercase, punctuation gone, spaces collapsed — so a title and a question
    lifted out of it compare equal where they overlap."""
    return " ".join(PUNCT.sub(" ", text.lower()).split())


def fail(msg):
    print(f"check-generated: {msg}", file=sys.stderr)
    sys.exit(1)


def load_vocabulary(path):
    """Read the word lists openers-corpus.py computed from the article bodies.

    Computed there rather than here, and from the content rather than from a
    hand-kept list, for the same reason check-dispatch.py computes its
    vocabulary from the diff: a list maintained by hand goes stale in the
    direction that opens holes, and every entry added to it is one more thing
    the gate stops checking.
    """
    v = json.load(open(path, encoding="utf-8"))
    fr, en = set(v.get("fr", [])), set(v.get("en", []))
    if len(fr) < 500 or len(en) < 200:
        fail(f"the vocabulary is too small to check anything ({len(fr)} fr, {len(en)} en)")
    return fr, en


def prompt_examples():
    """The example questions in the generation prompt, so none can be published.

    They live in a Markdown table whose first column is a backticked string,
    plus any backticked line ending in a question mark. Read from the file
    rather than copied here: an example added to the prompt is guarded the day
    it is written, not the day someone remembers to update this list.
    """
    try:
        text = open(PROMPT, encoding="utf-8").read()
    except OSError:
        return set()
    return {m.strip() for m in re.findall(r"`([^`\n]{8,120})`", text)
            if m.strip().endswith(("?", "!", "."))}


def main():
    if len(sys.argv) != 4:
        print("usage: check-generated.py <openers.json> <corpus.json> <vocabulary.json>",
              file=sys.stderr)
        sys.exit(1)

    doc = json.load(open(sys.argv[1], encoding="utf-8"))
    corpus = json.load(open(sys.argv[2], encoding="utf-8"))
    openers = doc.get("openers", [])

    if not isinstance(openers, list):
        fail("openers must be a list")
    if not all(isinstance(q, str) for q in openers):
        fail("every opener must be a string")
    if len(set(openers)) != len(openers):
        fail("the same question twice")

    need = corpus.get("need") or {}
    taken = [t for t in corpus.get("taken", []) if isinstance(t, str)]

    got_en = [q for q in openers if CO.looks_english(q)]
    got_fr = [q for q in openers if not CO.looks_english(q)]

    # AT MOST what was asked for, in each language. Over-delivering is not
    # generosity: the panel shows four buttons per language, the real questions
    # already hold some of them, and an extra written one would push a genuine
    # question off the page.
    #
    # Under-delivering is allowed, and that is a correction. Demanding an EXACT
    # count failed five generation runs out of five on 2026-09-15 — the model
    # can write good questions or hit two simultaneous quotas, not both, and
    # every one of those runs was refused for arithmetic while the questions
    # themselves were fine. A shorter panel is a smaller panel; a panel of
    # invented junk is a broken one, and only the second is worth failing over.
    for lang, got in (("french", got_fr), ("english", got_en)):
        want = int(need.get(lang[:2], 0))
        if len(got) > want:
            fail(f"{len(got)} {lang} question(s), at most {want} asked for")
    if not openers:
        fail("no question at all — nothing to publish")

    vocab_all, vocab_en = load_vocabulary(sys.argv[3])

    examples = prompt_examples()
    taken_words = [(t, CO.content_words(t)) for t in taken]

    seen = []
    for q in openers:
        if not CO.eligible(q):
            fail(f"{q!r} fails the shape rules shared with check-openers "
                 f"(length {CO.MIN_LEN}–{CO.MAX_LEN}, ends in '?', no markup or addresses)")
        words = re.findall(r"[\w'’-]+", q)
        cw = CO.content_words(q)
        if len(words) <= 3 or not cw:
            fail(f"{q!r} does not stand on its own — it names nothing a visitor can recognise")

        if FIRST_PERSON.search(q):
            fail(f"{q!r} speaks as the lab's owner (« mes », 'my') — a visitor asks "
                 "Bob about HIS lab: « ton SSH », 'your sessions'")

        if q.strip() in examples:
            fail(f"{q!r} is an example from openers-generate.md, not a question — "
                 "the prompt teaches by example and its examples are not for publishing")

        english = CO.looks_english(q)
        vocab = vocab_en if english else vocab_all

        where = "the English articles" if english else "the articles"

        # One rule, one pass: every word that carries subject matter must be a
        # word the site publishes. An earlier version ran a separate loop over
        # machine-shaped tokens first; a mutation test showed the loop could be
        # deleted without a single test noticing, because this check already
        # covers it — `gpu-99` is an unknown word like any other. What the
        # separate loop was really buying was a clearer sentence, so that is
        # all that survives of it.
        unknown = sorted(w for w in cw
                         if w not in vocab and w not in UNREVEALING
                         and destress(w) not in vocab)
        if unknown:
            nameish = [w for w in unknown if NAMEISH.fullmatch(w)]
            if nameish:
                fail(f"{q!r} names {nameish[0]!r}, which appears nowhere in "
                     f"{where} — no such machine, article or tool here")
            fail(f"{q!r} uses {unknown!r}, which {where} never use — a question "
                 "about something this site never published leads straight to "
                 "« ça, c'est pas documenté »")

        # A title with a question mark is a headline, not a question. Checked
        # as containment rather than by counting shared words: a good question
        # about an article legitimately shares its nouns — « Comment déployer
        # un cluster k3s avec Claude Code en mode headless ? » shares four with
        # its article and is fine — while a recycled headline is the title's
        # own words in the title's own order.
        flat_q = flatten(q)
        for art in corpus.get("articles", []):
            flat_t = flatten(art.get("title", ""))
            if flat_t and flat_q in flat_t:
                fail(f"{q!r} is the title of {art.get('slug')!r} with a question mark "
                     "on it — a headline, not something a visitor would type")

        # Same subject as a real question already chosen this morning.
        for t, tcw in taken_words:
            if CO.looks_english(t) == english and len(cw & tcw) >= 2:
                fail(f"{q!r} repeats a real question already chosen ({t!r}) — "
                     "the generated ones fill the gap, they do not compete")

        # Same subject twice inside this batch. Same rule, same code.
        for prev, pcw in seen:
            if CO.looks_english(prev) == english and len(cw & pcw) >= 2:
                fail(f"{q!r} and {prev!r} are the same question twice (share {sorted(cw & pcw)})")
        seen.append((q, cw))

    print(f"check-generated: ok ({len(openers)} written — {len(got_en)} en, {len(got_fr)} fr — "
          f"all grounded in {len(vocab_all)} corpus words, none repeating "
          f"{len(taken)} real question(s))")


if __name__ == "__main__":
    main()
