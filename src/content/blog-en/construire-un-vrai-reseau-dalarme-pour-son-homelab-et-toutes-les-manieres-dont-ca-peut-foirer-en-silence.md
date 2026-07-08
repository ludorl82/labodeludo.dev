---
title: "Building real alerting for a homelab (and every quiet way it can fail)"
pubDate: 2026-07-06
description: "Building a centralized monitoring dashboard (Uptime Kuma + ntfy) for a homelab ended up uncovering a mis-scoped Windows firewall rule, DNS rebinding protection, a JSONata bug, a UTC trap, and a parallel session that had quietly renamed an admin account."
tags: ["DevOps", "bob"]
heroImage: "/images/blog/banner-kuma-en.svg"
---
A homelab breaks. That's normal. The real problem isn't the outage itself — it's finding out about it three days later by stumbling onto it.

Three real examples, at different times:

-   A network watchdog that had silently stopped working for several days — discovered while investigating an unrelated problem.
-   A voice-assistant service left down after a reboot, with no notification at all.
-   A backup pipeline with its own local logging, tucked away somewhere nobody ever looks.

Three different monitoring mechanisms, three different log locations, and above all: **no central alert channel**. In both real incidents that motivated this project, the outage was discovered after the fact, never actively reported.

The fix: a private Uptime Kuma instance (VPN-only) wired to ntfy for push notifications, migrating every existing watchdog to this one central point, one at a time.

![Diagram of the three traps found while building the Uptime Kuma alerting](/images/blog/diagram-kuma.png)

## Round 1: the first three watchdogs

Three services, three different mechanisms depending on their nature:

| Watchdog | Monitor type | Why |
| --- | --- | --- |
| Ollama service on a Windows PC | Active HTTP | Kuma can query its API directly |
| IPv6 watchdog (cron script) | Push (dead man's switch) | It's a script — easy to add a heartbeat at the end of the run |
| Daily backup | Push | Only runs once a day, active polling doesn't fit |

It looked simple. It wasn't quite.

**First real network bug found along the way**: the central server couldn't reach the Windows PC hosting Ollama at all — not on its main IP, not on a secondary one — while other machines on the same network answered fine. The culprit: the Windows firewall rule was scoped to "local subnet," which lets traffic from other devices at home through but blocks traffic arriving over the VPN tunnel, whose source address doesn't match that subnet. Temporary workaround: switch that monitor to push mode instead of active polling, until the real cause could be dug into later.

Second surprise: the home firewall's local DNS resolver was silently blocking internal queries pointing at private IPs (anti-rebinding protection), which would have made the IPv6 watchdog's heartbeat fail forever with no obvious explanation. Fixed with a targeted exception on the internal domain involved.

Three monitors migrated, two real network bugs found and fixed along the way. Not bad for "just wire up a dashboard."

## Round 2: the Windows firewall, for real this time

The push workaround for Ollama eventually got fixed properly: the real cause wasn't the source address originally suspected, but the VPN tunnel's actual egress address, combined with the machine having two different default gateways — causing asymmetric routing that the router's firewall silently dropped. Once fixed with a broadened firewall rule and a static route, the Ollama monitor went back to simple active HTTP polling, simpler to maintain.

Two other machines on the network (a Home Assistant box, a NAS) had exactly the same kind of routing problem — same bug class, fixed the same way, monitors added once connectivity was confirmed.

## Round 3: the camera that lies without knowing it

A "Frigate responds" monitor isn't enough: Frigate can happily answer HTTP 200 while the camera itself is dead. Fix: a "JSON Query" monitor that reaches directly into Frigate's stats API for the camera's frames-per-second counter, with a boolean expression (`camera_fps > 0`). Gotcha hit along the way: the expression engine used isn't plain JSONPath but JSONata, with its own escaping rules — worth checking against a real payload before trusting the syntax.

Even trickier: a monitor that checks recordings are actually being written continuously (not just that the camera is up). That catches the case "Frigate is up, the camera is up, but recording silently stopped" — a state nothing else detects. The script compares the cumulative duration recorded over the hour, with a few minutes of tolerance for gaps to absorb small hiccups. The trap here: Frigate's API buckets hours in UTC, not local time — worth remembering when computing "how many minutes have elapsed this hour."

## The dumb bug that wasted the most time

One day, the ntfy app sends a notification, you tap "open monitor," and it lands nowhere useful. Digging in: the ntfy notification provider's "open" button uses the URL field **of the monitor itself**, not Kuma's base URL. Except Push-type monitors (and, side discovery, Port-type monitors too) simply have no URL field by default — so the button is broken by construction for that kind of monitor. Fix: give them a dummy URL at creation time, just so the button works.

Small amusing detail: this bug got rediscovered a second time, weeks later, on a brand-new batch of monitors — proof it's worth writing down in black and white rather than relying on memory.

## The accidental identity theft

A home video-streaming service kept mysteriously restarting. The investigation followed a real chain of dominoes:

1.  The NAS hosting it had rebooted on its own several days earlier (limited RAM, exact cause never confirmed).
2.  The service didn't come back up automatically afterward despite config saying it should — a stale PID file was left behind.
3.  A cron watchdog was added (checks the process, restarts if dead, pushes a heartbeat).
4.  The monitor started flapping (up/down in a loop) — panic.
5.  Cause of flap #1: an internal DNS service formerly hosted at home had just been decommissioned, breaking resolution of the hostname used by the heartbeat script. Fixed by pinning the IP address directly in the HTTP call, without depending on DNS.
6.  Cause of flap #2, completely unrelated: the heartbeat interval configured in Kuma (2 minutes) was shorter than the actual cadence of the cron job pushing the heartbeat (5 minutes) — so Kuma systematically marked the monitor "down" between runs, before flipping it back "up" at the next heartbeat. Entirely self-inflicted flapping, with nothing to do with DNS. Fixed by widening the interval.

Two independent bugs, the same symptom, discovered one after the other. A good lesson: don't stop at the first plausible explanation.

## The admin account that changes its name mid-flight

One last twist: an attempt to automate monitor creation via the API failed with "incorrect password" — even though the password, copy-pasted straight from the password manager, was clearly correct. First red herring explored: a version mismatch between the client library and the Kuma server. Ruled out, revisited, ruled out again.

The real explanation, found by cross-referencing server logs with a personal work log: a **parallel session**, earlier that same day, had renamed the admin account for a completely unrelated reason, without documenting it anywhere at the time. The username used for API authentication was simply stale — nothing to do with a compatibility bug.

Moral: when two work sessions touch the same infrastructure on the same day without seeing each other, the first plausible technical explanation isn't always the right one. Keeping even a minimal written trail of every "invisible" state change (like renaming an account) would have avoided going in circles.

## Where things stand today

The central dashboard now covers a good fifteen services: internal DNS, automated backups, the home voice service, home automation, network storage, the streaming server, the surveillance camera and its full recording pipeline (capture → local mirror → cloud sync). Every outage pushes a notification to the phone within seconds, tested and confirmed both ways (deliberately triggering a fake outage, then a return to normal) for each new monitor.

What was supposed to be "wire up a monitoring dashboard" ended up uncovering a misconfigured firewall, forgotten DNS rebinding protection, a reproducible Kuma UI bug, a UTC time-bucket trap, and a classic case of the left hand not knowing what the right hand was doing. Monitoring doesn't just watch the infrastructure — it always ends up exposing it.
