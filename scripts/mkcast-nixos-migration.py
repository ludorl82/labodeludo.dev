#!/usr/bin/env python3
"""Build the asciicast for the NixOS migration article.

Condensed from the real session transcript of one node's conversion
(2026-07-24). The prompts and Claude's stop messages come from that session;
timing is compressed and the long waits cut.

Hostnames are sanitized to match the article's fictional naming, not the real
inventory: the converted VM is `vm-05` (asked for as `vm-03` at first, then
kept under its own name), its Hyper-V host is `hv-01`, and the
fleet's build/deploy box is `gpu-01`. The technical narrative — Secure Boot
blocking kexec, then an initrd that won't unpack in 4 GB — is unchanged.

Palette and line grammar per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-nixos-migration.py
"""
import json
import random

OUT = "public/casts/nixos-migration.cast"
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

BRANCH = "nixos-vm-05"

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



# --- pinned status rows -------------------------------------------------
# The hint and tmux lines belong to the recording, not to CSS around it, so
# they survive wherever the cast is played — asciinema.org, embeds, a raw
# download. Same mechanism tmux uses: a scroll region over the upper rows
# leaves the bottom ones untouched while everything above them scrolls.
# Because they are terminal cells, they scale with the terminal instead of
# competing with it for width, which is what made the CSS version unusable
# on a phone.
STATUS_ROWS = 2
BODY = ROWS - STATUS_ROWS

CLOCK = "11:47:33"
STAMP = "25-Jul-26"
CONTAINER = "e5a2d76c318b"

HINT_PLAIN = "\u25b6\u25b6 auto mode on (shift+tab to cycle) \u00b7 esc to interrupt"
WINS_PLAIN = "1:claude*  2:claude-  3:zsh"


def _seg(text, bg, fg):
    return f"\x1b[48;5;{bg}m\x1b[38;5;{fg}m {text} ", len(text) + 2


def _hint_row():
    left = (
        f" {YELLOW}\u25b6\u25b6 auto mode on{R}"
        f"{DIM} (shift+tab to cycle) \u00b7 esc to interrupt{R}"
    )
    pad = max(1, COLS - 1 - len(HINT_PLAIN) - 4)
    return left + " " * pad + f"{GREEN}/rc{R} "


def _tmux_row():
    left, wl = "", 0
    for t, bg, fg in (("console", 250, 233), ("ludorl82", 245, 233), ("1:1", 240, 250)):
        s, w = _seg(t, bg, fg)
        left += s
        wl += w
    right, wr = "", 0
    for t, bg, fg in ((CLOCK, 235, 240), (STAMP, 240, 250), (CONTAINER, 245, 233)):
        s, w = _seg(t, bg, fg)
        right += s
        wr += w
    mid = max(len(WINS_PLAIN), COLS - wl - wr)
    gap = (mid - len(WINS_PLAIN)) // 2
    wins = (
        f"\x1b[48;5;233m" + " " * gap
        + f"\x1b[1m\x1b[38;5;253m1:claude*{R}\x1b[48;5;233m"
        + f"\x1b[38;5;240m  2:claude-  3:zsh"
        + " " * (mid - len(WINS_PLAIN) - gap)
    )
    return left + wins + right + R


def paint_status():
    """Draw the pinned rows, then confine scrolling to the rows above them."""
    out("\x1b[2J\x1b[H")
    out(f"\x1b[{ROWS - 1};1H\x1b[2K" + _hint_row())
    out(f"\x1b[{ROWS};1H\x1b[2K" + _tmux_row())
    out(f"\x1b[1;{BODY}r")
    out("\x1b[1;1H")


paint_status()

