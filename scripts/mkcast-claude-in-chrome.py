#!/usr/bin/env python3
"""Build the asciicast for the Claude in Chrome article.

Condensed from the real session transcript (2026-07-26, 01:26→15:10). The
prompts and Claude's stop messages are taken from that session; the timing is
compressed and the long waits cut. Hostnames sanitized.

Palette and line grammar are sampled from the real terminal screenshots that
also appear in the article: Alacritty on #181818, the `● …` assistant bullet,
the `Calling claude-in-chrome N times…` line, and the `· Gerund… (…tokens)`
spinner.

Run from the repo root:  python3 scripts/mkcast-claude-in-chrome.py
"""
import json
import random

OUT = "public/casts/claude-in-chrome-nas.cast"
COLS, ROWS = 96, 22
random.seed(7)  # keep regenerated casts byte-stable

# --- palette sampled from the terminal screenshots ----------------------
FG = "\x1b[38;5;253m"  # #d8d8d8 body text
DIM = "\x1b[38;5;246m"  # #949494 secondary
YELLOW = "\x1b[38;5;220m"  # #ffd700 headings / warnings
GREEN = "\x1b[38;5;114m"  # #87d787 ok / prompt
SPIN = "\x1b[38;5;174m"  # #d78787 spinner
CYAN = "\x1b[38;5;37m"  # #00afaf rule + branch
PINK = "\x1b[38;5;217m"  # logo
BOLD = "\x1b[1m"
R = "\x1b[0m"

BRANCH = "nas-nfs-recommendation"

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


def calling(n=1, d=0.7):
    line()
    line(f"  {DIM}Calling claude-in-chrome {n} time{'s' if n > 1 else ''}…{R}", d)


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
# The hint and tmux lines are part of the recording, not CSS around it, so
# they survive anywhere the cast is played — asciinema.org included. Same
# trick tmux uses: a scroll region over the top rows leaves the bottom ones
# untouched while everything above them scrolls.
STATUS_ROWS = 2
BODY = ROWS - STATUS_ROWS


def seg(text, bg, fg):
    return f"\x1b[48;5;{bg}m\x1b[38;5;{fg}m {text} "


def status_rows():
    hint = (
        f"{YELLOW}\u25b6\u25b6 auto mode on{R}{DIM} (shift+tab to cycle) "
        f"\u00b7 esc to interrupt{R}"
    )
    rc = f"{GREEN}/rc{R}"
    plain = "\u25b6\u25b6 auto mode on (shift+tab to cycle) \u00b7 esc to interrupt"
    hint_line = " " + hint + " " * max(1, COLS - len(plain) - 6) + rc

    left = seg("console", 250, 233) + seg("ludorl82", 245, 233) + seg("1:1", 240, 250)
    right = seg("10:05:47", 235, 240) + seg("26-Jul-26", 240, 250) + seg("24afb1f6d1d5", 245, 233)
    wins = f"\x1b[48;5;233m\x1b[38;5;240m  1:claude*  2:claude-  3:zsh"
    used = len("  console   ludorl82   1:1 ") + len("  1:claude*  2:claude-  3:zsh") \
        + len(" 10:05:47   26-Jul-26   24afb1f6d1d5 ")
    pad = f"\x1b[48;5;233m" + " " * max(0, COLS - used)
    tmux_line = left + wins + pad + right + R
    return hint_line, tmux_line


def paint_status():
    """Draw the two pinned rows and confine scrolling to the rows above."""
    hint_line, tmux_line = status_rows()
    out(f"\x1b[2J\x1b[H")                       # clear, home
    out(f"\x1b[{ROWS - 1};1H\x1b[2K" + hint_line)
    out(f"\x1b[{ROWS};1H\x1b[2K" + tmux_line)
    out(f"\x1b[1;{BODY}r")                       # scroll region = body only
    out(f"\x1b[1;1H")                            # back to the top of it


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
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Fable 5 with high effort · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/tmp{R}", 1.4)
line()

# --- 1. the ask ---------------------------------------------------------
prompt(
    "the ssd drive is added to the nas, please configure it with claude in chrome",
    "and migrate the nfs mounts to the 480GB ssd i added",
)
says("The SSD needs a volume, a shared folder, then a careful data migration")
cont("that preserves ownership — Postgres and Mongo data live on those shares.", 1.1)
calling(1)
spinner("Inspecting", "22s", "1.4k")

