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

import claude_tui as T
from claude_tui import BOLD, DIM, FG, GREEN, R, RED, YELLOW, calling, cont, line, prompt, says, spinner, waiting

T.setup(
    out="public/casts/nas-pull-the-plug.cast",
    title="Débrancher le NAS pour la science (reconstitution)",
    session="liveness-probes",
    windows=["backlog", "liveness-probes"],
    current="liveness-probes",
    start="30-Jul-26 13:26:04",
    cwd="~/tmp",
    model="Opus 5 with high effort · Claude Max",
    seed=7,
)

T.disclaimer("Demandes et messages réels, minutage compressé,",
             "noms d'hôte sanitisés.")
T.banner()

# --- 1. the ask ---------------------------------------------------------
prompt("Can you please add liveness probes to all our k3s-iac apps? I want to make",
       "sure we don't have zombie pods running when we yank the nfs volume storage.")
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
prompt("i yanked the power on the nas. any clue why the pods are all still marked",
       "as ready?")
calling("Bash", 2)
spinner("Sampling", "28s", "1.8k")
line(f"  {FG}cronicle  {RED}0/1{R}   {FG}grafana  {RED}0/1{R}   {FG}n8n  {RED}0/1{R}   {FG}nginx  {RED}0/1{R}", 0.7)
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
line(f"  {RED}loki: CrashLoopBackOff (restarts 4 → 6){R}", 1.8)
says("loki can't replay its WAL: it deletes segment files it still holds")
cont("open, NFS turns that into a silly-rename to .nfsXXXX, and the rmdir", 0.8)
cont("dies with ENOTEMPTY. Every restart regenerates the failure — a stable", 0.8)
cont("equilibrium, not residue. Waiting will not fix it.", 1.6)
calling("Bash", 1)
T.denied("kubectl exec loki-fix", 0.8)
line(f"       {DIM}-- mv /loki/…/wal /loki/…/wal.broken{R}", 1.4)
line()
line(f"  {YELLOW}{BOLD}I need to stop and get your call on one command.{R}", 0.9)
line(f"  {YELLOW}mv on loki's data volume — blocked, reasonably. Risk is nil: all{R}", 0.6)
waiting()
prompt("go ahead")
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
prompt("i unplugged and replugged the nas. please monitor if everything happens",
       "as expected")
calling("Bash", 3)
spinner("Monitoring", "8m", "6.1k")
line(f"  {FG}detection   {GREEN}6/6 NFS workloads NotReady{R}", 0.6)
line(f"  {FG}loki        {GREEN}ready=true restarts=0 — immune, correctly this time{R}", 0.6)
line(f"  {FG}recovery    {GREEN}all containers Ready ~3 min after NFS answered{R}", 0.6)
line(f"  {FG}interventions  {GREEN}zero{R}", 2.2)
line()
line(f"{DIM}  Three power cuts in one afternoon. The last one was boring.{R}", 3.5)

T.save()
