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

import claude_tui as T
from claude_tui import BOLD, CYAN, DIM, FG, GREEN, PINK, R, RED, SPIN, YELLOW, calling, cont, line, prompt, says, spinner, waiting

T.setup(
    out="public/casts/iac-apply.cast",
    title="La porte anti-destroy refuse d'appliquer (reconstitution)",
    session="iac-auto-deploy",
    windows=["backlog", "iac-auto-deploy"],
    current="iac-auto-deploy",
    start="30-Jul-26 19:26:44",
    cwd="~/tmp",
    model="Fable 5 · Claude Max",
    version="v2.1.220",
    seed=7,
)

T.disclaimer("Demandes et messages réels, minutage compressé,",
             "noms d'hôte sanitisés.")
T.banner()


# L'ancien script rythmait ses réponses à 1,35 s par ligne : on garde son rythme.
def says(text, d=1.35):
    T.says(text, d)


def cont(text, d=1.35):
    T.cont(text, d)


def stop(text, detail=None, d=3.2):
    """Ancienne aide : le message d'arrêt en jaune, puis l'agent rend la main."""
    line(f"  {YELLOW}{BOLD}{text}{R}", 0.9)
    if detail:
        line(f"  {YELLOW}{detail}{R}", 0.6)
    waiting()
    pause_ = d - 1.2
    if pause_ > 0:
        T.pause(pause_)

# --- 1. the ask ---------------------------------------------------------
prompt("hey, can we start building the auto deployment through github actions of all iac projects?")
says("The backlog already answers the design questions: plan on PR, apply on")
cont("merge, and never auto-apply a plan that contains destroys — a delete", 1.15)
cont("stops the job and waits for a human. Weakest blast radius first.", 2.6)

# --- 2. the design conversation: picking a tool per repo -----------------
prompt("hey i want to do gitops, like argocd or flux. would that be better than github actions?")
says("It fits per layer, not wholesale. k3s-iac is plain YAML — exactly what")
cont("these controllers are built for. The tofu repos are not: the extensions", 1.15)
cont("that run tofu in-cluster are the orphaned corner of that ecosystem, and", 1.15)
cont("you'd lose plan-as-PR-comment with a destroy gate before merge.", 2.8)

prompt("if we use gitops everywhere, can we still gate the prs?")
says("Yes — but the gate is CI at PR time no matter what: controllers only")
cont("ever see main. GitOps never replaces the PR half; it only changes who", 1.15)
cont("holds the apply credentials.", 2.8)

prompt("ok so what is the benefit of using gitops at all then, instead of github hosted runners?")
says("For the tofu repos: essentially none — their APIs are public. For the")
cont("cluster it's concrete: a hosted runner can't reach the k3s API at all,", 1.15)
cont("and a controller that pulls means no kubeconfig ever leaves the lab.", 2.8)

prompt("Why are you recommending Argo over Flux?")
says("Flux's whole design is continuous reconciliation — it re-applies on an")
cont("interval, git change or not. It would have re-scaled your eleven", 1.15)
cont("deliberately-stopped workloads on the next tick and called it", 1.15)
cont("convergence. Argo with selfHeal off applies on merge, and only then.", 2.8)
line()
says("So: cloudflare-iac + aws-iac → GitHub Actions with OIDC and the destroy")
cont("gate · k3s-iac → Argo CD, no selfHeal, no prune · nixos-iac → comin,", 1.15)
cont("each host pulls and builds itself. Canary first, control plane last.", 2.2)

prompt("I can already validate the diff when we do the pr. I don't need another validation after we've merged to main. Are you still recommending Argo?")
says("Yes — auto-sync without selfHeal gives exactly those semantics: apply")
cont("when git changes, and otherwise leave the cluster alone. Flux's", 1.1)
cont("interval loop is precisely the post-merge validation you don't want.", 3.0)
stop("Plan ready — approve it to start building.")
line(f"{DIM}  → plan approved{R}", 1.6)
line()
calling("Write", 9)
calling("Bash", 14)
spinner("Building", "38m", "112k")
says("Done: OIDC roles + workflows in both tofu repos, Argo CD app-of-apps")
cont("live on the cluster (16 apps synced, zero pod restarts), comin canary", 1.1)
cont("deployed on vm-01. Now let's prove the gate instead of trusting it.", 3.0)

# --- 3. jump cut: the destroy-gate test ---------------------------------
T.separator("plus tard dans la session : tester la porte pour vrai", 1.6)
says("PR #2 is open: it deletes the throwaway TXT record created by PR #1.")
cont("The plan comment flags it loudly:", 1.0)
line(f"  {SPIN}⛔ Plan contains 1 destroy — the apply workflow will refuse this{R}", 0.5)
line(f"  {SPIN}   cloudflare_dns_record.cicd_test_txt{R}", 1.6)
stop("Merge PR #2 — the apply run must FAIL at the destroy gate.")

prompt("done")
calling("Bash", 2)
spinner("Watching the apply run", "1m 04s", "1.2k")
says("The run failed exactly where it should:", 1.15)
line(f"  {SPIN}##[error] Plan contains destroys — refusing to auto-apply.{R}", 0.5)
line(f"  {SPIN}          A human must run this.{R}", 0.5)
line(f"  {SPIN}cloudflare_dns_record.cicd_test_txt  (_cicd-test.pub.example.com){R}", 1.8)
says("The gate held. The record still exists; git says delete; closing that")
cont("gap is now deliberate human work — which is the whole point.", 2.4)

# --- 3. jump cut: comin deploys with nobody home ------------------------
T.separator("plus tard encore : le même merge, côté NixOS", 1.6)
prompt("merged the prs")
calling("Bash", 1)
spinner("Watching vm-01", "1m 12s", "0.8k")
line(f"  {GREEN}deployer: deploying generation 88ec6151 (switch){R}", 0.4)
line(f"  {GREEN}nix: deployment ended{R}", 1.4)
says("vm-01 picked up the merge on its own: fetched master, evaluated,")
cont("switched — three seconds of work, one poll after the merge, no hands.", 1.2)
cont("configurationRevision now equals origin/master.", 2.0)
line()
line(f"{DIM}  Le bouton merge est devenu le bouton deploy.{R}", 3.5)

T.save()
