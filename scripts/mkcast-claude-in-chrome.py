#!/usr/bin/env python3
"""Build the asciicast for the Claude in Chrome article.

Condensed from the real session transcript (2026-07-26, 01:26→15:10). The
wording of the prompts and of Claude's stop messages is taken from that
session; the timing is compressed and the long waits cut, so ~50 minutes of
NAS work plays in about two minutes. Hostnames sanitized.
"""
import json
import random

OUT = "public/casts/claude-in-chrome-nas.cast"
COLS, ROWS = 98, 20

# --- palette, matching the site's terminal look -------------------------
GREEN = "\x1b[38;5;77m"
DIM = "\x1b[38;5;244m"
WHITE = "\x1b[38;5;255m"
ORANGE = "\x1b[38;5;215m"
RED = "\x1b[38;5;203m"
PINK = "\x1b[38;5;217m"
BOLD = "\x1b[1m"
R = "\x1b[0m"

events = []
t = 0.0


def out(s):
    events.append([round(t, 3), "o", s])


def pause(d):
    global t
    t += d


def line(s="", d=0.28):
    out(s + "\r\n")
    pause(d)


def typed(s, d=0.55):
    """Type a line character by character, like a human at the prompt."""
    global t
    for ch in s:
        out(ch)
        t += random.uniform(0.018, 0.055)
    out("\r\n")
    pause(d)


def prompt(user_text):
    out(f"{GREEN}❯{R} ")
    pause(0.5)
    typed(f"{WHITE}{user_text}{R}")


def claude(text, d=0.5):
    line(f"{ORANGE}●{R} {text}", d)


def tool(name, arg, d=0.32):
    line(f"  {DIM}└─ {name}({arg}){R}", d)


def stop(text):
    line()
    line(f"{RED}{BOLD}■ {text}{R}", 0.9)
    line()


# --- 0. banner ----------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.220{R}", 0.15)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Fable 5 with high effort · Claude Pro{R}", 0.15)
line(f"{PINK}  ▀▀    ▀▀{R}", 0.6)
line()
line(f"{DIM}Claude in Chrome: enabled · browser connected{R}", 0.9)
line()

# --- 1. the ask ---------------------------------------------------------
prompt("the ssd drive is added to the nas, please configure it with claude in chrome")
out(f"{GREEN}❯{R} ")
pause(0.3)
typed(f"{WHITE}and migrate the nfs mounts to the 480GB ssd i added{R}", 1.0)
line()

claude("The SSD needs a volume, a shared folder, then a careful data migration that")
line("  preserves ownership — Postgres and Mongo data live on those shares.", 0.6)
tool("claude-in-chrome", "screenshot")
pause(1.2)

# --- 2. hard limit: no passwords ---------------------------------------
claude("The QTS session has expired — the NAS rebooted during the swap, and it's")
line("  now at the login prompt asking for the admin password.", 0.5)
stop("I can't type a password into a login form. That's a hard limit.")
line(f"{DIM}  Waiting for you to sign in at https://nas.example.com …{R}", 2.4)
line()

prompt("ok i'm logged in, go ahead")
line()
claude("Logged in. Opening Storage & Snapshots to confirm the SSD is detected.", 0.4)
for arg in ("screenshot", "left_click 691,133", "wait 5s", "screenshot"):
    tool("claude-in-chrome", arg, 0.22)
pause(0.8)

# --- 3. it stops on its own -------------------------------------------
claude("SSD detected in bay 1 — but the volume count went to 2, with a new")
line('  "Volume hérité" row. That suggests the SSD isn\'t blank.', 0.5)
for arg in ("left_click 264,300", "screenshot", "hover 1265,369", "zoom 900,330→1400,430"):
    tool("claude-in-chrome", arg, 0.22)
pause(0.7)
claude("Kingston SA400S37480G, 447 GB. Legacy volume usage bar is completely full.", 0.6)
stop("Stopping before configuring anything: that SSD is not blank.")
line(f"  {WHITE}436.98 GB already on it. Wipe it, or did you mean a different disk?{R}", 2.2)
line()

