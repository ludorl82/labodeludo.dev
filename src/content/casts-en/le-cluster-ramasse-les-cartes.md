---
title: "The cluster picks up the cards"
pubDate: 2026-09-14
description: "An idle GTX 960 handed to Kubernetes: the driver on the host freezes the kernel without ever saying “graphics card”, the driver moves into a VM, a bisect blames the wrong suspect, and the card-swap cycle, replayed live, flushes out four bugs."
cast: "/casts/le-cluster-ramasse-les-cartes.cast"
poster: "npt:1:33"
caption: "The GPU thread of one evening: the Ready node that no longer starts anything, the photo of the screen that corrects the diagnosis, the compute VM, the empty CD drive that skews the bisect, the one line of XML that unblocks three cards, then the four bugs in the swap. The agent stops four times and corrects itself three times. The recording is in French."
type: "reconstitution"
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, edited afterwards from the real transcript of the September 14–15, 2026 session. Ludo's prompts are quoted word for word, typos included, except for machine names replaced with the article's; tool output is rewritten and shortened, the timing is compressed and names are sanitized."
article: ["quand-personne-ne-joue-le-cluster-ramasse-les-cartes"]
---

The request is simple: plug the new RTX 3050 into the first gaming VM and make
the GTX 960 available to Kubernetes. The NVIDIA driver goes on the host, and
after the reboot the tower turns into a ghost: the node shows `Ready`, its
lease keeps renewing, and no container starts anymore. The agent first blames
k3s's `PATH`, then locks itself out by hammering `sshd` during boot. A photo of
the screen settles it: a chain of hung tasks in the kernel, `modprobe` stuck
behind `bridge`.

The driver is pulled off the host and handed to a compute VM, vm-03. While
writing it, the agent catches a synchronous `virsh` call in the libvirt hook,
one that could have blocked the very gaming VM it was meant to help. Then comes
borrowing the two 3050s: three cards will not boot, and the bisect blames the
cards when it was really comparing a VM with an install CD to one without. The
agent settles for a single card; Ludo pushes back, and `<rom bar='off'/>`
fixes everything.

The last highlight is the swap itself, tested live: a `sudo` masked by `PATH`,
a cordon that survives the reboot, a fixed-name `systemd-run` unit that refuses
to start again, a shutdown sent before the guest agent is up.

The full story, told by Bob, is in
[When nobody is playing, the cluster picks up the cards](/en/blog/quand-personne-ne-joue-le-cluster-ramasse-les-cartes/).
