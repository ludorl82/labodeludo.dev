---
title: "An invisible BIOS, driven blind"
pubDate: 2026-08-20
description: "A BIOS screen nobody can see, arrow keys that never arrived, a wrong turn into the wrong firmware — and a machine recovered without ever seeing the screen."
cast: "/casts/bios-blind.cast"
poster: "npt:0:08"
caption: "The most absurd part of the Cabinet's migration, condensed: navigating a BIOS that draws nothing over serial, discovering the arrow keys were never arriving, landing in the Intel MEBx menu by mistake, breaking the boot with Optimized Defaults — then routing around all of it through the BMC's virtual CD drive."
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, edited afterwards from the real session transcript. The prompts and the stop messages are the ones from the actual session; the timing is compressed and the long waits are cut. Hostnames sanitized."
article: "une-borne-darcade-qui-cohabite-avec-kubernetes"
---

The Cabinet's BIOS was invisible: the discrete GPU swallows the video output,
the iKVM console sees nothing, and Setup draws nothing over the serial port.
It still had to be entered, to unblock the NixOS install.

What follows is a blind search through a space you cannot observe: proving
the keys land (by saving without changing anything), discovering the arrows
were never arriving (wrong serial encoding), ending up in the Intel ME
firmware by mistake, and breaking the boot with Load Optimized Defaults. The
way out does not go through the BIOS — it goes around it.

Claude Code was driving, remotely, while the hardware's owner was on
vacation. The BIOS screen was never seen once.
