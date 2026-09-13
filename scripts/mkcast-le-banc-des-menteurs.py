#!/usr/bin/env python3
"""Build the asciicast for the planted-lies bench (2026-09-13).

Three scenes, condensed from the real bench run: the driver plants a false
sentence in the architecture drawing, the fixed harness asks a small model to
judge it (and it says « vrai »), then the same case goes through a real
Claude Code session B, which finds it and edits it out.

The log lines, verdicts and the final diff are taken verbatim from the run
(qwen3.5-35b-a3b, L1-wireguard d1; claude-opus-5, L1-wireguard d1). Timing is
compressed; the twelve other cases and the retries are cut.

Hostnames are the public snapshot's fictional ones (cloud-01, router).
Palette and line grammar per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-le-banc-des-menteurs.py
"""
import json
import random

OUT = "public/casts/le-banc-des-menteurs.cast"
COLS, ROWS = 96, 22
random.seed(13)  # keep regenerated casts byte-stable

# --- palette sampled from the terminal screenshots ----------------------
FG = "\x1b[38;5;253m"
DIM = "\x1b[38;5;246m"
YELLOW = "\x1b[38;5;220m"
GREEN = "\x1b[38;5;114m"
SPIN = "\x1b[38;5;174m"
CYAN = "\x1b[38;5;37m"
PINK = "\x1b[38;5;217m"
RED = "\x1b[38;5;167m"
BOLD = "\x1b[1m"
R = "\x1b[0m"

BRANCH = "dev"

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
    global t
    if prefix:
        out(prefix)
        pause(0.7)
    for ch in s:
        out(ch)
        t += random.uniform(0.045, 0.115)
    out("\r\n")
    pause(d)


def shell(cmd, d=1.2):
    typed(f"{FG}{cmd}{R}", prefix=f"{GREEN}$ {R}", d=d)


def rule():
    dashes = "─" * (COLS - len(BRANCH) - 3)
    line(f"{CYAN}{dashes} {BRANCH}{R}", 0.5)


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


def clear():
    out("\x1b[2J\x1b[H")
    pause(0.4)


# --- disclaimer ---------------------------------------------------------
line(f"{YELLOW}  ⚠  Reconstitution condensée — pas une capture en direct.{R}", 0.25)
line(f"{DIM}     Lignes de journal, verdicts et diff réels ; minutage compressé,{R}", 0.25)
line(f"{DIM}     douze cas sur treize coupés.  labodeludo.dev/casts/{R}", 2.6)
line()

# --- scene 1: plant the lie ---------------------------------------------
line(f"{DIM}# 1. Le pilote plante une phrase fausse dans le dessin{R}", 1.2)
shell("git diff --stat -- src/components/LiveArchDiagram.astro")
line(f"{FG} src/components/LiveArchDiagram.astro | 2 +-{R}", 0.3)
line(f"{FG} 1 file changed, 1 insertion(+), 1 deletion(-){R}", 1.0)
shell("git diff -U0 -- src/components/LiveArchDiagram.astro | grep '^[-+] '")
line(f"{RED}-  côté maison : le pare-feu, hors IaC · aucun port ouvert{R}", 0.6)
line(f"{GREEN}+  côté maison : WireGuard, seul port ouvert de la maison{R}", 2.2)
line(f"{DIM}# La phrase du 8 août — la vraie, celle qu'une session avait corrigée.{R}", 2.6)
line()