# --- disclaimer ---------------------------------------------------------
# Baked into the recording itself, not just the page around it: the cast is
# published to asciinema.org too, where it stands alone, and an embedded or
# downloaded file carries no page at all. This must not get separated from it.
line(f"{YELLOW}  \u26a0  Reconstitution condens\u00e9e \u2014 pas une capture en direct.{R}", 0.25)
line(f"{DIM}     Demandes et messages r\u00e9els, minutage compress\u00e9,{R}", 0.25)
line(f"{DIM}     noms d'h\u00f4te sanitis\u00e9s.  labodeludo.dev/casts/{R}", 2.6)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.220{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Opus 5 with high effort · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/git/nixos-iac{R}", 1.4)
line()

# --- 1. the ask ---------------------------------------------------------
prompt("Can you ssh into vm-05 and convert it to nixos as vm-03?")
says("I'll start by reading the relevant memory files for context.", 1.1)
spinner("Gathering", "18s", "1.2k")
says("Noting that the rename isn't free: vm-05 is a k3s node, so vm-03 means")
cont("draining it, deleting the old node object and re-joining under the new", 0.9)
cont("name — plus DNS, the DHCP reservation and the monitoring checks.", 1.2)

# --- 2. the user steers mid-flight -------------------------------------
prompt("nvm keep the name vm-05")
says("Got it — no rename. Converting in place as `vm-05`.", 1.0)

says("Important find before I wipe anything: vm-05 runs a scheduled S3 backup")
cont("(`~/scripts/homelab-backup.sh` + its key). Preserving that first.", 1.2)
running("Bash  scp -p vm-05:~/scripts/homelab-backup.sh ./salvage/")
spinner("Salvaging", "12s", "0.8k")

says("Now writing the vm-05 config, then checking it evaluates.", 1.0)
running("Bash  nix eval .#nixosConfigurations.vm-05.config.system.build.toplevel")
spinner("Evaluating", "41s", "2.6k")
says("Config evaluates cleanly. Committing to the repo.", 1.1)

# --- 3. point of no return ---------------------------------------------
says("Now the kexec phase — this is the point of no return for vm-05's")
cont("Debian install.", 1.2)
running("Bash  nixos-anywhere --flake .#vm-05 root@vm-05")
spinner("Installing", "1m 04s", "3.4k")

# --- 4. first wall: Secure Boot ----------------------------------------
says("Kexec was rejected: Secure Boot is enabled on this VM, so the kernel")
cont("refuses to load the unsigned NixOS kernel. Checking how boxed-in we are.", 1.2)
spinner("Investigating", "27s", "1.9k")

says("Blocked on a real fork. vm-05 is a Gen-2 VM with Secure Boot On, and the")
cont("kernel is in `integrity` lockdown — that blocks both kexec paths, so the")
cont("install can't start. NixOS also can't Secure Boot without lanzaboote.", 1.3)
stop(
    "I can disable Secure Boot from the hypervisor and power-cycle it.",
    "That reboots vm-05. Say go and I'll do it.",
)

prompt("go ahead")
running("Bash  ssh hv-01 powershell -c \"Set-VMFirmware vm-05 -EnableSecureBoot Off\"")
spinner("Reconfiguring", "34s", "1.1k")
says("Lockdown is now `[none]` — kexec will work. Re-running.", 1.0)
spinner("Installing", "2m 11s", "4.2k")

# --- 5. second wall: initrd won't unpack -------------------------------
says("Mid-kexec, host unreachable as expected. But it never came back.", 1.1)
says("I have hypervisor access, so let me grab the VM console screen directly.", 1.0)
running("Bash  ssh hv-01 powershell -c \"Get-VMConsole vm-05 | Out-File screen.txt\"")
spinner("Capturing", "19s", "1.5k")

says("Found it — the console shows the kexec kernel booted but")
cont(f"{YELLOW}Initramfs unpacking failed: XZ-compressed data is corrupt{R}, then hung.")
cont("That's the classic symptom of too little RAM to unpack the ~430 MB", 0.9)
cont("installer initrd. vm-05 has 4 GB. Bumping it temporarily to 8 GB.", 1.2)
spinner("Retrying", "3m 48s", "5.7k")

# --- 6. it comes back ---------------------------------------------------
says("Host is answering — connection refused, not unreachable. It's booting,")
cont("sshd not up yet.", 1.1)
says(f"{GREEN}vm-05 is up on NixOS 26.11{R}, booted from disk, both NICs and the IPv6")
cont("address correct. Two things to check — DNS is failing.", 1.2)

says("Found the real issue: private names fail while public names work.")
cont("systemd-resolved is routing queries to its fallback instead of the local")
cont("resolver, because nothing marks the interface's DNS as authoritative.", 1.0)
cont("Fixing that in the config, not by hand on the box.", 1.2)
spinner("Rebuilding", "58s", "2.2k")

# --- 7. the real test ---------------------------------------------------
says("Now restoring the VM to its original 4 GB and doing a cold boot — the")
cont("real test that it comes up unattended.", 1.2)
spinner("Verifying", "1m 27s", "3.0k")

says(f"{GREEN}Everything verified.{R} vm-05 runs NixOS 26.11, converted entirely over")
cont("SSH. Disk layout, both NICs, IPv6, DNS and the cluster agent all check out")
cont("after a cold boot at the original 4 GB. Config committed and pushed.", 1.4)
line()
line(f"  {DIM}8 of 9 nodes converted.{R}", 2.6)

# --- write it out -------------------------------------------------------
header = {
    "version": 2,
    "width": COLS,
    "height": ROWS,
    # Shown by asciinema.org in listings and embeds — say what it is there too.
    "title": "Une conversion de nœud vers NixOS (reconstitution)",
    "timestamp": 0,
    "idle_time_limit": 2,
    "env": {"TERM": "xterm-256color", "SHELL": "/bin/zsh"},
}
with open(OUT, "w") as fh:
    fh.write(json.dumps(header) + "\n")
    for ev in events:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

print(f"{OUT}: {len(events)} events, {events[-1][0]:.0f}s")
