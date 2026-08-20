---
title: "A smart-home button that hires a Claude"
pubDate: 2026-08-20
description: "A Home Assistant button that opens a tmux window with a fresh Claude Code session, drivable from the phone while it lives. Plus the two-tmux-servers trap."
cast: "/casts/bouton-claude.cast"
poster: "npt:0:08"
caption: "A simple ask — start Claude Code at boot inside tmux — that hits a real trap (two tmux servers in the same container), then ends as a Home Assistant button: each press opens a tmux window with a new Claude, drivable from the app while it lives."
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, edited afterwards from the real session transcript. The prompts and the stop messages are the ones from the actual session; the timing is compressed and the long waits are cut. Hostnames sanitized."
---

The detail that makes this session strange: Claude Code is configuring its
own autostart, from inside the container it runs in — and the first attempt
lands in the wrong tmux server, invisible to the operator's `tmux ls`. Same
container, two sockets.

Once the right socket is found, the rest falls into place: a declarative
systemd unit that GitOps deploys on its own, then three Home Assistant
entities — a button that opens a tmux window with a new Claude Code (remote
control on), a button that closes the last one, a sensor that counts them.

Each window prints a session URL: open it in the app and you are driving the
same session — typing in the app updates the terminal, and the other way
around.

The limit, discovered afterwards: this only holds for *live* sessions. A
closed session cannot be resurrected from the app — resuming one is still a
`/resume` in the tmux pane, over SSH. The button hires new Claudes; it does
not wake the dead.
