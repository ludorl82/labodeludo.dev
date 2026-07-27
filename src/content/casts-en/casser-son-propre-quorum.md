---
title: "Breaking your own etcd quorum"
pubDate: 2026-07-27
description: "The same command, twice. The first time it is safe, the second time it takes the cluster down — because the number of voters changed in between."
cast: "/casts/control-plane-consolidation.cast"
poster: "npt:0:08"
caption: "Tearing a three-node control plane down to one. The outage in the middle is self-inflicted, and the command that fixes it gets blocked by the permission guardrail while the cluster is down."
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, edited afterwards from the real session transcript. The prompts and the stop messages are the ones from the actual session; the timing is compressed and the long waits are cut. Hostnames sanitized, and some worker nodes are left out of the display — that is called out on screen."
article: "je-me-suis-vote-hors-de-l-ile"
---

Removing two etcd members from a three-member control plane. The first one
leaves without a fuss. The second one, with exactly the same sequence of
commands, cuts the cluster API dead — because at two members, there is no
majority left to lose.

What makes the recording interesting is not the mistake itself: it is the
thirty seconds that follow. The recovery command gets refused by the permission
classifier, while the cluster is down. The guardrail does exactly its job — at
the worst possible moment.
