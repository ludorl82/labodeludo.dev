#!/usr/bin/env python3
"""Build the asciicast for the Home Assistant button that opens Claude Code
sessions in tmux (2026-08).

Condensed from the real session transcript. The prompts and Claude's messages
come from that session; timing is compressed and the investigation detours cut.

Hostnames are sanitized: the VM hosting the console container is `console-vm`
(the session itself runs inside that container — which is half the story).

Palette and line grammar per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-bouton-claude.py
"""
import json
import random

OUT = "public/casts/bouton-claude.cast"
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

BRANCH = "console-claude-session"

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


def running(cmd, d=0.7):
    line()
    line(f"  {DIM}{cmd}{R}", d)


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



# --- disclaimer ---------------------------------------------------------
line(f"{YELLOW}  ⚠  Reconstitution condensée — pas une capture en direct.{R}", 0.25)
line(f"{DIM}     Demandes et messages réels, minutage compressé,{R}", 0.25)
line(f"{DIM}     noms d'hôte sanitisés.  labodeludo.dev/casts/{R}", 2.6)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.225{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Opus 5 · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/git/nixos-iac{R}", 1.4)
line()

# --- 1. the ask ----------------------------------------------------------
prompt("can you make sure when console-vm is powered back on with the ha switch",
       "that it starts up claude code with remote control turned on in a tmux session called claude?")
says("Let me find how Remote Control is enabled and where `claude` actually")
cont("lives — then test the exact invocation before declaring it.", 1.2)
running("Bash  docker exec console tmux new-session -d -s claude 'claude --remote-control'")
spinner("Testing", "48s", "1.1k")
says("Works — Remote Control is live with a session URL. Now to declare it so")
cont("it happens on every boot.", 1.3)

# --- 2. the two-tmux-servers twist ----------------------------------------
prompt("hey i want the claude tmux session to run in the container you are",
       "currently running in")
says("Two different tmux servers — so my test was not landing where I am.")
cont("Let me identify my actual container:", 1.1)
running("Bash  cat /proc/self/cgroup && tmux -L console ls")
spinner("Investigating", "31s", "0.8k")
says("Same container — the difference is the tmux socket. I'm on a named")
cont("socket `console`; the unit created its session on the default socket,")
cont("so it's invisible to your `tmux ls`.", 1.2)
says("Found it: the image's entrypoint creates that socket, running for the")
cont("container's full 10-day uptime. That's the server to join. Fixing the")
cont("unit and letting GitOps deploy it.", 1.3)
spinner("Deploying", "2m 14s", "1.9k")

says(f"{GREEN}Working and verified end to end.{R} `tmux ls` now shows both:")
cont("claude:  1 windows (created Wed Aug 19 20:20:53 2026)", 0.6)
cont("console: 4 windows (created Sun Aug  9 11:08:46 2026)", 1.0)
says("The unit created the session unprompted — which is the real proof,")
cont("since that's the same path a boot takes.", 1.4)

# --- 3. the button --------------------------------------------------------
prompt("can you add a button in home assistant to add a new window in the tmux",
       "session with a new Claude code instance with remote control turned on?")
running("Bash  curl -X POST …/api/services/button/press  # full chain test")
spinner("Building", "4m 02s", "2.7k")
says(f"{GREEN}Done and verified through the full chain{R} — HA button press →")
cont("shell_command → SSH → dispatcher → tmux window with a live Claude.", 1.1)
says("Three new Home Assistant entities:")
cont(f"{FG}button.claude_window_ajouter{R}  opens window claude-N, Remote Control on", 0.7)
cont(f"{FG}button.claude_window_enlever{R}  kills the highest-indexed window", 0.7)
cont(f"{FG}sensor.claude_windows{R}         current window count, 60 s poll", 1.4)

# --- 4. the payoff question ------------------------------------------------
prompt("can i resume a session from remote control Claude app ?")
says("Yes — that's the core of what Remote Control is for, and it works in")
cont("both directions. Each window the button opens prints a session URL and")
cont("registers with your account.", 1.1)
says("Open that session in the app and you're driving the same session — same")
cont("conversation, same working directory, same tmux window. It isn't a")
cont("copy: type in the app and the tmux pane updates; type in the pane and")
cont("the app follows.", 1.4)
line()
line(f"  {DIM}A smart-home button that hires another Claude.{R}", 2.6)

# --- write it out -------------------------------------------------------
header = {
    "version": 2,
    "width": COLS,
    "height": ROWS,
    "title": "Un bouton domotique qui embauche un Claude (reconstitution)",
    "timestamp": 0,
    "idle_time_limit": 2,
    "env": {"TERM": "xterm-256color", "SHELL": "/bin/zsh"},
}
with open(OUT, "w") as fh:
    fh.write(json.dumps(header) + "\n")
    for ev in events:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

print(f"{OUT}: {len(events)} events, {events[-1][0]:.0f}s")
