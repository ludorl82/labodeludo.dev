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

import claude_tui as T
from claude_tui import BOLD, CYAN, DIM, FG, GREEN, PINK, R, RED, SPIN, YELLOW, calling, cont, line, prompt, says, spinner, waiting

T.setup(
    out="public/casts/bouton-claude.cast",
    title="Un bouton domotique qui embauche un Claude (reconstitution)",
    session="console-claude-session",
    windows=["backlog", "console-claude-session"],
    current="console-claude-session",
    start="19-Aug-26 20:08:12",
    cwd="~/git/nixos-iac",
    model="Opus 5 · Claude Max",
    version="v2.1.225",
    seed=7,
)

T.disclaimer("Demandes et messages réels, minutage compressé,",
             "noms d'hôte sanitisés.")
T.banner()


# --- 1. the ask ----------------------------------------------------------
prompt("can you make sure when console-vm is powered back on with the ha switch",
       "that it starts up claude code with remote control turned on in a tmux session called claude?")
says("Let me find how Remote Control is enabled and where `claude` actually")
cont("lives — then test the exact invocation before declaring it.", 1.2)
calling("Bash", 1)
T.detail(f"{DIM}docker exec console tmux new-session -d -s claude 'claude --remote-control'{R}", 0.7)
spinner("Testing", "48s", "1.1k")
says("Works — Remote Control is live with a session URL. Now to declare it so")
cont("it happens on every boot.", 1.3)

# --- 2. the two-tmux-servers twist ----------------------------------------
prompt("hey i want the claude tmux session to run in the container you are",
       "currently running in")
says("Two different tmux servers — so my test was not landing where I am.")
cont("Let me identify my actual container:", 1.1)
calling("Bash", 1)
T.detail(f"{DIM}cat /proc/self/cgroup && tmux -L console ls{R}", 0.7)
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
calling("Bash", 1)
T.detail(f"{DIM}curl -X POST …/api/services/button/press  # full chain test{R}", 0.7)
spinner("Building", "4m 02s", "2.7k")
says(f"{GREEN}Done and verified through the full chain{R} — HA button press →")
cont("shell_command → SSH → dispatcher → tmux window with a live Claude.", 1.1)
says("Three new Home Assistant entities:")
cont(f"{FG}button.claude_window_ajouter{R}  opens window claude-N, Remote Control on", 0.7)
cont(f"{FG}button.claude_window_enlever{R}  kills the highest-indexed window", 0.7)
cont(f"{FG}sensor.claude_windows{R}         current window count, 60 s poll", 1.4)

# --- 4. closing ----------------------------------------------------------
# The session's final Q&A ("can i resume a session from remote control Claude
# app?") is deliberately CUT: the real answer covered attaching to live
# sessions and never actually answered the question as meant (resuming a
# previously *closed* session from the app — which doesn't work; that still
# takes /resume over ssh in the tmux pane). The page prose carries the honest
# limitation instead. Condense by cutting, never by rewriting.
says("Each window the button opens prints a session URL and registers with")
cont("your account — open it in the app and you're driving the same session.", 1.4)
line()
line(f"  {DIM}A smart-home button that hires another Claude.{R}", 2.6)

T.save()
