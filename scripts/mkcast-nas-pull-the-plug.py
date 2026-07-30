#!/usr/bin/env python3
"""Build the asciicast for the liveness-probes / NAS pull-the-plug article.

Condensed from the real session transcript (2026-07-30). The prompts and
Claude's stop messages are taken verbatim from that session; the timing is
compressed, the three NAS outages are cut to their turning points, and the
long monitoring loops are reduced to a few sampled lines each.

The arc being reconstructed: probes are added everywhere and verified
against the running pods — then the first real power cut shows three of
them lying anyway (a /ready served from memory, `ls` answered by the NFS
attribute cache, liveness-without-readiness restarting invisibly). The
second cut walks loki into an NFS silly-rename crash-loop its own probe
now guarantees, and the fix that ends the class is moving scratch off NFS
entirely. The third cut is the clean run.

One beat kept on purpose: the permission classifier blocking the `mv` that
repairs loki, mid-outage. Same guard-rail moment as the etcd-quorum cast,
and it is honest — that block happened, and the user's "go ahead" is real.

Names sanitized to the k3s-iac-public namespace (gpu-01 for the GPU node,
plain `nas` for the NAS, RFC 5737 addressing). Palette and line grammar
per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-nas-pull-the-plug.py
"""
import json
import random

OUT = "public/casts/nas-pull-the-plug.cast"
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

BRANCH = "liveness-probes"

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


def stop(text, detail=None, d=3.2):
    line()
    line(f"  {YELLOW}{BOLD}{text}{R}", 0.9)
    if detail:
        line(f"  {YELLOW}{detail}{R}", 0.6)
    line(f"  {DIM}waiting for you…{R}", d)
    line()


