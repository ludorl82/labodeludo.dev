---
title: "The survivor island, unplugged for real"
pubDate: 2026-08-05
description: "The lab's last pull-the-plug test: the cord pulled, the shutdown cascade firing on the UPS's signal, a BMC lost on the wrong VLAN, and the latch closing out the outage by itself."
cast: "/casts/survivor-island.cast"
poster: "npt:0:06"
caption: "The final pull test: cascade, stray BMC, in-band repair, and the latch closing the outage on its own."
article: "l-ile-du-survivant"
frame: "none"
type: "reconstitution"
disclaimer: "⚠ This is not a live capture: a condensed reconstruction from the real session transcript (2026-08-05). The prompts are verbatim, waits are compressed, and hostnames and addresses are fictional."
---

Three days of power outages, then four deliberate pulls of the plug to check
what had to outlive everything else: the router, the modem and a single
Raspberry Pi, on the least loaded UPS.

This session is the last of the four. The shutdown cascade fires on the UPS's
native signal, the permission classifier stops the agent along the way, and the
IPMI wake-up runs into a BMC that is not on the VLAN where it is being looked
for. The repair happens in-band, and the outage closes itself when the latch
sees power come back.
