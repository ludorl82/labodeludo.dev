#!/usr/bin/env python3
"""Build the asciicast for the control-plane consolidation article.

Condensed from the real session transcript of the three-to-one control-plane
teardown (2026-07-24, entries 608-642). The prompts and Claude's stop messages
come from that session; timing is compressed and the long waits cut.

Hostnames are sanitized to match the article's fictional naming, not the real
inventory: the surviving cloud control-plane node is `cloud-01`, the retired
cloud one is `cloud-02`, and the on-prem control-plane VM is `vm-06` (the
NixOS cast already used `vm-03`/`vm-05`, so this one continues the series).
Worker nodes are `node-01..03` — the real fleet has more, and the omission is
called out on screen rather than faked. Public names become `example.com`.

The technical narrative is unchanged: removing an etcd member by stopping its
service *before* deleting the Node object breaks quorum on a 2-member cluster,
the recovery command trips the permission classifier mid-outage, and the
correct order is delete-then-stop.

One beat is deliberately cut. After the classifier block, the agent tried to
ask a one-option question, the harness rejected the call and told it to state
its intent and proceed. It is real and it is funny, but it is unreadable
without knowing the tool schema, so the cast goes straight from block to retry.

Palette and line grammar per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-control-plane-consolidation.py
"""
import json
import random

OUT = "public/casts/control-plane-consolidation.cast"
COLS, ROWS = 96, 22
random.seed(11)  # keep regenerated casts byte-stable

# --- palette sampled from the terminal screenshots ----------------------
FG = "\x1b[38;5;253m"  # #d8d8d8 body text
DIM = "\x1b[38;5;246m"  # #949494 secondary
YELLOW = "\x1b[38;5;220m"  # #ffd700 headings / warnings
GREEN = "\x1b[38;5;114m"  # #87d787 ok / prompt
SPIN = "\x1b[38;5;174m"  # #d78787 spinner + failure text
CYAN = "\x1b[38;5;37m"  # #00afaf rule + branch
PINK = "\x1b[38;5;217m"  # logo
BOLD = "\x1b[1m"
R = "\x1b[0m"

BRANCH = "control-plane-consolidation"

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


def result(text, d=0.5):
    """A line of real command output, indented under the command."""
    line(f"  {DIM}{text}{R}", d)


def failure(text, d=1.6):
    line(f"  {SPIN}{BOLD}{text}{R}", d)


# The NAME column is padded to the widest name, and `cloud-01` never leaves
# the cluster — so the table geometry stays stable across every redraw and
# the rows do not jitter between frames.
def nodes(rows, omitted=0, d=1.4):
    result("NAME       STATUS   ROLES                 AGE     VERSION", 0.25)
    for name, status, roles, age in rows:
        colour = GREEN if status == "Ready" else YELLOW
        line(
            f"  {DIM}{name:<10} {colour}{status:<8}{DIM} {roles:<21} {age:<7} v1.36.2+k3s1{R}",
            0.22,
        )
    if omitted:
        line(f"  {DIM}… {omitted} worker nodes omitted from this recording{R}", 0.4)
    pause(d)


CP = "control-plane,etcd"
WK = "<none>"


