#!/usr/bin/env python3
"""Tests for check-generated.py and openers-corpus.py — the questions Bob writes.

check-openers.py can lean on one rule that settles everything: the question must
appear verbatim in what visitors asked. These two files exist because that rule
is gone, so what replaces it is what gets tested here — that a question naming
something this site never published cannot reach the panel.

Everything is offline and self-contained: a small fake content tree stands in
for the articles, so the vocabulary under test is one this file states outright
rather than whatever the repository happens to contain today. A fixture more
generous than production tests nothing at the point where it is generous, so
the fake tree is deliberately SMALLER than the real one — a question that
passes here would pass there.

  python3 scripts/topology/tests/test-check-generated.py
"""
import importlib.util
import itertools
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
GATE = HERE.parent / "check-generated.py"
CORPUS = HERE.parent / "openers-corpus.py"

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  \033[32mok\033[0m   {label}")
    else:
        failed += 1
        print(f"  \033[31mFAIL\033[0m {label}: got {got!r}, wanted {want!r}")


# --------------------------------------------------------------------------
# A fake site: two French articles, one English, one device.
# --------------------------------------------------------------------------
FR_BODY = """---
title: "Frigate et la carte graphique"
---
Frigate enregistre ses images sur le stockage objet. Le cluster k3s roule sur
gpu-02 et le modèle Ollama garde la mémoire vive occupée. La dépêche du matin
raconte ce qui a bougé dans le parc. Comment écrire un article ? Le cluster a
douze nœuds quand tout le monde est debout, non ?
"""
EN_BODY = """---
title: "Frigate and the graphics card"
---
Frigate records its snapshots on object storage. The k3s cluster runs on gpu-02
and the Ollama model keeps the memory busy. How does the cluster share a card?
"""

GROUNDING = {
    "generated": "2026-09-15T04:30:00Z",
    "corpusFields": "kind|slug|date|title|en",
    "corpus": "\n".join([
        "article|frigate-et-la-carte|2026-09-01|Frigate et la carte graphique|en",
        "article|la-depeche-du-matin|2026-09-02|La dépêche du matin|",
    ]),
    "fleet": "gpu-02 | gpu-node | vlan10\nap-01 | access-point | vlan50",
}


# openers-corpus.py refuses a vocabulary under 500 words, because a content
# directory that moved or came back empty would otherwise produce a gate that
# passes nothing — a real failure worth keeping. Padding is what satisfies that
# floor here, and it is inert on purpose: every token below is nonsense no test
# ever puts in a question, so it changes no verdict. The words that decide
# anything are the ones written out in FR_BODY and EN_BODY above.
PADDING = " ".join(f"remplissage{i:04d}" for i in range(700))


# Every build gets its own directory. They used to share one, so a later call
# silently rewrote the corpus an earlier handle still pointed at — which made
# the thin-vocabulary probe a duplicate of someone else's "taken" question and
# hid a deleted guard behind the wrong refusal. Found by mutation, not by the
# suite passing.
_builds = itertools.count()


def build(kept, tmp, extra=()):
    """Run openers-corpus.py over the fake tree; return (corpus, vocab) paths."""
    root = pathlib.Path(tmp) / f"build{next(_builds)}"
    content = root / "content"
    for sub, body in (("blog", FR_BODY), ("casts", FR_BODY), ("pages", FR_BODY),
                      ("blog-en", EN_BODY), ("casts-en", EN_BODY)):
        (content / sub).mkdir(parents=True, exist_ok=True)
        (content / sub / "a.md").write_text(body + "\n" + PADDING, encoding="utf-8")
    (root / "grounding.json").write_text(json.dumps(GROUNDING), encoding="utf-8")
    (root / "kept.json").write_text(json.dumps({"openers": kept}), encoding="utf-8")
    r = subprocess.run([sys.executable, str(CORPUS), *extra, str(root / "grounding.json"),
                        str(root / "kept.json"), str(content), str(root / "out")],
                       capture_output=True, text=True)
    return r, root / "out" / "corpus.json", root / "out" / "vocabulary.json"


def gate(openers, corpus_path, vocab_path, need=None, tmp=None):
    """Run the gate on a list of questions; return its exit code."""
    p = pathlib.Path(tmp) / "openers.json"
    p.write_text(json.dumps({"openers": openers}, ensure_ascii=False), encoding="utf-8")
    cp = corpus_path
    if need is not None:
        c = json.loads(corpus_path.read_text(encoding="utf-8"))
        c["need"] = need
        cp = pathlib.Path(tmp) / "corpus.json"
        cp.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
    r = subprocess.run([sys.executable, str(GATE), str(p), str(cp), str(vocab_path)],
                       capture_output=True, text=True)
    return r.returncode


with tempfile.TemporaryDirectory() as tmp:
    real = ["Quels articles parlent de Kubernetes ?"]
    r, corpus_p, vocab_p = build(real, tmp)

    print("\033[1m== openers-corpus computes the gap, per language\033[0m")
    check("builds both files", r.returncode, 0)
    c = json.loads(corpus_p.read_text(encoding="utf-8"))
    check("one French question kept leaves three missing", c["need"]["fr"], 3)
    check("no English question kept leaves four missing", c["need"]["en"], 4)
    check("the real question is passed along as taken", c["taken"], real)
    check("articles come from the grounding", len(c["articles"]), 2)
    v = json.loads(vocab_p.read_text(encoding="utf-8"))
    check("the French vocabulary has the French body", "dépêche" in v["fr"], True)
    check("the English vocabulary does NOT", "dépêche" in v["en"], False)
    check("device names are in both", "gpu-02" in v["en"], True)

    print("\n\033[1m== a full panel asks for nothing\033[0m")
    full = ([f"Comment Frigate enregistre ses images numéro {i} ?" for i in range(4)]
            + [f"How does Frigate record its snapshots number {i}?" for i in range(4)])
    r2, _, _ = build(full, tmp)
    # four kept in each language -> exit 3, and the caller skips the model call
    check("exit 3 when neither language is short", r2.returncode, 3)
    r2b, c2b, _ = build(full[:4], tmp)
    check("still asks when only English is short", r2b.returncode, 0)
    check("and asks for exactly four English",
          json.loads(c2b.read_text(encoding="utf-8"))["need"], {"fr": 0, "en": 4})
    # rebuild the shared fixture the rest of the file leans on
    r, corpus_p, vocab_p = build(real, tmp)

    print("\n\033[1m== grounding: the rule that replaces verbatim\033[0m")
    ok = lambda q, need=None: gate(q, corpus_p, vocab_p, need, tmp)
    check("a question about something published passes",
          ok(["Comment Frigate enregistre ses images ?"], {"fr": 1, "en": 0}), 0)
    check("an invented product is refused",
          ok(["Est-ce que tu roules Proxmox chez vous ?"], {"fr": 1, "en": 0}), 1)
    check("an invented machine is refused",
          ok(["Ça fait quoi, worker9, dans ton rack ?"], {"fr": 1, "en": 0}), 1)
    check("a real machine passes",
          ok(["Ça fait quoi, gpu-02, dans le cluster ?"], {"fr": 1, "en": 0}), 0)

    print("\n\033[1m== an article title with a question mark is a headline\033[0m")
    # Found by reading the model's output rather than its score: it handed back
    # « Quand personne ne joue le cluster ramasse les cartes ? » and « Comment
    # j'ai appris à chercher sur internet ? », both titles, the second in Bob's
    # own first person. Containment, not shared-word counting: a good question
    # about an article legitimately shares its nouns.
    check("a title with a question mark is refused",
          ok(["Frigate et la carte graphique ?"], {"fr": 1, "en": 0}), 1)
    check("part of a title is refused too",
          ok(["La dépêche du matin ?"], {"fr": 1, "en": 0}), 1)
    check("a real question sharing the title's nouns passes",
          ok(["Comment Frigate enregistre ses images sur le cluster ?"],
             {"fr": 1, "en": 0}), 0)

    print("\n\033[1m== French inversion is grammar, not a hostname\033[0m")
    # `a-t-il` matches the kebab-case pattern that catches `gpu-99`, and a
    # generation run was refused for naming a machine called "a-t-il". The
    # pronouns that can follow the hyphen are a closed set, so stripping them
    # rescues the grammar without excusing an invented name.
    check("an inverted question passes",
          ok(["Frigate enregistre-t-il ses images ?"], {"fr": 1, "en": 0}), 0)
    check("an invented machine still does not",
          ok(["Frigate tourne-t-il sur worker9 ?"], {"fr": 1, "en": 0}), 1)

    print("\n\033[1m== English may not reach into the French-only articles\033[0m")
    check("an English question about a French-only word is refused",
          ok(["What is the dépêche you publish?"], {"fr": 0, "en": 1}), 1)
    check("an English question about an English article passes",
          ok(["How does the cluster share a card?"], {"fr": 0, "en": 1}), 0)

    print("\n\033[1m== shape and volume come from check-openers, not from here\033[0m")
    check("too long for a button",
          ok(["Peux-tu me raconter comment Frigate enregistre ses images sur le stockage objet ?"],
             {"fr": 1, "en": 0}), 1)
    check("not a question", ok(["Frigate enregistre ses images."], {"fr": 1, "en": 0}), 1)
    check("three words naming nothing", ok(["Pis après ça ?"], {"fr": 1, "en": 0}), 1)
    check("more than was asked for",
          ok(["Comment Frigate enregistre ses images ?", "Comment roule le cluster k3s ?"],
             {"fr": 1, "en": 0}), 1)
    # `need` is a ceiling, not a quota. Demanding an exact count failed five
    # generation runs out of five on 2026-09-15: every one was refused for
    # arithmetic while its questions were fine. A shorter panel is a smaller
    # panel; only a panel of invented junk is worth failing over.
    check("fewer than was asked for is fine",
          ok(["Comment Frigate enregistre ses images ?"], {"fr": 2, "en": 0}), 0)
    check("but nothing at all is not", ok([], {"fr": 2, "en": 0}), 1)
    check("and a language asked for zero gets zero",
          ok(["How does the cluster share a card?"], {"fr": 1, "en": 0}), 1)
    check("the same subject twice",
          ok(["Comment Frigate enregistre ses images ?", "Pourquoi Frigate garde ses images ?"],
             {"fr": 2, "en": 0}), 1)

    print("\n\033[1m== it does not compete with a question someone really asked\033[0m")
    r3, corpus3, vocab3 = build(["Comment Frigate enregistre ses images ?"], tmp)
    check("a near-duplicate of a real question is refused",
          gate(["Pourquoi Frigate enregistre ses images ?"], corpus3, vocab3, {"fr": 1, "en": 0}, tmp), 1)
    check("a different subject is fine",
          gate(["Comment roule le cluster k3s ?"], corpus3, vocab3, {"fr": 1, "en": 0}, tmp), 0)

    print("\n\033[1m== the prompt's own examples cannot be published\033[0m")
    # On 2026-09-13 the model handed the other prompt its counter-example back
    # as a suggestion. Read from the prompt file, so an example added tomorrow
    # is guarded the day it is written.
    spec = importlib.util.spec_from_file_location("cg", GATE)
    cg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cg)
    examples = cg.prompt_examples()
    check("the prompt's examples were actually found", len(examples) >= 4, True)
    # Deliberately the ONE example the fake corpus grounds — "cluster", "douze"
    # and "nœuds" are all in FR_BODY above. Every other example is refused by
    # the grounding rule anyway, so testing with one of those would pass
    # whether this rule existed or not: a mutation test caught exactly that.
    ex = "Ton cluster a douze nœuds, non ?"
    check("the chosen example is one the prompt really contains", ex in examples, True)
    check(f"refuses {ex!r}", ok([ex], {"fr": 1, "en": 0}), 1)

    print("\n\033[1m== an invented machine is named as such, not as a missing word\033[0m")
    # This branch changes no verdict, only the sentence the retry loop shows the
    # model. That makes it invisible to an exit code, so the message is what is
    # asserted — a mutation run proved an exit-code test could not see it.
    o = pathlib.Path(tmp) / "msg.json"
    o.write_text(json.dumps({"openers": ["Ça fait quoi, worker9, dans le cluster ?"]},
                            ensure_ascii=False), encoding="utf-8")
    cm = pathlib.Path(tmp) / "msg-corpus.json"
    _c = json.loads(corpus_p.read_text(encoding="utf-8")); _c["need"] = {"fr": 1, "en": 0}
    cm.write_text(json.dumps(_c, ensure_ascii=False), encoding="utf-8")
    msg = subprocess.run([sys.executable, str(GATE), str(o), str(cm), str(vocab_p)],
                         capture_output=True, text=True).stderr
    check("says no such machine", "no such machine" in msg, True)
    check("and names the offender", "worker9" in msg, True)

    print("\n\033[1m== a written question never speaks as the lab's owner\033[0m")
    check("« mes » is refused",
          ok(["Comment Frigate enregistre mes images ?"], {"fr": 1, "en": 0}), 1)
    check("\"my\" is refused",
          ok(["How does my cluster share a card?"], {"fr": 0, "en": 1}), 1)
    check("« ton » is the visitor's voice and passes",
          ok(["Comment ton Frigate enregistre ses images ?"], {"fr": 1, "en": 0}), 0)

    print("\n\033[1m== --fresh-days keeps only this week's articles, one question each\033[0m")
    # The grounding is dated 2026-09-15; the articles 09-01 (with English) and
    # 09-02 (French only). The window is counted from the grounding, not the clock.
    rf, cf, _ = build([], tmp, ["--fresh-days", "14"])
    c = json.loads(cf.read_text(encoding="utf-8"))
    check("both articles inside fourteen days", len(c["articles"]), 2)
    check("one question per language, not four", c["need"], {"fr": 1, "en": 1})
    check("the corpus says it is fresh", c.get("fresh"), True)
    rf, cf, _ = build([], tmp, ["--fresh-days", "13"])
    c = json.loads(cf.read_text(encoding="utf-8"))
    check("thirteen days keeps only the newer one", [a["slug"] for a in c["articles"]],
          ["la-depeche-du-matin"])
    check("French-only article asks no English", c["need"], {"fr": 1, "en": 0})
    rf, _, _ = build([], tmp, ["--fresh-days", "5"])
    check("nothing recent exits 3, no model call", rf.returncode, 3)
    full_fr = [f"Comment Frigate enregistre ses images numéro {i} ?" for i in range(4)]
    rf, cf, _ = build(full_fr, tmp, ["--fresh-days", "14"])
    c = json.loads(cf.read_text(encoding="utf-8"))
    check("a language already full stays at zero", c["need"]["fr"], 0)

    print("\n\033[1m== a vocabulary too small to check anything is refused\033[0m")
    # Every content word of the probe IS in this vocabulary, so the ONLY thing
    # that can refuse it is the size floor itself.
    thin = pathlib.Path(tmp) / "thin.json"
    thin.write_text(json.dumps({"fr": ["frigate", "enregistre", "images"],
                                "en": ["frigate", "enregistre", "images"]}), encoding="utf-8")
    check("exits rather than passing everything",
          gate(["Comment Frigate enregistre ses images ?"], corpus_p, thin, {"fr": 1, "en": 0}, tmp), 1)

print(f"\n\033[1m{passed} passed, {failed} failed\033[0m")
sys.exit(1 if failed else 0)
