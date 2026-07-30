---
title: "Unplugging the NAS for science"
pubDate: 2026-07-30
description: "Three deliberate power cuts to the NAS to verify freshly written liveness probes. Each cut finds something the previous one had missed — and the last one is boring, which was the goal."
cast: "/casts/nas-pull-the-plug.cast"
poster: "npt:0:08"
caption: "The three cuts, condensed: the probes that still lied, Loki's crash loop, the permission guard-rail in the middle of the repair, and the clean run at the end."
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, assembled after the fact from the session's real transcript. The prompts and stop messages are those of the actual session; timing is compressed and the long monitoring loops are cut. Hostnames sanitized."
article: "debrancher-le-nas-pour-la-science"
---

k3s workloads left `Running` with their NFS storage dead underneath — zombies
nothing was reporting. The session adds liveness probes everywhere, then
verifies them the only honest way: by pulling the NAS's plug. Three times.

What makes the recording interesting is the progression: the first cut shows
three probes still lying (a `/ready` served from memory, `ls` answered by the
NFS attribute cache). The second one wakes a bug the old configuration had
been masking — Loki's WAL crash loop, regenerated on every restart by the NFS
*silly-rename*. And in the middle of the repair, the permission classifier
blocks the `mv` on the data volume, during the outage: the guard-rail doing
exactly its job, at the exact moment you wish it would keep quiet.

The third cut finds nothing. That was the goal.
