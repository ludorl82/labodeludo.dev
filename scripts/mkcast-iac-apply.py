#!/usr/bin/env python3
"""Build the asciicast for the IaC auto-deployment article.

Condensed from the real session transcript (2026-07-30, session
"iac-auto-deploy"). The prompts and Claude's stop messages are taken from
that session; the timing is compressed and the long CI-watch loops cut.

Two moments, jump-cut together:

1. The destroy gate, live: a PR deleting a throwaway DNS record is merged,
   and the apply workflow REFUSES it — the whole design in one red line.
2. The payoff: a merged nixos-iac change is deployed by comin on vm-01
   (worker3) with nobody at the keyboard.

Names sanitized per the shared host map (worker3 → vm-01, tptpt.net →
pub.example.com). The record shown was a throwaway created for this test
and no longer exists in any form.

Palette and line grammar per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-iac-apply.py
"""
import json
import random

OUT = "public/casts/iac-apply.cast"
COLS, ROWS = 96, 22
random.seed(7)  # keep regenerated casts byte-stable

# --- palette sampled from the terminal screenshots ----------------------
FG = "\x1b[38;5;253m"  # #d8d8d8 body text
DIM = "\x1b[38;5;246m"  # #949494 secondary
YELLOW = "\x1b[38;5;220m"  # #ffd700 headings / warnings
GREEN = "\x1b[38;5;114m"  # #87d787 ok / prompt
SPIN = "\x1b[38;5;174m"  # #d78787 spinner, and the refusal lines here
CYAN = "\x1b[38;5;37m"  # #00afaf rule + branch
PINK = "\x1b[38;5;217m"  # logo
BOLD = "\x1b[1m"
R = "\x1b[0m"

BRANCH = "iac-auto-deploy"

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
line(f"{YELLOW}  ⚠  Reconstitution condensée — pas une capture en direct.{R}", 0.25)
line(f"{DIM}     Demandes et messages réels, minutage compressé,{R}", 0.25)
line(f"{DIM}     noms d'hôte sanitisés.  labodeludo.dev/casts/{R}", 2.6)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.220{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Fable 5 · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/tmp{R}", 1.4)
line()

# --- 1. the ask ---------------------------------------------------------
prompt("hey, can we start building the auto deployment through github actions of all iac projects?")
says("The backlog already answers the design questions: plan on PR, apply on")
cont("merge, and never auto-apply a plan that contains destroys — a delete", 0.8)
cont("stops the job and waits for a human. Weakest blast radius first.", 1.8)

# --- 2. the design conversation: picking a tool per repo -----------------
prompt("hey i want to do gitops, like argocd or flux. would that be better than github actions?")
says("It fits per layer, not wholesale. k3s-iac is plain YAML — exactly what")
cont("these controllers are built for. The tofu repos are not: the extensions", 0.8)
cont("that run tofu in-cluster are the orphaned corner of that ecosystem, and", 0.8)
cont("you'd lose plan-as-PR-comment with a destroy gate before merge.", 1.8)

prompt("if we use gitops everywhere, can we still gate the prs?")
says("Yes — but the gate is CI at PR time no matter what: controllers only")
cont("ever see main. GitOps never replaces the PR half; it only changes who", 0.8)
cont("holds the apply credentials.", 1.8)

prompt("ok so what is the benefit of using gitops at all then, instead of github hosted runners?")
says("For the tofu repos: essentially none — their APIs are public. For the")
cont("cluster it's concrete: a hosted runner can't reach the k3s API at all,", 0.8)
cont("and a controller that pulls means no kubeconfig ever leaves the lab.", 1.8)

prompt("Why are you recommending Argo over Flux?")
says("Flux's whole design is continuous reconciliation — it re-applies on an")
cont("interval, git change or not. It would have re-scaled your eleven", 0.8)
cont("deliberately-stopped workloads on the next tick and called it", 0.8)
cont("convergence. Argo with selfHeal off applies on merge, and only then.", 1.8)
line()
says("So: cloudflare-iac + aws-iac → GitHub Actions with OIDC and the destroy")
cont("gate · k3s-iac → Argo CD, no selfHeal, no prune · nixos-iac → comin,", 0.8)
cont("each host pulls and builds itself. Canary first, control plane last.", 2.2)

# --- 3. jump cut: the destroy-gate test ---------------------------------
line(f"{DIM}  ── plus tard dans la session : tester la porte pour vrai ──{R}", 1.6)
line()
says("PR #2 is open: it deletes the throwaway TXT record created by PR #1.")
cont("The plan comment flags it loudly:", 1.0)
line(f"  {SPIN}⛔ Plan contains 1 destroy — the apply workflow will refuse this{R}", 0.5)
line(f"  {SPIN}   cloudflare_dns_record.cicd_test_txt{R}", 1.6)
stop("Merge PR #2 — the apply run must FAIL at the destroy gate.")

prompt("done", d=1.2)
calling("Bash", 2)
spinner("Watching the apply run", "1m 04s", "1.2k")
says("The run failed exactly where it should:", 0.8)
line(f"  {SPIN}##[error] Plan contains destroys — refusing to auto-apply.{R}", 0.5)
line(f"  {SPIN}          A human must run this.{R}", 0.5)
line(f"  {SPIN}cloudflare_dns_record.cicd_test_txt  (_cicd-test.pub.example.com){R}", 1.8)
says("The gate held. The record still exists; git says delete; closing that")
cont("gap is now deliberate human work — which is the whole point.", 2.4)

# --- 3. jump cut: comin deploys with nobody home ------------------------
line(f"{DIM}  ── plus tard encore : le même merge, côté NixOS ──{R}", 1.6)
line()
prompt("merged the prs", d=1.2)
calling("Bash", 1)
spinner("Watching vm-01", "1m 12s", "0.8k")
line(f"  {GREEN}deployer: deploying generation 88ec6151 (switch){R}", 0.4)
line(f"  {GREEN}nix: deployment ended{R}", 1.4)
says("vm-01 picked up the merge on its own: fetched master, evaluated,")
cont("switched — three seconds of work, one poll after the merge, no hands.", 1.2)
cont("configurationRevision now equals origin/master.", 2.0)
line()
line(f"{DIM}  Le bouton merge est devenu le bouton deploy.{R}", 3.5)

# --- write --------------------------------------------------------------
header = {
    "version": 2,
    "width": COLS,
    "height": ROWS,
    "title": "La porte anti-destroy refuse d'appliquer (reconstitution)",
    "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"},
    "idleTimeLimit": 2,
}
with open(OUT, "w") as f:
    f.write(json.dumps(header) + "\n")
    for e in events:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

print(f"{OUT}: {len(events)} events, {events[-1][0]:.1f}s")
