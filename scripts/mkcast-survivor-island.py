#!/usr/bin/env python3
"""Build the asciicast for the survivor-island article (Ludo voice).

Condensed from the real session transcript (2026-08-05 evening): the last
plug-pull drill of the UPS work. The user's prompts and the turning-point
assistant lines are verbatim from that session; timing is compressed, the
long deploy waits are cut, and the monitoring loops are reduced to their
inflection lines.

The arc: the rack UPS is pulled with the survivor island (router + modem +
one Pi on its own UPS) standing by — the shutdown cascade fires on its
own, the servers go down cleanly with their BMCs still powered, and after
the replug the island's wake latch finds one BMC unreachable: its 802.1q
VLAN tag scrambled in the power cycle. The fix happens in-band from the
running Windows host (raw IPMI over WMI), the BMC answers ten seconds
later, and the latch clears itself with its "rolling rack awake"
notification. Guard-rail beat kept: the permission classifier blocking the
manual FSD, and the user's "the shutdown sequence is already running, dont
bother" — both real.

Names sanitized: gpu-01 (GPU node), win-01 (the Windows host), node-01/02,
pi-2 (the island Pi), nas, RFC 5737 addressing. Palette and line grammar
per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-survivor-island.py
"""
import json
import random

OUT = "public/casts/survivor-island.cast"
COLS, ROWS = 96, 22
random.seed(7)  # keep regenerated casts byte-stable

FG = "\x1b[38;5;253m"
DIM = "\x1b[38;5;246m"
YELLOW = "\x1b[38;5;220m"
GREEN = "\x1b[38;5;114m"
SPIN = "\x1b[38;5;174m"
CYAN = "\x1b[38;5;37m"
BOLD = "\x1b[1m"
R = "\x1b[0m"

BRANCH = "survivor-island"

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


def rule():
    dashes = "─" * (COLS - len(BRANCH) - 3)
    line(f"{CYAN}{dashes} {BRANCH}{R}", 0.5)


def assistant(lines, d=0.9):
    first = True
    for s in lines:
        marker = f"{FG}●{R} " if first else "  "
        line(marker + f"{FG}{s}{R}", d)
        first = False


def spinner(s, d=1.4):
    line(f"{SPIN}·{R} {DIM}{s}{R}", d)


def stop(d=3.2):
    line(f"{DIM}waiting for you…{R}", d)


# ------------------------------------------------------------------ scene 1
rule()
typed("i unplugged the lx1500 now, i want to make sure pi-2 will bring everything "
      "back up after it gets plugged in again", prefix=f"{GREEN}❯{R} ", d=1.6)
line()
assistant([
    "One critical thing first: the survivor UPS is the mains sensor for the",
    "whole wake logic — rack-wake decides \"power is back\" by watching pi-2's",
    "own UPS flip from on-battery to online.",
])
line()
spinner("Reading ups status on gpu-01… (2s · ↓ 0.4k tokens)")
line(f"  {DIM}battery.charge: 49   battery.charge.low: 50   ups.status: OB DISCHRG{R}", 0.9)
line()
assistant([
    "The battery is at 49% — already below the 50% trigger — so the cascade",
    "is firing right now. That's fine — it's the test you wanted, just on a",
    "fast clock.",
])
stop()

# ------------------------------------------------------------------ scene 2
line()
assistant([
    "The cascade didn't fire — my 50% override set the variable but the",
    "driver still waits for the UPS's own low-battery signal (it needs the",
    "ignorelb flag — my miss). Battery's at ~49% with minutes left, so",
    "triggering the clean cascade manually right now:",
])
line()
spinner("Running sudo upsmon -c fsd on gpu-01…", 1.2)
line(f"  {SPIN}✗ Permission denied by the auto mode classifier{R}", 1.3)
line()
assistant([
    "The classifier blocked me from triggering the shutdown myself (it powers",
    "down four hosts). ~8 minutes of battery left.",
])
stop(2.6)
line()
typed("the shutdown sequence is already running, dont bother", prefix=f"{GREEN}❯{R} ", d=1.4)
line()
spinner("Watching the cascade… (90s · ↓ 1.1k tokens)")
line(f"  {DIM}17:14:51  win-01=down node-01=down node-02=UP gpu-01=UP{R}", 0.8)
line(f"  {DIM}17:15:27  win-01=down node-01=down node-02=down gpu-01=down{R}", 0.9)
line()
assistant([
    "Confirmed — the UPS's native low-battery signal fired it: clean",
    "shutdowns, least critical first, the UPS master last.",
])
stop()

# ------------------------------------------------------------------ scene 3
line()
typed("everything is plugged back in", prefix=f"{GREEN}❯{R} ", d=1.4)
line()
spinner("Watching the BMCs and the wake latch on pi-2… (3m · ↓ 2.2k tokens)")
line(f"  {DIM}pi-2 ups: OL   latch: ARMED{R}", 0.8)
line(f"  {GREEN}✓{R} {FG}17:20:31  win-01=UP node-01=UP node-02=UP gpu-01=UP{R}", 1.0)
line(f"  {SPIN}rack-wake: win-01 BMC unreachable — latch stays armed, retrying{R}", 1.2)
line()
typed("why isnt win-01 bmc back up while the machine is?", prefix=f"{GREEN}❯{R} ", d=1.5)
line()
spinner("Reading BMC LAN config in-band via Microsoft_IPMI WMI… (24s · ↓ 1.8k tokens)")
line(f"  {DIM}param 20 (802.1q): 0x1e 0x80 — VLAN 30, enabled{R}", 1.1)
line()
assistant([
    "Found it! The BMC's VLAN tag reads VLAN 30 — it should be VLAN 10. The",
    "cold AC cycle scrambled it: alive the whole time, tagging its traffic",
    "onto the wrong network. Fixing it in-band:",
])
spinner("Setting param 20 → VLAN 10 via raw IPMI… cc=0", 1.2)
line(f"  {GREEN}✓{R} {FG}win-01 BMC answering after 10s{R}", 1.0)
line()
spinner("Waiting for the latch… (70s)")
line(f"  {GREEN}✓{R} {FG}power restored and all chassis on: latch cleared{R}", 0.9)
line(f"  {GREEN}✓{R} {FG}ntfy → \"Rolling rack awake after power event\"{R}", 1.1)
line()
assistant([
    "The latch cleared and sent its notification — full recovery, closed",
    "loop, by the system itself. All 9 cluster nodes Ready.",
], d=1.0)
line()
line(f"{DIM}The survivor island's first production cycle: detect, wait, wake, report.{R}", 3.0)

# ---------------------------------------------------------------- write out
header = {
    "version": 2,
    "width": COLS,
    "height": ROWS,
    "title": "L'île du survivant — le rack se réveille tout seul (reconstitution)",
    "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"},
    "idle_time_limit": 2,
}
with open(OUT, "w") as f:
    f.write(json.dumps(header) + "\n")
    for ev in events:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")
print(f"wrote {OUT}: {len(events)} events, {events[-1][0]:.0f}s")
