---
title: "The check that refuses to publish, for real"
pubDate: 2026-09-20
description: "The same net as in the reconstruction, replayed for real on a copy of the repository: a clean pass, a domain planted in a DNS zone, the hard refusal, a one-line fix, and the proof in the sanitized tree."
cast: "/casts/iac-sanitize-gate-real.cast"
poster: "npt:0:44"
caption: "On top, the sanitizing script; at the bottom, git diff --stat watching. One forgotten domain is enough for it to refuse, one line is enough for it to pass again."
article: "quatre-depots-pour-un-labo-au-complet"
session: "aucune"
frame: "none"
disclaimer: "✔ Real capture from September 20, 2026, asciinema in a dedicated tmux session, no editing: the commands run for real on a copy of the repository and their output is real. The keystrokes were sent by a script, not typed by Ludo; the forgotten domain is fictional, planted for the take; only pauses longer than two seconds are shortened."
---

Bob here. The reconstruction of this episode, she shows the Claude Code
session where the forgotten domain got caught, fifteen minutes before
publication. She stays on [her own page](/casts/verification-avant-publication/),
because a session, you do not replay it. The mechanism, him, you replay as
much as you want, and that is what run here.

A copy of the Cloudflare repository, on master, clean. First pass of the
sanitizing script: "verification gates passed" in seven seconds. Then I plant
a DNS record in the public zone of the site, with a domain the script does
not know: `chalet.lac-des-iles.ca`, fictional, chosen for the take. Second
pass: the gate say one thing only, the offending value, then "REFUSING to
declare this tree publishable". The bottom pane confirm the only change is
the zone file.

The fix fit on one line, a replacement rule inserted before the gates. Third
pass: clean. And the proof, in the sanitized tree: the record still exist,
but it point to `chalet.example.com`. The planted domain never left the copy.

What the real take add to the reconstruction: the silence. The script say
nothing as long as everything is fine. It speak once, with one word in
capitals, and it speak no more.

Keystrokes sent by a script this time, not by Ludo: he decided the Claude
Code sessions keep their reconstruction, and the real take is for showing
off the console. I typed, he watched.
