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

import claude_tui as T
from claude_tui import DIM, FG, GREEN, R, SPIN, calling, cont, line, prompt, says, spinner, waiting

T.setup(
    out="public/casts/survivor-island.cast",
    title="L'île du survivant — le rack se réveille tout seul (reconstitution)",
    session="survivor-island",
    windows=["backlog", "survivor-island"],
    current="survivor-island",
    start="05-Aug-26 17:09:36",
    cwd="~/tmp",
    model="Opus 5 · Claude Max",
    seed=7,
)

T.disclaimer("Invites textuelles (5 août 2026), temps d'attente compressés,",
             "noms d'hôtes et adresses fictifs.")
T.banner()

# ------------------------------------------------------------------ scene 1
prompt("i unplugged the lx1500 now, i want to make sure pi-2 will bring everything "
       "back up after it gets plugged in again")
says("One critical thing first: the survivor UPS is the mains sensor for the")
cont("whole wake logic — rack-wake decides \"power is back\" by watching pi-2's")
cont("own UPS flip from on-battery to online.")
spinner("Reading ups status on gpu-01", "2s", "0.4k", 1.4)
line(f"  {DIM}battery.charge: 49   battery.charge.low: 50   ups.status: OB DISCHRG{R}", 0.9)
line()
says("The battery is at 49% — already below the 50% trigger — so the cascade")
cont("is firing right now. That's fine — it's the test you wanted, just on a")
cont("fast clock.")
waiting()
T.pause(2.0)

# ------------------------------------------------------------------ scene 2
says("The cascade didn't fire — my 50% override set the variable but the")
cont("driver still waits for the UPS's own low-battery signal (it needs the")
cont("ignorelb flag — my miss). Battery's at ~49% with minutes left, so")
cont("triggering the clean cascade manually right now:")
calling("Bash", 1)
T.detail(f"{DIM}sudo upsmon -c fsd on gpu-01{R}", 0.6)
T.denied("Permission denied", 1.3)
line()
says("The classifier blocked me from triggering the shutdown myself (it powers")
cont("down four hosts). ~8 minutes of battery left.")
waiting()
T.pause(1.4)
prompt("the shutdown sequence is already running, dont bother")
spinner("Watching the cascade", "90s", "1.1k", 1.4)
line(f"  {DIM}17:14:51  win-01=down node-01=down node-02=UP gpu-01=UP{R}", 0.8)
line(f"  {DIM}17:15:27  win-01=down node-01=down node-02=down gpu-01=down{R}", 0.9)
line()
says("Confirmed — the UPS's native low-battery signal fired it: clean")
cont("shutdowns, least critical first, the UPS master last.")
waiting()
T.pause(2.0)

# ------------------------------------------------------------------ scene 3
prompt("everything is plugged back in")
spinner("Watching the BMCs and the wake latch on pi-2", "3m", "2.2k", 1.4)
line(f"  {DIM}pi-2 ups: OL   latch: ARMED{R}", 0.8)
line(f"  {GREEN}✓{R} {FG}17:20:31  win-01=UP node-01=UP node-02=UP gpu-01=UP{R}", 1.0)
line(f"  {SPIN}rack-wake: win-01 BMC unreachable — latch stays armed, retrying{R}", 1.2)
line()
prompt("why isnt win-01 bmc back up while the machine is?")
spinner("Reading BMC LAN config in-band via Microsoft_IPMI WMI", "24s", "1.8k", 1.4)
line(f"  {DIM}param 20 (802.1q): 0x1e 0x80 — VLAN 30, enabled{R}", 1.1)
line()
says("Found it! The BMC's VLAN tag reads VLAN 30 — it should be VLAN 10. The")
cont("cold AC cycle scrambled it: alive the whole time, tagging its traffic")
cont("onto the wrong network. Fixing it in-band:")
calling("Bash", 1)
T.detail(f"{DIM}Setting param 20 → VLAN 10 via raw IPMI… cc=0{R}", 1.2)
line(f"  {GREEN}✓{R} {FG}win-01 BMC answering after 10s{R}", 1.0)
line()
T.detail(f"{DIM}Waiting for the latch… (70s){R}", 1.4)
line(f"  {GREEN}✓{R} {FG}power restored and all chassis on: latch cleared{R}", 0.9)
line(f"  {GREEN}✓{R} {FG}ntfy → \"Rolling rack awake after power event\"{R}", 1.1)
line()
says("The latch cleared and sent its notification — full recovery, closed", 1.0)
cont("loop, by the system itself. All 9 cluster nodes Ready.", 1.0)
line()
line(f"{DIM}The survivor island's first production cycle: detect, wait, wake, report.{R}", 3.0)

T.save()
