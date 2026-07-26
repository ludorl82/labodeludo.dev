---
title: "The check that refuses to publish"
pubDate: 2026-07-26
description: "The last net before a repository goes public: a forgotten domain, a hard refusal, and the fix added on both sides."
cast: "/casts/iac-sanitize-gate.cast"
poster: "npt:0:06"
caption: "The final check before publication: it finds a forgotten domain, refuses to go on, and the offending name gets added both to the replacement rule and to the check itself."
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, edited afterwards from the real session transcript. The prompts are the ones from the actual session; the timing is compressed and the long waits are cut. And the domain caught on screen is already the fictional name — publishing a demonstration of a leak detector with the real value inside it would have been a little ironic."
article: "quatre-depots-pour-un-labo-au-complet"
---

I published the four repositories that describe my lab. Before anything goes
public, a script replaces the real names with fictional ones, and a check
re-reads the result.

That check is what runs here. It found a real domain name that had survived
inside a sentence in a documentation file — my rules covered the code, nobody
had thought about the prose — and it refused to go any further. Fifteen
minutes before publication.

The offending name got added in both places: to the replacement rule, and to
the check itself.
