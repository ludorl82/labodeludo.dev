#!/usr/bin/env python3
"""Build the asciicast for the stateless-scheduler article.

A two-act reconstruction around one identical request — "drain the node my
scheduler runs on" — asked before and after the storage migration.

Act 1 (before): the scheduler keeps its data on the node's local disk, so
the evicted pod goes Pending with `volume node affinity conflict`. The
drain is technically a success; the service is technically down. The only
way out is to put the node back.

Act 2 (after, data in S3): the same drain. The replacement pod is Running
on another node 12 seconds after the eviction, because nothing had to move
— there was nothing on the node but CPU and RAM.

This one is a *simulation*, not a condensation of a single real session:
the migration is real (2026-08-07, Cronicle from a node-bound volume to
the S3 storage engine), the before/after behaviours are the true
behaviours of those two configurations, but the two drains were not run
back-to-back on camera and the storage story is simplified to local disk
for clarity. The disclaimer baked into the recording says so.

Names sanitized per house convention: nodes gpu-01 / vm-01, bucket
s3://scheduler-data. Palette and line grammar per
net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-stateless-move.py
"""
import json
import random

OUT = "public/casts/stateless-move.cast"
COLS, ROWS = 96, 22
random.seed(7)  # keep regenerated casts byte-stable

# --- palette sampled from the terminal screenshots ----------------------
FG = "\x1b[38;5;253m"  # #d8d8d8 body text
DIM = "\x1b[38;5;246m"  # #949494 secondary
YELLOW = "\x1b[38;5;220m"  # #ffd700 headings / warnings
GREEN = "\x1b[38;5;114m"  # #87d787 ok / prompt
SPIN = "\x1b[38;5;174m"  # #d78787 spinner, failures
CYAN = "\x1b[38;5;37m"  # #00afaf rule + branch
PINK = "\x1b[38;5;217m"  # logo
BOLD = "\x1b[1m"
R = "\x1b[0m"

BRANCH = "cronicle-refactor"

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


def prompt(text, d=1.8):
    rule()
    typed(f"{FG}{text}{R}", prefix=f"{GREEN}❯{R} ", d=d)
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


def watch(rows):
    """A condensed `kubectl get pods -o wide -w` style block."""
    line(f"  {DIM}NAME              STATUS              NODE     AGE{R}", 0.5)
    for name, status, colour, node, age, d in rows:
        line(
            f"  {FG}{name:<17}{R} {colour}{status:<19}{R} {FG}{node:<8}{R} {DIM}{age}{R}",
            d,
        )