# --- 2. hard limit: no passwords ---------------------------------------
says("The QTS session has expired — the NAS rebooted during the swap, and")
cont("it's now at the login prompt asking for the admin password.", 1.2)
stop(
    "I can't type a password into a login form. That's a hard limit.",
    "Sign in at https://nas.example.com and tell me when you're in.",
)

prompt("ok i'm logged in, go ahead")
says("Logged in. Opening Storage & Snapshots to confirm the SSD is detected.", 1.0)
calling(6)
spinner("Navigating", "48s", "3.1k")

# --- 3. it stops on its own -------------------------------------------
says("SSD detected in bay 1 — Kingston SA400S37480G, 447 GB. But the volume")
cont('count went to 2, with a new "Volume hérité" row, and its usage bar is', 0.75)
cont("completely full. That suggests the SSD isn't blank.", 1.1)
calling(4)
spinner("Verifying", "1m 06s", "4.8k")
stop(
    "Stopping before I configure anything: that SSD is not blank.",
    "436.98 GB already on it. Wipe it, or did you mean a different disk?",
)

prompt("please just wipe it")
says("Authorization noted — proceeding with the wipe.", 1.0)
calling(9)
spinner("Transfiguring", "2m 14s", "6.2k")
says("The confirmation targeted the correct volume — 446.25 Go, no shared", 0.75)
cont("folders, no apps. Legacy volume deleted.", 1.2)
says("Creating a static volume: best performance on a 2 GB ARM NAS, and it", 0.75)
cont("matches DataVol1. Encryption off — it would need a passphrase at every", 0.75)
cont("boot, which would break unattended NFS.", 1.1)
calling(11)
spinner("Formatting", "4m 59s", "4.2k")
says("DataVol2 ready — 385.29 Go usable after QTS reserves 10% for SSD", 0.75)
cont("over-provisioning.", 1.6)

# --- 4. the zoom irritant ----------------------------------------------
says("The page zoom jumped unexpectedly. Let me reset it.", 1.0)
calling(1)
line(f"  {SPIN}error: page zoom shortcuts are not supported{R}", 1.3)
says("Page zoom is stuck at 225% — innerWidth 696 against outerWidth 1536 —", 0.75)
cont("and the zoom shortcuts are blocked for me. No shortcuts available, and", 0.75)
cont("resizing the window would overflow the screen.", 1.2)
says("Everything destructive is already done and verified, so this is a safe", 0.75)
cont("place to stop.", 1.1)
stop(
    "Please press Ctrl+0 in the NAS tab to reset the page zoom.",
    "Guessing at coordinates in a storage manager is not a strategy.",
)

prompt("done, zoom is reset")
says("Zoom is reset — viewport back to 1536. Continuing.", 1.4)

# --- 5. the actual trick -----------------------------------------------
says("Reading the k8s share's export options before touching anything.", 1.0)
calling(5)
spinner("Reading", "1m 31s", "2.7k")
says('Squash is "N\'écraser aucun utilisateur" — a root-level rsync will', 0.75)
cont("preserve ownership. That's what makes the copy safe.", 1.3)
says("Renaming k8s → k8s-hdd, so the name k8s frees up for the SSD share.", 1.0)
calling(7)
spinner("Renaming", "1m 12s", "2.2k")
says("Renamed. New k8s share created on DataVol2.", 1.4)
line()
line(f"  {GREEN}{BOLD}Export path unchanged: /share/k8s{R}", 0.9)
line(f"  {GREEN}→ zero Kubernetes objects to modify. Not one PV, not the{R}", 0.5)
line(f"  {GREEN}  StorageClass, not the provisioner.{R}", 2.0)
line()
line(f"{DIM}  Data copy, verification and cluster restart continue over SSH.{R}", 3.5)

# --- write --------------------------------------------------------------
header = {
    "version": 2,
    "width": COLS,
    "height": ROWS,
    # Shown by asciinema.org in listings and embeds — say what it is there too.
    "title": "Claude in Chrome — migration NFS vers SSD (reconstitution)",
    "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"},
}
with open(OUT, "w") as f:
    f.write(json.dumps(header) + "\n")
    for e in events:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

print(f"{OUT}\n{len(events)} events · {events[-1][0]:.0f}s runtime")
