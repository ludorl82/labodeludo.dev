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

One of the nine machines converted the same day — a virtual one.
`nixos-anywhere` does everything over SSH: it uploads an installer, `kexec`s
into it, partitions, installs, and the machine comes back exactly as git
describes it. No screen plugged in, no USB stick.

In practice it stalls. Twice over here: Secure Boot blocking the `kexec`,
then an initrd that refuses to unpack for lack of memory.

Claude Code — the Fable 5 and Opus 5 models — drove it. My part: validate,
ask questions, and unblock what an agent isn't allowed to do on its own.