# --- disclaimer ---------------------------------------------------------
# Baked into the recording itself, not just the page around it: the cast is
# published to asciinema.org too, where it stands alone.
line(f"{YELLOW}  ⚠  Simulation pédagogique — pas une capture en direct.{R}", 0.25)
line(f"{DIM}     La migration est réelle; les deux drains sont rejoués et le{R}", 0.25)
line(f"{DIM}     stockage est simplifié en disque local.  labodeludo.dev/casts/{R}", 2.6)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.220{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Fable 5 · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/k3s-iac{R}", 1.4)
line()

# --- act 1: before — the data lives on the node -------------------------
line(f"{YELLOW}{BOLD}  AVANT — les données du planificateur vivent sur le disque du nœud{R}", 2.2)
line()
prompt("i need to reboot gpu-01. can you drain it? cronicle runs there")
calling("Bash", 2)
spinner("Draining", "22s", "1.1k")
line(f"  {FG}node/gpu-01 cordoned{R}", 0.7)
line(f"  {FG}evicting pod cronicle/cronicle-7d4f9…{R}", 1.3)
watch(
    [
        ("cronicle-7d4f9", "Terminating", SPIN, "gpu-01", "13d", 0.8),
        ("cronicle-b112c", "Pending", YELLOW, "<none>", "2s", 0.9),
        ("cronicle-b112c", "Pending", YELLOW, "<none>", "45s", 0.9),
        ("cronicle-b112c", "Pending", YELLOW, "<none>", "2m11s", 1.6),
    ]
)
calling("Bash", 1)
line(f"  {SPIN}Warning  FailedScheduling{R}", 0.6)
line(f"  {DIM}  0/9 nodes are available: 1 node(s) had volume node affinity{R}", 0.5)
line(f"  {DIM}  conflict, 8 node(s) didn't find available persistent volume{R}", 1.5)
says("The drain worked; the scheduler didn't survive it. Its volume is bound")
cont("to gpu-01's local disk, so the replacement pod can only run on the one", 0.8)
cont("node you just emptied. Eight healthy nodes, zero candidates.", 1.5)
says("Nothing is broken. This is the configuration doing exactly what it")
cont("says: the data lives on that node, so the pod belongs to that node.", 1.6)
line()
line(f"  {YELLOW}{BOLD}Le pod n'a nulle part où aller.{R}", 0.9)
line(f"  {DIM}uncordon gpu-01, ou pas de planificateur pendant le reboot.{R}", 2.8)
prompt("ok uncordon it. i'll reboot another day", d=1.2)
calling("Bash", 1)
line(f"  {GREEN}node/gpu-01 uncordoned — cronicle-b112c Running on gpu-01 (8s){R}", 2.4)
line()

# --- interlude: the migration, in one line ------------------------------
line(f"{CYAN}  ─────────────────────────────────────────────────────────────────{R}", 0.4)
line(f"  {DIM}Une migration plus tard : moteur de stockage S3, 1 136 enregistrements{R}", 0.3)
line(f"  {DIM}copiés en 21 s, plus aucun volume. L'état du pod : un bucket, ailleurs.{R}", 2.6)
line(f"{CYAN}  ─────────────────────────────────────────────────────────────────{R}", 1.2)
line()

# --- act 2: after — stateless -------------------------------------------
line(f"{YELLOW}{BOLD}  APRÈS — les données vivent dans S3, le pod ne possède rien{R}", 2.2)
line()
prompt("ok gpu-01 reboot, take two. drain it — and time the pod this time")
calling("Bash", 3)
spinner("Draining", "31s", "1.4k")
line(f"  {FG}node/gpu-01 cordoned{R}", 0.7)
line(f"  {FG}evicting pod cronicle/cronicle-e83a1…   {DIM}t+0s{R}", 1.1)
watch(
    [
        ("cronicle-e83a1", "Terminating", SPIN, "gpu-01", "41m", 0.8),
        ("cronicle-f96d2", "Pending", YELLOW, "<none>", "0s", 0.7),
        ("cronicle-f96d2", "ContainerCreating", YELLOW, "vm-01", "1s", 1.0),
        ("cronicle-f96d2", "Running", GREEN, "vm-01", "4s", 0.9),
        ("cronicle-f96d2", "Running 1/1", GREEN, "vm-01", "12s", 1.8),
    ]
)
line(f"  {GREEN}scheduler ready on vm-01 — {BOLD}12 s{R}{GREEN} after the eviction{R}", 1.0)
line(f"  {GREEN}history intact: 30 events, job logs readable, S3 reads 140 ms{R}", 1.8)
says("Twelve seconds, and none of them were spent moving data — there is no")
cont("data to move. The pod carries its image and its config; everything it", 0.8)
cont("knows is in s3://scheduler-data, which never noticed the drain.", 1.6)
says("That is the whole trade. Before, the node owned the pod. Now any node")
cont("with CPU and RAM will do — gpu-01 is just hardware again.", 1.7)
line()
line(f"  {DIM}reboot gpu-01 whenever you like.{R}", 3.0)

# ------------------------------------------------------------------------
header = {
    "version": 2,
    "width": COLS,
    "height": ROWS,
    "title": "Un pod stateless change de nœud en 12 secondes",
    "env": {"SHELL": "/bin/zsh", "TERM": "alacritty"},
}
with open(OUT, "w") as f:
    f.write(json.dumps(header) + "\n")
    for ev in events:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")
print(f"{OUT}: {len(events)} events, {events[-1][0]:.0f}s")