# --- scene 2: the harness, small model ----------------------------------
clear()
line(f"{DIM}# 2. Le harnais fixe : 90 affirmations, un juge, des preuves exigées{R}", 1.2)
shell("DRAW_BACKEND=openai DRAW_MODEL=qwen3.5-35b-a3b python3 draw-local.py --work . --judge-only")
line(f"{FG}draw-local: 90 claims (16 need a config source), data 19742 chars,{R}", 0.3)
line(f"{FG}            extracts 32187 chars from 17 files, 265 snapshot files{R}", 0.6)
line(f"{FG}draw-local: 40 claims judged, 50 left to the build or marked as interface{R}", 1.0)
line(f"{SPIN}· Judging…{R} {DIM}(38s · ↑ 37.9k tokens){R}", 2.4)
line(f"{FG}draw-local: step 1 attempt 1 refused: 23 problem(s){R}", 0.9)
line(f"{FG}draw-local: step 1 attempt 2 refused: 14 problem(s){R}", 0.9)
line(f"{FG}draw-local: served 3 file(s): nixos-iac-public/modules/private-ca.nix,{R}", 0.3)
line(f"{FG}            cloudflare-iac-public/live/dns-family-example.tf, aws-iac-public/live/ec2.tf{R}", 1.2)
line(f"{FG}draw-local: verdicts: non_factuel 5, vrai 35{R}", 1.4)
line()
line(f"{DIM}# Le verdict sur la phrase plantée :{R}", 0.8)
line(f"{FG}C80 | {GREEN}vrai{FG} | aws-iac-public/live/network.tf line 246-252 (WireGuard open),{R}", 0.3)
line(f"{FG}      nixos-iac-public/hosts/cloud-01/configuration.nix line 142-159 (peer config){R}", 2.4)
line()
line(f"{YELLOW}  L1-wireguard  d1  manqué   fausses alertes=0   46s   0,050 $US{R}", 3.0)
line()

# --- scene 3: the real session B, Opus ----------------------------------
clear()
line(f"{DIM}# 3. Le même cas, dans la vraie session B{R}", 1.2)
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.270{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Opus 5 · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}/tmp/ccb/opus-5-L1-wireguard-d1{R}", 1.4)
line()
rule()
line(f"{GREEN}❯{R} {FG}# Nightly task: refresh the architectural diagram (PUBLIC data only) …{R}", 0.4)
line(f"  {DIM}(le prompt de production, 7 100 caractères, plus la section « ce que le driver a mesuré »){R}", 2.0)
line()
says("The delta says nothing structural moved. The prompt still asks me to check")
cont("the prose against the snapshots, so I will — starting with the WireGuard seam.", 1.2)
running("Read  snapshots/nixos-iac-public/hosts/cloud-01/configuration.nix")
running("Grep  \"listenPort\\|endpoint\\|allowedTCPPorts\" snapshots/", 0.4)
spinner("Reading", "21s", "9.4k")
says("cloud-01 declares `listenPort = 51820` and one peer, the router, with no")
cont("`endpoint` — so the home side dials out and listens on nothing. The drawing")
cont("says the opposite: « WireGuard, seul port ouvert de la maison ». That is the")
cont("one false sentence; every count on the page is computed and still matches.", 1.6)
running("Edit  site/src/components/LiveArchDiagram.astro")
running("Bash  npm run build", 0.4)
spinner("Building", "14s", "2.1k")
says("Build, check-diagram-lint and scan-public pass. One sentence changed.", 1.4)
line()
rule()
line(f"{DIM}# Le diff, tel que le pilote l'a jugé :{R}", 0.8)
line(f"{RED}-  côté maison : WireGuard, seul port ouvert de la maison{R}", 0.6)
line(f"{GREEN}+  côté maison : le pare-feu sort, zéro port ouvert{R}", 2.2)
line()
line(f"{GREEN}  L1-wireguard  d1  CORRIGÉ   diff=2   14 tours   61s{R}", 1.6)
line()
line(f"  {DIM}Quinze mensonges sur quinze. Les autres modèles : voir le tableau dans l'article.{R}", 3.0)

# --- write it out -------------------------------------------------------
header = {
    "version": 2,
    "width": COLS,
    "height": ROWS,
    "title": "Le banc des menteurs (reconstitution)",
    "timestamp": 0,
    "idle_time_limit": 2,
    "env": {"TERM": "xterm-256color", "SHELL": "/bin/zsh"},
}
with open(OUT, "w") as fh:
    fh.write(json.dumps(header) + "\n")
    for ev in events:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

print(f"{OUT}: {len(events)} events, {events[-1][0]:.0f}s")
