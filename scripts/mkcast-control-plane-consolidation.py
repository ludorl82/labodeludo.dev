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

import claude_tui as T
from claude_tui import BOLD, DIM, GREEN, R, RED, YELLOW, cont, line, prompt, says, spinner

T.setup(
    out="public/casts/control-plane-consolidation.cast",
    title="Casser son propre quorum etcd (reconstitution)",
    session="control-plane-consolidation",
    windows=["backlog", "control-plane-consolidation"],
    current="control-plane-consolidation",
    start="24-Jul-26 15:42:18",
    cwd="~/git/k3s-iac",
    model="Sonnet 5 · Claude Max",
    seed=11,
)


# The NAME column is padded to the widest name, and `cloud-01` never leaves
# the cluster — so the table geometry stays stable across every redraw and
# the rows do not jitter between frames.
def nodes(rows, omitted=0, d=2.2):
    line(f"  {DIM}NAME       STATUS   ROLES                 AGE     VERSION{R}", 0.35)
    for name, status, roles, age in rows:
        colour = GREEN if status == "Ready" else YELLOW
        line(
            f"  {DIM}{name:<10} {colour}{status:<8}{DIM} {roles:<21} {age:<7} v1.36.2+k3s1{R}",
            0.3,
        )
    if omitted:
        line(f"  {DIM}… {omitted} worker nodes omitted from this recording{R}", 0.6)
    T.pause(d)


CP = "control-plane,etcd"
WK = "<none>"

T.disclaimer("Demandes et messages réels, minutage compressé,",
             "noms d'hôte sanitisés.")
T.banner()

# --- 1. the ask ---------------------------------------------------------
prompt("remove cloud-02 and vm-06 now")
says("Taking a fresh etcd snapshot before touching membership — if this goes")
cont("wrong, the snapshot is the only way back.", 1.2)
line()
line(f"  {DIM}Bash  ssh cloud-01 'sudo k3s etcd-snapshot save --name pre-removal'{R}", 0.7)
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
line()
line(f"  {DIM}Bash  ssh cloud-02 'sudo systemctl stop k3s'{R}", 0.7)
line(f"  {DIM}inactive{R}", 0.6)
line()
line(f"  {DIM}Bash  ssh cloud-01 'k3s kubectl delete node cloud-02'{R}", 0.7)
line(f'  {DIM}node "cloud-02" deleted{R}', 1.7)
nodes(
    [
        ("cloud-01", "Ready", CP, "136m"),
        ("vm-06", "Ready", CP, "127m"),
        ("gpu-01", "Ready", WK, "4h1m"),
        ("node-01", "Ready", WK, "5d"),
    ],
    omitted=4,
)
says(f"{GREEN}Clean.{R} cloud-01 and vm-06 are the etcd pair now, public routing still", 1.2)
cont("answering. Same procedure for vm-06.", 2.2)

# --- 3. the wall --------------------------------------------------------
# Identical command, and that is the whole point: what was safe at three
# members is fatal at two.
line()
line(f"  {DIM}Bash  ssh vm-06 'sudo systemctl stop k3s'{R}", 0.7)
line(f"  {DIM}inactive{R}", 0.8)
line()
line(f"  {DIM}Bash  ssh cloud-01 'k3s kubectl delete node vm-06'{R}", 0.7)
line(f"  {RED}{BOLD}Unable to connect to the server: unexpected EOF{R}", 4.0)

says("That broke quorum. Same command as a minute ago — but stopping a member", 1.3)
cont("is not the same thing as removing one.", 2.2)
cont(f"{YELLOW}`systemctl stop` does not shrink etcd's membership.{R}", 1.2)
cont(f"{YELLOW}The member stays on the roster; it just stops answering.{R}", 2.8)
cont("And quorum is a majority of the roster — not of whatever is alive:", 1.6)
line()
line(f"    {DIM}roster 3 · 2 alive · needs 2   {GREEN}✓  the first removal{R}", 1.4)
line(f"    {DIM}roster 2 · 1 alive · needs 2   {RED}✗  this one{R}", 3.4)
line()
cont("Deleting the Node object is what actually shrinks the roster — and that", 1.1)
cont("needs a working cluster to carry out. Which is now down.", 2.6)
says("Restarting vm-06 to restore the pair, then redoing it in the right order.", 1.8)

# --- 4. the guardrail fires at the worst possible moment ---------------
line()
line(f"  {DIM}Bash  ssh vm-06 'sudo systemctl start k3s'{R}", 0.7)
T.denied("Blocked before execution.", 3.6)
line()
says("The recovery command is the one that got blocked — and the cluster is", 1.3)
cont("down while we discuss it. Nothing here is destructive: it starts a", 0.9)
cont("service that was running two minutes ago. Retrying.", 2.2)
line()
line(f"  {DIM}Bash  ssh vm-06 'sudo systemctl start k3s' && sleep 15{R}", 0.7)
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
says(f"{GREEN}Quorum restored.{R} API is answering again.", 2.8)

# --- 5. the correct order ----------------------------------------------
says("Now the right way round: delete the Node object while vm-06 is still", 1.1)
cont("running, so the roster shrinks from 2 to 1 with quorum intact the whole", 1.1)
cont("way. At a roster of 1, cloud-01 alone is a majority — and only then is", 1.2)
cont("stopping vm-06 harmless.", 2.6)
line()
line(f"  {DIM}Bash  ssh cloud-01 'k3s kubectl delete node vm-06'{R}", 0.7)
line(f'  {DIM}node "vm-06" deleted{R}', 1.7)
nodes(
    [
        ("cloud-01", "Ready", CP, "139m"),
        ("gpu-01", "Ready", WK, "4h4m"),
        ("node-01", "Ready", WK, "5d"),
    ],
    omitted=4,
)
says("cloud-01 never flinched this time. Stopping vm-06 for real now.", 1.8)
line()
line(f"  {DIM}Bash  ssh vm-06 'sudo systemctl stop k3s' && curl -s -w '%{{http_code}}' …{R}", 0.7)
line(f"  {DIM}inactive{R}", 0.4)
line(f"  {DIM}status.example.com  -> 200{R}", 0.35)
line(f"  {DIM}jobs.example.com    -> 200{R}", 2.2)

# --- 6. what it cost ----------------------------------------------------
says(f"{GREEN}One control-plane node, correctly sized.{R} Both members are out of etcd", 0.9)
cont("cleanly and everything is still routing.", 2.4)
line()
line(f"  {DIM}Three voters became one. The redundancy that was lost{R}", 1.1)
line(f"  {DIM}had been protecting a majority that lived in one place anyway.{R}", 4.0)

T.save()