prompt("please just wipe it")
line()
claude("Authorization noted — proceeding with the wipe.", 0.4)
for arg in (
    "left_click 600,369",
    "left_click 1258,219",
    "screenshot",
    "left_click 1154,236",
    "screenshot",
):
    tool("claude-in-chrome", arg, 0.2)
claude("The confirmation targets the correct volume — 446.25 Go, no shared folders.", 0.5)
tool("claude-in-chrome", "left_click 855,628 → Appliquer", 0.6)
claude("Legacy volume deleted. Creating a static volume on the SSD.", 0.5)
for arg in ("left_click 1004,219", "screenshot", "left_click 411,410", "wait 10s"):
    tool("claude-in-chrome", arg, 0.22)
claude("DataVol2 ready — 385.29 Go usable after QTS reserves 10% over-provisioning.", 1.0)
line()

# --- 4. the zoom irritant ----------------------------------------------
tool("claude-in-chrome", "screenshot", 0.25)
claude("The page zoom jumped unexpectedly. Let me reset it.", 0.4)
tool("claude-in-chrome", "key ctrl+0", 0.4)
line(f"  {RED}└─ error: page zoom shortcuts are not supported{R}", 0.5)
tool("claude-in-chrome", "javascript devicePixelRatio, innerWidth, outerWidth", 0.4)
line(f"  {DIM}└─ {{ iw: 696, ow: 1536 }}{R}", 0.5)
claude("Page zoom is stuck at 225%, and zoom shortcuts are blocked for me.", 0.45)
tool("claude-in-chrome", "shortcuts_list", 0.3)
line(f"  {DIM}└─ none available{R}", 0.4)
tool("claude-in-chrome", "resize_window 3400x1800", 0.5)
claude("No route from here. Everything destructive is already done and verified,", 0.3)
line("  so this is a safe place to stop.", 0.5)
stop("Please press Ctrl+0 in the NAS tab to reset the page zoom.")
line(f"{DIM}  Guessing at coordinates in a storage manager is not a strategy.{R}", 2.4)
line()

prompt("done, zoom is reset")
line()
tool("claude-in-chrome", "javascript innerWidth", 0.3)
line(f"  {DIM}└─ {{ iw: 1536 }}{R}", 0.4)
claude("Zoom is reset. Continuing.", 0.8)
line()

# --- 5. the actual trick -----------------------------------------------
claude("Reading the k8s share's export options before touching anything.", 0.4)
for arg in ("left_click 546,41", "left_click 903,222", "zoom 551,510→1205,570"):
    tool("claude-in-chrome", arg, 0.22)
claude('Squash is "N\'écraser aucun utilisateur" — a root rsync will preserve', 0.3)
line("  ownership. That's what makes the copy safe.", 0.7)
claude("Renaming k8s → k8s-hdd so the name k8s frees up for the SSD share.", 0.45)
for arg in ("triple_click 757,204", 'type "k8s-hdd"', "left_click 906,681"):
    tool("claude-in-chrome", arg, 0.25)
claude("Renamed. Creating the new k8s share on DataVol2.", 0.45)
for arg in ('type "k8s"', "left_click 622,345", "screenshot"):
    tool("claude-in-chrome", arg, 0.25)
line()
claude(f"{BOLD}Export path unchanged: /share/k8s{R}", 0.5)
line(f"  {GREEN}→ zero Kubernetes objects to modify. Not one PV, not the StorageClass.{R}", 1.6)
line()
line(f"{DIM}  Data copy, verification and cluster restart continue over SSH.{R}", 2.5)

# --- write --------------------------------------------------------------
header = {
    "version": 2,
    "width": COLS,
    "height": ROWS,
    "title": "Claude in Chrome — migration NFS vers SSD",
    "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"},
}
with open(OUT, "w") as f:
    f.write(json.dumps(header) + "\n")
    for e in events:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

print(f"{OUT}\n{len(events)} events · {events[-1][0]:.1f}s runtime")
