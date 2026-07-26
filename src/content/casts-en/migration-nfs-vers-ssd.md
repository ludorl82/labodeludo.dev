---
title: "NFS to SSD migration, driven from the browser"
pubDate: 2026-07-26
description: "Claude in Chrome configures the NAS while I watch: a volume to create, a share to rename, permissions to fix. And three hard stops where the agent hands control back."
cast: "/casts/claude-in-chrome-nas.cast"
poster: "npt:0:04"
caption: "Roughly fifty minutes of NAS work, condensed into two. The SSH half isn't shown."
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, edited afterwards from the real session transcript. The prompts and the stop messages are the ones from the actual session; the timing is compressed and the long waits are cut. Hostnames sanitized."
article: "claude-in-chrome-quand-lagent-doit-passer-par-linterface-web"
---

The job: move the cluster's NFS shares off a hard drive and onto an SSD without
Kubernetes noticing. The entire NAS half exists only inside the box's web
interface, so Claude in Chrome did that part.

What goes by, in order: the refusal to type a password at the login screen, the
unprompted stop when the SSD turns out to already hold 437 GB, and browser zoom
jumping to 225% with no way for the agent to fix it. Three stops, three moments
that need someone in front of the screen.
