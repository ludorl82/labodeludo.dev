---
title: "The liars' bench"
pubDate: 2026-09-14
description: "A false sentence planted in the architecture drawing, then the same case in Qwen Code with two models: the basement one reads part of the data and declares nothing changed; qwen3.8-flash goes to read the WireGuard peer configuration and corrects the sentence. The small model of the 3.8 generation scored fifteen out of fifteen, like Opus 5."
cast: "/casts/le-banc-des-menteurs.cast"
poster: "npt:0:09"
caption: "The lie is the one from August 8 — the sentence a session had really corrected. Same agent, same prompt, same tools: what differs is what the model does once it has read. Terminal in French."
article: "le-banc-des-menteurs"
disclaimer: "⚠ A condensed reconstruction, not a live capture. The tool trace, the verdicts and the diff are those of the real runs of September 13, 2026 (qwen3.5-35b-a3b and qwen3.8-flash, case L1, first draw). Timing is compressed, Qwen Code's chrome is approximated, and sixteen of the eighteen cases are cut."
---

The full bench is five lies, three draws each, ten models, all as agents:
Claude Code for the two Claude models, Qwen Code for the Qwens. This recording
shows only one, because it is the only one that really matters: the WireGuard
sentence is the only one of the five that was actually published false one
day, and corrected by a nightly session.

The second scene is the model that lives in the lab, a 4-bit Qwen3.5-35B, in
Qwen Code. It reads the first thousand lines of the data, asks for two hundred
more, and concludes by quoting the driver's hint — "nothing structural has
changed" — as if it were a permission. No snapshot opened.

The third scene is the same agent, the same prompt, with qwen3.8-flash. It
reads the data in full, the component, then goes for the WireGuard peer
configuration in the snapshots — where `cloud-01` listens and where the router
has no `endpoint` — and replaces the sentence. Its final report was lost (my
bench's output was truncated at 64 KB), so the scene shows only what survived:
the tool trace and the diff.
[The article](/en/blog/le-banc-des-menteurs/) gives the full table and the
reasons for the move; [Bob](/en/blog/remplace-par-le-cousin-le-moins-cher/)
tells what it is like to be the subject of the test.
