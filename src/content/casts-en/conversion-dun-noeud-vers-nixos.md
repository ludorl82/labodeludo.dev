---
title: "Converting one node to NixOS"
pubDate: 2026-07-25
description: "A machine reinstalled over SSH, with no screen and no USB stick. Secure Boot and an oversized initrd are the real obstacles."
cast: "/casts/nixos-migration.cast"
poster: "npt:0:06"
caption: "One node conversion from start to finish, condensed into under two minutes. Secure Boot and an initrd that refuses to unpack are the real walls in this session."
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, edited afterwards from the real session transcript. The prompts and the stop messages are the ones from the actual session; the timing is compressed and the long waits are cut. Hostnames sanitized."
article: "migrer-tout-mon-homelab-vers-nixos"
---

One of the nine machines in the fleet, converted end to end over SSH with
`nixos-anywhere` — no screen plugged in, no USB stick; the machine reinstalls
itself and comes back running NixOS.

The two walls in this session are the ones you don't see coming: Secure Boot
blocking `kexec`, and an initrd that refuses to unpack for lack of memory.
