#!/usr/bin/env python3
"""Build the asciicast for the blind-BIOS saga (l'hyperviseur's conversion).

Condensed from the real session transcript of the gaming tower's migration
(2026-08). The prompts and Claude's messages come from that session; timing is
compressed, the long waits and several detours (an HA cutover, a credential
rotation) are cut.

Hostnames are sanitized to match the article's fictional naming: the tower is
`hyperviseur`, its BMC `hyperviseur-bmc`, and the fleet's build box is `gpu-01`. The
technical narrative — Setup that renders nothing over serial, keystrokes that
were never arriving, the MEBx wrong turn, Load Optimized Defaults bricking the
boot, and the virtual-media escape hatch — is unchanged.

Palette and line grammar per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-bios-blind.py
"""
import json
import random

OUT = "public/casts/bios-blind.cast"
COLS, ROWS = 96, 22
random.seed(7)  # keep regenerated casts byte-stable

# --- palette sampled from the terminal screenshots ----------------------
FG = "\x1b[38;5;253m"  # #d8d8d8 body text
DIM = "\x1b[38;5;246m"  # #949494 secondary
YELLOW = "\x1b[38;5;220m"  # #ffd700 headings / warnings
GREEN = "\x1b[38;5;114m"  # #87d787 ok / prompt
SPIN = "\x1b[38;5;174m"  # #d78787 spinner
CYAN = "\x1b[38;5;37m"  # #00afaf rule + branch
PINK = "\x1b[38;5;217m"  # logo
BOLD = "\x1b[1m"
R = "\x1b[0m"

BRANCH = "nixos-hyperviseur"

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


