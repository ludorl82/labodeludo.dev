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
import json
import random

OUT = "public/casts/iac-sanitize-gate.cast"
COLS, ROWS = 96, 22
random.seed(7)  # keep regenerated casts byte-stable

# --- palette sampled from the terminal screenshots ----------------------
FG = "\x1b[38;5;253m"  # #d8d8d8 body text
DIM = "\x1b[38;5;246m"  # #949494 secondary
YELLOW = "\x1b[38;5;220m"  # #ffd700 headings / warnings
GREEN = "\x1b[38;5;114m"  # #87d787 ok / prompt
SPIN = "\x1b[38;5;174m"  # #d78787 spinner, and the failure lines here
CYAN = "\x1b[38;5;37m"  # #00afaf rule + branch
PINK = "\x1b[38;5;217m"  # logo
BOLD = "\x1b[1m"
R = "\x1b[0m"

BRANCH = "sanitize-public"

events, t = [], 0.0


def out(s):
    events.append([round(t, 3), "o", s])


def pause(d):
    global t
    t += d


def line(s="", d=0.55):
    out(s + "\r\n")
    pause(d)


def typed(s, prefix="", d=1.5):
    """Type a line out character by character, at human speed."""
    global t
    if prefix:
        out(prefix)
        pause(0.7)
    for ch in s:
        out(ch)
        t += random.uniform(0.045, 0.115)
    out("\r\n")
    pause(d)


def rule():
    """The branch rule the TUI draws above the prompt."""
    dashes = "─" * (COLS - len(BRANCH) - 3)
    line(f"{CYAN}{dashes} {BRANCH}{R}", 0.5)


def prompt(text, second=None):
    rule()
    typed(f"{FG}{text}{R}", prefix=f"{GREEN}❯{R} ", d=0.6 if second else 1.8)
    if second:
        typed(f"{FG}{second}{R}", prefix=f"{GREEN}❯{R} ", d=1.8)
    line()


def says(text, d=0.9):
    line(f"{FG}●{R} {text}", d)


def cont(text, d=0.9):
    line(f"  {text}", d)


def calling(tool, n=1, d=0.7):
    line()
    line(f"  {DIM}Calling {tool} {n} time{'s' if n > 1 else ''}…{R}", d)


def spinner(word, secs, tokens, d=2.0):
    line(f"{SPIN}· {word}…{R} {DIM}({secs} · ↓ {tokens} tokens){R}", d)
    line()


def stop(text, detail=None, d=3.2):
    line()
    line(f"  {YELLOW}{BOLD}{text}{R}", 0.9)
    if detail:
        line(f"  {YELLOW}{detail}{R}", 0.6)
    line(f"  {DIM}waiting for you…{R}", d)
    line()



# --- pinned status rows -------------------------------------------------
# The hint and tmux lines belong to the recording, not to CSS around it, so
# they survive wherever the cast is played — asciinema.org, embeds, a raw
# download. Same mechanism tmux uses: a scroll region over the upper rows
# leaves the bottom ones untouched while everything above them scrolls.
# Because they are terminal cells, they scale with the terminal instead of
# competing with it for width, which is what made the CSS version unusable
# on a phone.
STATUS_ROWS = 2
BODY = ROWS - STATUS_ROWS

CLOCK = "14:22:09"
STAMP = "26-Jul-26"
CONTAINER = "7b3c1e90a4d2"

HINT_PLAIN = "\u25b6\u25b6 auto mode on (shift+tab to cycle) \u00b7 esc to interrupt"
WINS_PLAIN = "1:claude*  2:claude-  3:zsh"


def _seg(text, bg, fg):
    return f"\x1b[48;5;{bg}m\x1b[38;5;{fg}m {text} ", len(text) + 2


def _hint_row():
    left = (
        f" {YELLOW}\u25b6\u25b6 auto mode on{R}"
        f"{DIM} (shift+tab to cycle) \u00b7 esc to interrupt{R}"
    )
    pad = max(1, COLS - 1 - len(HINT_PLAIN) - 4)
    return left + " " * pad + f"{GREEN}/rc{R} "


def _tmux_row():
    left, wl = "", 0
    for t, bg, fg in (("console", 250, 233), ("ludorl82", 245, 233), ("1:1", 240, 250)):
        s, w = _seg(t, bg, fg)
        left += s
        wl += w
    right, wr = "", 0
    for t, bg, fg in ((CLOCK, 235, 240), (STAMP, 240, 250), (CONTAINER, 245, 233)):
        s, w = _seg(t, bg, fg)
        right += s
        wr += w
    mid = max(len(WINS_PLAIN), COLS - wl - wr)
    gap = (mid - len(WINS_PLAIN)) // 2
    wins = (
        f"\x1b[48;5;233m" + " " * gap
        + f"\x1b[1m\x1b[38;5;253m1:claude*{R}\x1b[48;5;233m"
        + f"\x1b[38;5;240m  2:claude-  3:zsh"
        + " " * (mid - len(WINS_PLAIN) - gap)
    )
    return left + wins + right + R


def paint_status():
    """Draw the pinned rows, then confine scrolling to the rows above them."""
    out("\x1b[2J\x1b[H")
    out(f"\x1b[{ROWS - 1};1H\x1b[2K" + _hint_row())
    out(f"\x1b[{ROWS};1H\x1b[2K" + _tmux_row())
    out(f"\x1b[1;{BODY}r")
    out("\x1b[1;1H")


paint_status()

# --- disclaimer ---------------------------------------------------------
# Baked into the recording itself, not just the page around it: the cast is
# published to asciinema.org too, where it stands alone, and an embedded or
# downloaded file carries no page at all. This must not get separated from it.
line(f"{YELLOW}  \u26a0  Reconstitution condens\u00e9e \u2014 pas une capture en direct.{R}", 0.25)
line(f"{DIM}     Demandes et messages r\u00e9els, minutage compress\u00e9,{R}", 0.25)
line(f"{DIM}     noms d'h\u00f4te sanitis\u00e9s.  labodeludo.dev/casts/{R}", 2.6)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.220{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Opus 5 with high effort · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/tmp{R}", 1.4)
line()

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
line(f"  {GREEN}+ sub \"lrl.io\"  \"shrt.example\"{R}", 0.6)
line(f"  {GREEN}+ check \"real domain\" '(…|lrl\\.io|…)'{R}", 1.5)
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

# --- write --------------------------------------------------------------
header = {
    "version": 2,
    "width": COLS,
    "height": ROWS,
    # Shown by asciinema.org in listings and embeds — say what it is there too.
    "title": "La barrière de vérification refuse de publier (reconstitution)",
    "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"},
    "idleTimeLimit": 2,
}
with open(OUT, "w") as f:
    f.write(json.dumps(header) + "\n")
    for e in events:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

print(f"{OUT}: {len(events)} events, {events[-1][0]:.1f}s")
