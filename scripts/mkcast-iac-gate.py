#!/usr/bin/env python3
"""Build the asciicast for the four-repos / sanitization article.

Condensed from the real session transcript (2026-07-26). The prompts and
Claude's stop messages are taken from that session; the timing is compressed
and the long waits cut.

The moment being reconstructed: the last check before the two new snapshot
repos were made public. It caught a domain that had survived in *prose* — a
README sentence — long after every occurrence in the code had been replaced.

That hit came from the pre-publication scan, NOT from the gate: the gate had
no rule for that domain, which is exactly what the bug was. The cast keeps
that honest, and the payoff beat is the rule being added to both the
substitution and the gate.

Names sanitized, and this one deserves a note: the leaked value shown on
screen is the FICTIONAL name (`shrt.example`), not the real one the gate
actually caught. A cast of a leak detector would otherwise publish the very
thing the detector exists to stop. The `disclaimer` prop on the embed says
so; see net-cfgs/asciicast-style.md, trap 3.

Palette and line grammar per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-iac-gate.py
"""

import claude_tui as T
from claude_tui import BOLD, CYAN, DIM, FG, GREEN, PINK, R, RED, SPIN, YELLOW, calling, cont, line, prompt, says, spinner, waiting

T.setup(
    out="public/casts/iac-sanitize-gate.cast",
    title="La barrière de vérification refuse de publier (reconstitution)",
    session="sanitize-public",
    windows=["backlog", "sanitize-public"],
    current="sanitize-public",
    start="26-Jul-26 15:42:09",
    cwd="~/tmp",
    model="Opus 5 with high effort · Claude Max",
    version="v2.1.220",
    seed=7,
)

# Baked into the recording itself, not just the page around it: the cast is
# published to asciinema.org too, where it stands alone, and an embedded or
# downloaded file carries no page at all. This must not get separated from it.
T.disclaimer("Demandes et messages réels, minutage compressé,",
             "noms d'hôte sanitisés.")
T.banner()


def stop(text, detail=None, d=3.2):
    """Ancienne aide : le message d'arrêt en jaune, puis l'agent rend la main."""
    line(f"  {YELLOW}{BOLD}{text}{R}", 0.9)
    if detail:
        line(f"  {YELLOW}{detail}{R}", 0.6)
    waiting()
    pause_ = d - 1.2
    if pause_ > 0:
        T.pause(pause_)

# --- 1. the ask ---------------------------------------------------------
prompt("can you also make a public version of aws-iac and cloudflare-iac?")
says("Both are sanitizable, and neither tracks state — *.tfstate is gitignored")
cont("in both, and git ls-files confirms zero tracked files.", 1.2)
calling("Write", 2)
spinner("Building", "3m 12s", "8.4k")
says("Copying only what git tracks, not an exclude list — tofu leaves real")
cont("state on disk, and an exclude list is one typo from shipping it.", 1.6)
says("Each sanitizer ends in a verification gate. The substitutions are best")
cont("effort; the gate is the guarantee. A missed rule fails the run instead", 0.75)
cont("of leaking quietly.", 1.2)
calling("Bash", 1)
spinner("Validating", "9s", "0.7k")
line(f"  {GREEN}Success! The configuration is valid.{R}", 0.8)
line(f"  {GREEN}sanitized tree written (verification gate passed){R}", 1.9)
says("Both snapshots pass. Pushed — as private repos.", 1.3)
stop(
    "Left them private on purpose: a review branch on a public repo",
    "is already public. Say the word and I'll flip them.",
)

# --- 2. ship it ---------------------------------------------------------
prompt("make them public")
says("Before flipping — a final check against what's actually on the remotes,")
cont("since that's what becomes public, not my local copy.", 1.2)
calling("Bash", 1)
spinner("Cloning", "6s", "1.1k")

# --- 3. the check fires -------------------------------------------------
# Accuracy note: this hit came from the pre-publication scan, not from the
# gate — the gate had no rule for that domain, which is precisely the bug.
# The next beat is Claude adding it to BOTH, which is the real lesson.
line(f"  {SPIN}{BOLD}LEAK [real domain]:{R}", 0.7)
line(f"  {DIM}./README.md:95:- `shrt.example` DNS — that zone is in Route53,{R}", 0.45)
line(f"  {DIM}                 not Cloudflare. It belongs to aws-iac phase 5.{R}", 1.1)
line()
line(f"  {SPIN}{BOLD}REFUSING to declare this tree publishable.{R}", 3.4)
line()
says("One real miss. I mapped that domain in the aws sanitizer and never in")
cont("the cloudflare one — and it survived in prose, in a README sentence,", 0.8)
cont("long after every occurrence in the code had been replaced.", 1.5)
says("A domain in a sentence leaks exactly as well as a domain in code.", 2.6)

# --- 4. fix the rule AND the gate ---------------------------------------
says("Adding it in two places, not one: the substitution, so it gets", 0.8)
cont("replaced — and the gate, so the next run catches it without me.", 1.6)
calling("Edit", 1)
# La barre tmux redessine son heure chaque seconde. Entre ces deux lignes,
# aucune seconde ne doit tomber : le flux brut collerait l'heure à la ligne
# « + sub », dont l'acquittement (check-public-leaks) vaut pour elle seule.
line(f"  {GREEN}+ sub \"lrl.io\"  \"shrt.example\"{R}", 0.25)
line(f"  {GREEN}+ check \"real domain\" '(…|lrl\\.io|…)'{R}", 1.85)
line()
calling("Bash", 1)
spinner("Regenerating", "11s", "0.9k")
line(f"  {GREEN}sanitized tree written (verification gates passed){R}", 2.2)
says("Force-pushed as a fresh single commit, so the leaking version is gone")
cont("from the history rather than merely superseded.", 1.3)
says("Both repos were still private the entire time. It was never exposed.", 2.0)

# --- 5. flip ------------------------------------------------------------
calling("Bash", 2)
spinner("Flipping", "8s", "0.6k")
line(f"  {GREEN}nixos-iac-public         PUBLIC{R}", 0.35)
line(f"  {GREEN}k3s-iac-public           PUBLIC{R}", 0.35)
line(f"  {GREEN}aws-iac-public           PUBLIC{R}", 0.35)
line(f"  {GREEN}cloudflare-iac-public    PUBLIC{R}", 1.8)
line()
calling("Bash", 1)
spinner("Verifying", "4s", "0.3k")
line(f"  {GREEN}all four reachable anonymously — HTTP 200{R}", 2.2)
line()
line(f"{DIM}  Caught fifteen minutes before publication.{R}", 3.5)

T.save()
