---
title: "The reply that left by the wrong leg, for real"
pubDate: 2026-09-25
description: "The frozen SSH failure, replayed for real and captured as is: rule 102 removed from a host with two legs, a session from the Mac that goes quiet for 40 seconds and never comes back while pfSense's state melts from 30 seconds to zero, then the rule put back and the same session getting through, with a state kept for 24 hours."
cast: "/casts/la-mauvaise-patte-real-en.cast"
poster: "npt:0:56"
caption: "Three panes: the commands on top, the state pfSense keeps on the session in the middle, the narration at the bottom. Without rule 102, 20 packets one way, zero the other, and a state that expires at 30 seconds. With the rule, both directions, and a state kept for 24 hours."
article: "la-reponse-par-la-mauvaise-patte"
session: "aucune"
frame: "none"
disclaimer: "✔ This is a real capture, made on September 24, 2026 with asciinema in a dedicated tmux session, with no editing. vm-02, mac and routeur are SSH aliases to the real machines, and the anonymise filter, visible on screen, replaces the real addresses with the article's on the fly; fiche is a small script that reads pfSense's state table (pfctl -ss -vv) through that filter. To replay the failure, rule 102 was removed from vm-02 for the take, then put back. The keystrokes were sent by a script and not typed by Ludo, the prompt is “ludo@labo”, only pauses longer than two seconds are shortened, and the container ID in the tmux bar is replaced by a name of the same length."
---

The failure from [the article](/en/blog/la-reponse-par-la-mauvaise-patte/), replayed
the same day, for real, with the narration in English. The client is the Mac,
the only device that sits on VLAN 50 alone: `ssh -J mac vm-02` makes the Mac open
the TCP connection to vm-02's VLAN 10 address, through pfSense. That is exactly
the path that froze.

On top, the commands. First the module's three rules on vm-02, then rule 102
removed, then the Mac sends a line after 40 seconds of silence. In the middle, a
`watch` that rereads every two seconds the state pfSense keeps on that session:
`SYN_SENT:CLOSED`, twenty packets one way, zero the other, and an expiry that
melts from 30 seconds to zero. The state disappears, the line never gets
through, and the test is cut by its own timeout at 50 seconds.

Then the rule put back, and the same test, with a session that stays open twenty
seconds longer so the state stays in view. This time it moves to
`ESTABLISHED:ESTABLISHED`, with packets in both directions and an expiry at 24
hours, and the line arrives after its 40 seconds of silence.

What was touched after the take, and nothing else: pauses longer than two
seconds and the container ID in the tmux bar. The addresses are fictional right
on screen: they go through the `anonymise` filter you can see in the commands.