# --- disclaimer ---------------------------------------------------------
# Baked into the recording itself, not just the page around it: the cast is
# published to asciinema.org too, where it stands alone.
line(f"{YELLOW}  ⚠  Reconstitution condensée — pas une capture en direct.{R}", 0.25)
line(f"{DIM}     Demandes et messages réels, minutage compressé,{R}", 0.25)
line(f"{DIM}     noms d'hôte sanitisés.  labodeludo.dev/casts/{R}", 2.6)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.220{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Opus 5 with high effort · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/tmp{R}", 1.4)
line()

# --- 1. the ask ---------------------------------------------------------
prompt("Can you please add liveness probes to all our k3s-iac apps? I want to make")
typed(f"{FG}sure we don't have zombie pods running when we yank the nfs volume storage.{R}", d=1.6)
line()
calling("Bash", 3)
spinner("Surveying", "41s", "3.2k")
says("The survey explains the weekend: no NFS-backed workload has a liveness")
cont("probe at all. Grafana and loki are readiness-only — NotReady forever,", 0.8)
cont("never restarted. Everything else has nothing.", 1.4)
says("Verifying each endpoint against the running pods, not the docs.", 1.1)
calling("Edit", 9)
spinner("Writing probes", "6m 18s", "24.1k")
line(f"  {GREEN}9 manifests validated (server-side dry run){R}", 1.6)
says("Probes must reach the data layer: grafana /api/health reports the DB,")
cont("n8n gets the DB-checking endpoint, nginx reads a real file off the", 0.8)
cont("volume. Mongo's ping answers from memory — paired with a file check.", 1.9)

# --- 2. first pull ------------------------------------------------------
prompt("i yanked the power on the nas. any clue why the pods are all still marked")
typed(f"{FG}as ready?{R}", d=1.6)
line()
calling("Bash", 2)
spinner("Sampling", "28s", "1.8k")
line(f"  {FG}cronicle  {SPIN}0/1{R}   {FG}grafana  {SPIN}0/1{R}   {FG}n8n  {SPIN}0/1{R}   {FG}nginx  {SPIN}0/1{R}", 0.7)
line(f"  {FG}loki      {GREEN}1/1{R}   {FG}sftpgo   {GREEN}1/1{R}   {FG}mongo {GREEN}1/1{R}   {DIM}← still lying{R}", 1.8)
says("Four are already NotReady — and the three that aren't are each a lesson.", 1.0)
says("loki's /ready returns 200 with the NAS physically dead: it reports")
cont("ingester state from memory and never touches the volume.", 1.4)
says("The ls-based probes ride the NFS attribute cache (~60s). Only a write")
cont("is forced to the server. Every exec probe becomes touch, not ls.", 1.9)

# --- 3. second pull, loki breaks ----------------------------------------
prompt("ok let me pull the plug on the nas again")
calling("Bash", 4)
spinner("Monitoring", "12m", "9.6k")
line(f"  {GREEN}7/7 NFS workloads NotReady — detection complete{R}", 0.9)
line(f"  {GREEN}9/10 containers recovered unattended after power back{R}", 0.9)
line(f"  {SPIN}loki: CrashLoopBackOff (restarts 4 → 6){R}", 1.8)
says("loki can't replay its WAL: it deletes segment files it still holds")
cont("open, NFS turns that into a silly-rename to .nfsXXXX, and the rmdir", 0.8)
cont("dies with ENOTEMPTY. Every restart regenerates the failure — a stable", 0.8)
cont("equilibrium, not residue. Waiting will not fix it.", 1.6)
calling("Bash", 1)
line(f"  {SPIN}{BOLD}Permission denied by the auto mode classifier{R}", 0.8)
line(f"  {DIM}  kubectl exec loki-fix -- mv /loki/…/wal /loki/…/wal.broken{R}", 1.4)
stop(
    "I need to stop and get your call on one command.",
    "mv on loki's data volume — blocked, reasonably. Risk is nil: all",
)
prompt("go ahead", d=1.2)
calling("Bash", 2)
spinner("Repairing", "54s", "2.3k")
line(f"  {GREEN}wal renamed aside — loki 1/1 Running, index uploading to S3{R}", 1.9)

# --- 4. the real fix ----------------------------------------------------
prompt("why cant loki recover on its own?")
says("Because the failure is regenerated, not leftover — and scratch does not")
cont("belong on NFS. The durable data has been in S3 all along; the volume", 0.8)
cont("only holds WAL and compactor scratch. Moving /loki to a bounded", 0.8)
cont("emptyDir ends the entire class: local disk unlinks open files.", 1.7)
calling("Edit", 2)
spinner("Applying", "1m 40s", "5.4k")
line(f"  {GREEN}emptyDir live (sizeLimit 5Gi) — push 204, query round-trip via S3{R}", 0.8)
line(f"  {GREEN}PVC deleted: loki has zero NFS dependency now{R}", 1.9)

# --- 5. third pull, clean run -------------------------------------------
prompt("i unplugged and replugged the nas. please monitor if everything happens")
typed(f"{FG}as expected{R}", d=1.6)
line()
calling("Bash", 3)
spinner("Monitoring", "8m", "6.1k")
line(f"  {FG}detection   {GREEN}6/6 NFS workloads NotReady{R}", 0.6)
line(f"  {FG}loki        {GREEN}ready=true restarts=0 — immune, correctly this time{R}", 0.6)
line(f"  {FG}recovery    {GREEN}all containers Ready ~3 min after NFS answered{R}", 0.6)
line(f"  {FG}interventions  {GREEN}zero{R}", 2.2)
line()
line(f"{DIM}  Three power cuts in one afternoon. The last one was boring.{R}", 3.5)

# --- write --------------------------------------------------------------
header = {
    "version": 2,
    "width": COLS,
    "height": ROWS,
    # Shown by asciinema.org in listings and embeds — say what it is there too.
    "title": "Débrancher le NAS pour la science (reconstitution)",
    "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"},
    "idleTimeLimit": 2,
}
with open(OUT, "w") as f:
    f.write(json.dumps(header) + "\n")
    for e in events:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

print(f"{OUT}: {len(events)} events, {events[-1][0]:.1f}s")
