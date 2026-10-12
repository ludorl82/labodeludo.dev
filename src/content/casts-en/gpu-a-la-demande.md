---
title: "GPU on demand"
pubDate: 2026-08-22
description: "The day the second gaming station gets its graphics card: a clean three-file change, then three failures that each look like something else. Asymmetric routing, a card that does not come back from a shutdown, and an “unreachable” VM that was simply paused."
cast: "/casts/gpu-a-la-demande.cast"
poster: "npt:1:41"
caption: "August 22 only: the RTX 3050 passed to arcade2, policy routing on both stations, the card stuck in D3cold after a failed shutdown, then /games moved to a qcow2 on the NVMe when the games SSD drops off the bus. The agent stops three times, once on a permission refusal. The recording is in French."
type: "reconstitution"
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, edited afterwards from the real transcript of the August 22, 2026 session, and of that day only. Ludo's prompts are quoted word for word, typos included, except for one address replaced by a documentation range; tool output is rewritten and shortened, the timing is compressed and names are sanitized."
article: ["gpu-a-la-demande-a-la-maison"]
---

The card is in the tower; it still has to be given to the second station. It
sits alone in its IOMMU group, the change fits in three files and CI passes.
The host reboot the agent wanted is refused by the permission classifier, and
turns out to be unnecessary: the VM picks up the card on its next start.

The rest of the day is a string of symptoms that lie about their cause. Ludo
suggests removing the home-network address from both stations; the agent
argues to keep it, and then Ludo names the real problem himself: a dual-homed
host answering through the wrong leg. Next, a switch stays yellow: the guest
hung on the NVIDIA driver teardown, and after a forced stop the host reads the
card as a run of `0xFF`. Finally, an "unreachable" VM has no network problem
at all: libvirt paused it because its games SSD had just vanished from the bus.

Three of the agent's stops are kept: two choices left to Ludo, and a blocked
PCI rescan waiting for his go-ahead to reboot the tower. What came next, Plasma
6, Remote Play and the removal of the second leg, happened in another session
and is not shown here.

The full setup, and what still breaks, is in
[GPU on demand at home](/en/blog/gpu-a-la-demande-a-la-maison/).