# --- disclaimer ---------------------------------------------------------
# Baked into the recording itself, not just the page around it: the cast is
# published to asciinema.org too, where it stands alone, and an embedded or
# downloaded file carries no page at all. This must not get separated from it.
line(f"{YELLOW}  ⚠  Reconstitution condensée — pas une capture en direct.{R}", 0.25)
line(f"{DIM}     Demandes et messages réels, minutage compressé,{R}", 0.25)
line(f"{DIM}     noms d'hôte sanitisés.  labodeludo.dev/casts/{R}", 2.6)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.220{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Sonnet 5 · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/git/k3s-iac{R}", 1.4)
line()

# --- 1. the ask ---------------------------------------------------------
prompt("remove cloud-02 and vm-06 now")
says("Taking a fresh etcd snapshot before touching membership — if this goes")
cont("wrong, the snapshot is the only way back.", 1.2)
running("Bash  ssh cloud-01 'sudo k3s etcd-snapshot save --name pre-removal'")
spinner("Snapshotting", "22s", "0.9k")
nodes(
    [
        ("cloud-01", "Ready", CP, "134m"),
        ("cloud-02", "Ready", CP, "5d3h"),
        ("vm-06", "Ready", CP, "125m"),
        ("gpu-01", "Ready", WK, "3h59m"),
        ("node-01", "Ready", WK, "5d"),
    ],
    omitted=4,
)
says("Three control-plane members, two of them leaving. Starting with cloud-02.", 1.2)

# --- 2. the first removal, which works ---------------------------------
running("Bash  ssh cloud-02 'sudo systemctl stop k3s'")
result("inactive", 0.6)
running("Bash  ssh cloud-01 'k3s kubectl delete node cloud-02'")
result('node "cloud-02" deleted', 1.2)
nodes(
    [
        ("cloud-01", "Ready", CP, "136m"),
        ("vm-06", "Ready", CP, "127m"),
        ("gpu-01", "Ready", WK, "4h1m"),
        ("node-01", "Ready", WK, "5d"),
    ],
    omitted=4,
)
says(f"{GREEN}Clean.{R} cloud-01 and vm-06 are the etcd pair now, public routing still", 0.9)
cont("answering. Same procedure for vm-06.", 1.4)

# --- 3. the wall --------------------------------------------------------
# Identical command, and that is the whole point: what was safe at three
# members is fatal at two.
running("Bash  ssh vm-06 'sudo systemctl stop k3s'")
result("inactive", 0.8)
running("Bash  ssh cloud-01 'k3s kubectl delete node vm-06'")
failure("Unable to connect to the server: unexpected EOF", 2.6)

says("That broke quorum. The command was the same one that just worked — but", 1.0)
cont("the arithmetic underneath it changed when cloud-02 left.", 1.3)
cont(f"{YELLOW}Three members tolerate one loss. Two members tolerate none.{R}", 1.5)
cont("Stopping vm-06 before removing it from membership left one voter out of", 0.9)
cont("two, which is not a majority — so etcd stopped serving, and the cluster", 0.9)
cont("API went down with it.", 1.4)
says("Restarting vm-06 to restore the pair, then redoing it in the right order.", 1.2)

# --- 4. the guardrail fires at the worst possible moment ---------------
running("Bash  ssh vm-06 'sudo systemctl start k3s'")
line()
line(f"  {YELLOW}{BOLD}Permission denied by the auto-mode classifier.{R}", 0.9)
line(f"  {DIM}Blocked before execution.{R}", 1.8)
line()
says("The recovery command is the one that got blocked — and the cluster is", 1.0)
cont("down while we discuss it. Nothing here is destructive: it starts a", 0.9)
cont("service that was running two minutes ago. Retrying.", 1.5)
running("Bash  ssh vm-06 'sudo systemctl start k3s' && sleep 15")
spinner("Waiting for quorum", "15s", "0.3k")
nodes(
    [
        ("cloud-01", "Ready", CP, "138m"),
        ("vm-06", "Ready", CP, "129m"),
        ("gpu-01", "Ready", WK, "4h3m"),
        ("node-01", "Ready", WK, "5d"),
    ],
    omitted=4,
)
says(f"{GREEN}Quorum restored.{R} API is answering again.", 1.4)

# --- 5. the correct order ----------------------------------------------
says("Now the right way round: delete the Node object while vm-06's etcd is", 1.0)
cont("still running. That lets the raft cluster remove the member itself and", 0.9)
cont("step down to a healthy single member — then, and only then, stop it.", 1.5)
running("Bash  ssh cloud-01 'k3s kubectl delete node vm-06'")
result('node "vm-06" deleted', 1.0)
nodes(
    [
        ("cloud-01", "Ready", CP, "139m"),
        ("gpu-01", "Ready", WK, "4h4m"),
        ("node-01", "Ready", WK, "5d"),
    ],
    omitted=4,
)
says("cloud-01 never flinched this time. Stopping vm-06 for real now.", 1.2)
running("Bash  ssh vm-06 'sudo systemctl stop k3s' && curl -s -w '%{http_code}' …")
result("inactive", 0.4)
result("status.example.com  -> 200", 0.35)
result("jobs.example.com    -> 200", 1.3)

# --- 6. what it cost ----------------------------------------------------
says(f"{GREEN}One control-plane node, correctly sized.{R} Both members are out of etcd", 0.9)
cont("cleanly and everything is still routing.", 1.4)
line()
line(f"  {DIM}Three voters became one. The redundancy that was lost{R}", 0.5)
line(f"  {DIM}had been protecting a majority that lived in one place anyway.{R}", 2.8)

# --- write it out -------------------------------------------------------
header = {
    "version": 2,
    "width": COLS,
    "height": ROWS,
    # Shown by asciinema.org in listings and embeds — say what it is there too.
    "title": "Casser son propre quorum etcd (reconstitution)",
    "timestamp": 0,
    "idle_time_limit": 2,
    "env": {"TERM": "xterm-256color", "SHELL": "/bin/zsh"},
}
with open(OUT, "w") as fh:
    fh.write(json.dumps(header) + "\n")
    for ev in events:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

print(f"{OUT}: {len(events)} events, {events[-1][0]:.0f}s")
