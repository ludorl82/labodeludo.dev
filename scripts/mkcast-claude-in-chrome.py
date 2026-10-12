#!/usr/bin/env python3
"""Build the asciicast for the Claude in Chrome article.

Condensed from the real session transcript (2026-07-26, 01:26→15:10). The
prompts and Claude's stop messages are taken from that session; the timing is
compressed and the long waits cut. Hostnames sanitized.

Palette and line grammar are sampled from the real terminal screenshots that
also appear in the article: Alacritty on #181818, the `● …` assistant bullet,
the `Calling claude-in-chrome N times…` line, and the `· Gerund… (…tokens)`
spinner.

Run from the repo root:  python3 scripts/mkcast-claude-in-chrome.py
"""

import claude_tui as T
from claude_tui import BOLD, DIM, GREEN, R, SPIN, YELLOW, calling, cont, line, prompt, says, spinner, waiting

T.setup(
    out="public/casts/claude-in-chrome-nas.cast",
    title="Claude in Chrome — migration NFS vers SSD (reconstitution)",
    session="nas-nfs-recommendation",
    windows=["backlog", "nas-nfs-recommendation"],
    current="nas-nfs-recommendation",
    start="26-Jul-26 01:26:12",
    cwd="~/tmp",
    model="Fable 5 · Claude Max",
    seed=7,
)

# Baked into the recording itself, not just the page around it: the cast is
# published to asciinema.org too, where it stands alone, and an embedded or
# downloaded file carries no page at all. This must not get separated from it.
T.disclaimer("Demandes et messages réels, minutage compressé,",
             "noms d'hôte sanitisés.")
T.banner()

# --- 1. the ask ---------------------------------------------------------
prompt(
    "the ssd drive is added to the nas, please configure it with claude in chrome",
    "and migrate the nfs mounts to the 480GB ssd i added",
)
says("The SSD needs a volume, a shared folder, then a careful data migration")
cont("that preserves ownership — Postgres and Mongo data live on those shares.", 1.1)
calling("claude-in-chrome", 1)
spinner("Inspecting", "22s", "1.4k")

# --- 2. hard limit: no passwords ---------------------------------------
says("The QTS session has expired — the NAS rebooted during the swap, and")
cont("it's now at the login prompt asking for the admin password.", 1.2)
line()
line(f"  {YELLOW}{BOLD}I can't type a password into a login form. That's a hard limit.{R}", 0.9)
line(f"  {YELLOW}Sign in at https://nas.example.com and tell me when you're in.{R}", 0.6)
waiting()

prompt("ok i'm logged in, go ahead")
says("Logged in. Opening Storage & Snapshots to confirm the SSD is detected.", 1.0)
calling("claude-in-chrome", 6)
spinner("Navigating", "48s", "3.1k")

# --- 3. it stops on its own -------------------------------------------
says("SSD detected in bay 1 — Kingston SA400S37480G, 447 GB. But the volume")
cont('count went to 2, with a new "Volume hérité" row, and its usage bar is', 0.75)
cont("completely full. That suggests the SSD isn't blank.", 1.1)
calling("claude-in-chrome", 4)
spinner("Verifying", "1m 06s", "4.8k")
line()
line(f"  {YELLOW}{BOLD}Stopping before I configure anything: that SSD is not blank.{R}", 0.9)
line(f"  {YELLOW}436.98 GB already on it. Wipe it, or did you mean a different disk?{R}", 0.6)
waiting()

prompt("please just wipe it")
says("Authorization noted — proceeding with the wipe.", 1.0)
calling("claude-in-chrome", 9)
spinner("Transfiguring", "2m 14s", "6.2k")
says("The confirmation targeted the correct volume — 446.25 Go, no shared", 0.75)
cont("folders, no apps. Legacy volume deleted.", 1.2)
says("Creating a static volume: best performance on a 2 GB ARM NAS, and it", 0.75)
cont("matches DataVol1. Encryption off — it would need a passphrase at every", 0.75)
cont("boot, which would break unattended NFS.", 1.1)
calling("claude-in-chrome", 11)
spinner("Formatting", "4m 59s", "4.2k")
says("DataVol2 ready — 385.29 Go usable after QTS reserves 10% for SSD", 0.75)
cont("over-provisioning.", 1.6)

# --- 4. the zoom irritant ----------------------------------------------
says("The page zoom jumped unexpectedly. Let me reset it.", 1.0)
calling("claude-in-chrome", 1)
line(f"  {SPIN}error: page zoom shortcuts are not supported{R}", 1.3)
says("Page zoom is stuck at 225% — innerWidth 696 against outerWidth 1536 —", 0.75)
cont("and the zoom shortcuts are blocked for me. No shortcuts available, and", 0.75)
cont("resizing the window would overflow the screen.", 1.2)
says("Everything destructive is already done and verified, so this is a safe", 0.75)
cont("place to stop.", 1.1)
line()
line(f"  {YELLOW}{BOLD}Please press Ctrl+0 in the NAS tab to reset the page zoom.{R}", 0.9)
line(f"  {YELLOW}Guessing at coordinates in a storage manager is not a strategy.{R}", 0.6)
waiting()

prompt("done, zoom is reset")
says("Zoom is reset — viewport back to 1536. Continuing.", 1.4)

# --- 5. the actual trick -----------------------------------------------
says("Reading the k8s share's export options before touching anything.", 1.0)
calling("claude-in-chrome", 5)
spinner("Reading", "1m 31s", "2.7k")
says('Squash is "N\'écraser aucun utilisateur" — a root-level rsync will', 0.75)
cont("preserve ownership. That's what makes the copy safe.", 1.3)
says("Renaming k8s → k8s-hdd, so the name k8s frees up for the SSD share.", 1.0)
calling("claude-in-chrome", 7)
spinner("Renaming", "1m 12s", "2.2k")
says("Renamed. New k8s share created on DataVol2.", 1.4)
line()
line(f"  {GREEN}{BOLD}Export path unchanged: /share/k8s{R}", 0.9)
line(f"  {GREEN}→ zero Kubernetes objects to modify. Not one PV, not the{R}", 0.5)
line(f"  {GREEN}  StorageClass, not the provisioner.{R}", 2.0)
line()
line(f"{DIM}  Data copy, verification and cluster restart continue over SSH.{R}", 3.5)

T.save()