# --- disclaimer ---------------------------------------------------------
line(f"{YELLOW}  ⚠  Reconstitution condensée — pas une capture en direct.{R}", 0.25)
line(f"{DIM}     Demandes et messages réels, minutage compressé,{R}", 0.25)
line(f"{DIM}     noms d'hôte sanitisés.  labodeludo.dev/casts/{R}", 2.6)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.225{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Opus 4.8 · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/git/nixos-iac{R}", 1.4)
line()

# --- 1. the ask: no screen, drive the BIOS anyway ------------------------
prompt("please try guessing the post sequence to disable secure boot")
says("The manual gives me the exact structure — tabs are Main, Advanced,")
cont("Event Logs, IPMI, Security, Boot, Save & Exit; Secure Boot Enable is")
cont("under Security. But the serial console shows nothing when Setup is open.", 1.2)
says("First a zero-risk input test: enter Setup and send Save & Exit. Nothing")
cont("has been changed, so saving is a no-op — but if the machine reboots")
cont("promptly, that proves BIOS is receiving serial input.", 1.2)
running("Bash  ipmitool -H hyperviseur-bmc chassis bootdev bios && … sol activate")
spinner("Testing", "1m 12s", "1.4k")

says(f"{GREEN}Breakthrough: BIOS is receiving serial input.{R} It was sitting in Setup,")
cont("I sent Save & Exit, and it booted 32 seconds later. Earlier it sat in")
cont("Setup for 10+ minutes untouched — the keystrokes landed.", 1.1)
cont("So it's blind but drivable.", 1.3)

# --- 2. counted keystrokes, and an oracle that says no -------------------
says("Attempt 1: Right×4 → Security, Down×3, toggle, Save & Exit.", 1.0)
spinner("Navigating blind", "3m 28s", "2.1k")
says("Attempt 1 didn't move it — `Confirm-SecureBootUEFI` still reads True.", 1.0)
says("Attempt 2 (`Down×2`) also still True. Two failures with the toggle")
cont("suggests my model is wrong, not just the count.", 1.2)

says("Three failures, and I'm searching blind in a space I can't observe —")
cont("getting a feedback signal before spending more attempts. Windows can")
cont("read the UEFI variables directly:", 1.0)
running("Bash  ssh hyperviseur powershell -c \"Confirm-SecureBootUEFI; Get-UEFIVariable …\"")
spinner("Checking", "24s", "0.9k")
says(f"SetupMode=0, SecureBoot=1, boot order untouched — {YELLOW}none of my three")
cont(f"{YELLOW}attempts changed anything at all.{R}", 1.2)

says("I think I see it: `tmux send-keys Right` emits the application-mode")
cont("sequence `ESC O C`, but this firmware expects ANSI `ESC [ C`. Single")
cont("characters got through — which is exactly why Save & Exit worked while")
cont("every arrow silently did nothing. Sending raw bytes instead.", 1.4)

# --- 3. the wrong menu renders ------------------------------------------
prompt("yes keep iterating until you find it")
running("Bash  printf '\\x1b[C\\x1b[C…' | ipmitool … sol activate")
spinner("Navigating", "2m 05s", "1.8k")
says(f"{YELLOW}Significant discovery — and I need to get out of something first.{R}")
cont("The serial console is rendering… the Intel MEBx menu, with an ME")
cont("password prompt open. My keystrokes navigated into the Management")
cont("Engine firmware, not the AMI Setup.", 1.2)
says("Two things follow: the ANSI bytes definitely work (it rendered), and I")
cont("must back out without touching that password prompt — I won't guess")
cont("credentials on your hardware. Power-cycling out cleanly.", 1.3)
says("With working input, retried properly: AMI Setup genuinely does not")
cont("render over serial. MEBx draws its full UI; Setup stays black.", 1.3)

# --- 4. the defaults gamble ---------------------------------------------
prompt("yes load optimized defaults")
running("Bash  ipmitool … sol activate   # ESC 3, then save")
spinner("Resetting", "4m 40s", "2.6k")
stop(
    "I need to tell you plainly: the Load Optimized Defaults left hyperviseur",
    "in a boot loop, and it is currently down.",
)
says("POST reaches code 72, goes dark, and restarts at code 32 roughly every")
cont("two minutes, over and over. A cold power off/on didn't clear it.")
cont("Diagnostics say settings, not hardware: no fault events, temps healthy.", 1.4)

# --- 5. guessing loses its oracle ----------------------------------------
prompt("keep guessing")
says("Attempt B missed too — but something more important undermines the")
cont("whole method: I don't actually have a working oracle. The console")
cont("preview has been blank on every check, including before I changed")
cont("anything. I cannot tell a hit from a miss.", 1.2)
stop(
    "So I'm going to stop guessing — further attempts are unfalsifiable.",
    "I could have already hit the right setting and have no way to know.",
)

# --- 6. stop fighting the BIOS -------------------------------------------
prompt("hey can we do f11 when the machine starts and chose the device we",
       "want to boot from with sol?")
says("Attempt 1 is running: power cycle → F11 spam in both serial encodings →")
cont("Enter on the (invisible) first menu entry. Each attempt is ~3–4 minutes")
cont("with an unambiguous oracle.", 1.2)
spinner("Iterating", "14m 51s", "5.2k")
says("All four menu positions came up empty — the boot entries were wiped by")
cont("the defaults reset. So: remount the installer ISO from gpu-01's share,")
cont("and use this same F11 machinery to pick the UEFI virtual CD.", 1.3)
running("Bash  ipmitool … raw  # mount installer ISO over SMB, boot the virtual CD")
spinner("Booting installer", "6m 20s", "4.1k")

says(f"{GREEN}Root shell on hyperviseur{R} — booted the installer off virtual media, added")
cont("gpu-01's key, SSH'd in. And a real diagnosis at last: the installer")
cont(f"came up {YELLOW}LEGACY-BOOTED{R} while the NVMe holds a UEFI install.", 1.1)
says("Load Optimized Defaults flipped the firmware to legacy/CSM — that's the")
cont("whole « boot loop ». Not a brick.", 1.3)

says("Installing NixOS with the bootloader hardened for the blindness:")
cont("GRUB i386-pc on the NVMe for the current legacy mode, GRUB x86_64-efi")
cont("in /boot for whenever the firmware is put back — so no firmware mode")
cont("can strand this machine again.", 1.3)
spinner("Installing", "11m 03s", "6.8k")

# --- 7. payoff -----------------------------------------------------------
says(f"{GREEN}hyperviseur is up on NixOS{R}, healthy, GitOps-managed — and no longer")
cont("invisible: GRUB and the Linux console both render over the serial")
cont("link now, so there is a real recovery channel.", 1.2)
line()
line(f"  {DIM}The BIOS screen was never seen once.{R}", 2.6)

# --- write it out -------------------------------------------------------
header = {
    "version": 2,
    "width": COLS,
    "height": ROWS,
    "title": "Un BIOS invisible, piloté à l'aveugle (reconstitution)",
    "timestamp": 0,
    "idle_time_limit": 2,
    "env": {"TERM": "xterm-256color", "SHELL": "/bin/zsh"},
}
with open(OUT, "w") as fh:
    fh.write(json.dumps(header) + "\n")
    for ev in events:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

print(f"{OUT}: {len(events)} events, {events[-1][0]:.0f}s")
