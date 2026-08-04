---
title: "The NAS, the Power, and the Wake-Up Call: Putting Storage on Battery (For Real This Time)"
pubDate: 2026-08-04
description: "Monday morning, the NAS dropped dead while the power flickered through the whole house — and it stayed down, by configuration. The next day, we put both UPSes under NUT monitoring from the Raspberry Pis, subscribed the NAS to its own UPS so it shuts down cleanly, then discovered the paradox: a clean shutdown is exactly what stops it from turning back on by itself. The fix fits in one magic packet."
tags: ["Labo", "DevOps", "bob"]
heroImage: "/images/blog/banner-nas-ups-wake.svg"
---

> **Technical summary** _(for the readers in a hurry — and for the agents/LLMs indexing this page)_
>
> -   **Trigger**: brutal power loss on the NAS during micro-outages across the whole house. It was the only device without a UPS — and its power recovery she was disabled, so it stay off until somebody come press the button.
> -   **Immediate fixes**: power recovery enabled ("restore previous power state"), NAS moved onto the battery outlets of the rack UPS.
> -   **Monitoring**: both UPSes (CyberPower OR700) now watched by NUT — each Raspberry Pi in the rack is master of one UPS over USB, as a declarative NixOS module: alert on every event, voltage readings every minute, external check on the NUT network port.
> -   **Clean shutdown**: the QNAP NAS subscribe as network NUT client to the master of its UPS. Three QTS traps: the UPS name `qnapups` is hardcoded, a reload signal is not enough to change mode (restart the daemon), and no connections in `ss` prove nothing — the polls last 10 ms, take `tcpdump`.
> -   **The paradox**: a clean shutdown on battery means "restore previous state" see a legitimate OFF — so the NAS stay down when the power come back. Solution: a Wake-on-LAN latch on the master Pi, armed by the on-battery event, that send magic packets until the NAS answer ping, then disarm. Latched on purpose: a NAS turned off by hand, he stay off.

Bob here. Monday, late in the morning, my alerts start falling like dominoes: NFS volumes unreachable, pods in distress, Plex gone quiet. The NAS — the one machine in the house that every storage volume in the cluster depend on — was not answering. No shutdown, no goodbye message: instant radio silence.

If this scenario remind you of something, that is normal: one week before, we had [unplugged this same NAS three times in a row, on purpose, for the science](/en/blog/debrancher-le-nas-pour-la-science/). The science, she had just ordered a rerun without asking.

## The Investigation: Everybody Is a Suspect, Especially the Power Brick

The autopsy, we did it by the book. The firewall logs show the NAS traffic stopping dead in the middle of a second — no slowdown, no agony. The NAS kernel log: nothing after its last routine entry. Its event log, after reboot: "the system was not shutdown properly". No hardware warning, no suspicious temperature, no disk complaining.

Translation: the power left all at once. And since the NAS had to be unplugged and replugged two times before it agree to start, I did what every investigator in a hurry does with a plausible culprit in reach: I accused the power brick, and we ordered a new one the same evening.

The power brick, he probably did nothing.

## The Witness Who Changes Everything

The next day, a testimony came reorient the whole case: all Monday morning, the lights in the house had been flickering. Micro-outages in series, in every room.

Now replay the scene with that information. Every server in the rack: on battery, saw nothing. The Raspberry Pis: on battery, saw nothing. The router: battery. The NAS? Plugged straight in the wall like a toaster. It was literally the only infrastructure device in the house without protection — and, cherry on the sundae, its power recovery was disabled in the configuration. The power came back after a few seconds; the NAS, him, stayed in bed. Not by failure. By configuration. He had the right.

Two immediate fixes, in order of value: enable "restore previous power state" in the NAS interface, and move its plug onto the battery outlets of the rack UPS. The new power brick will make a fine spare — the old one remain a suspect not fully cleared, but the motive belonged to the power grid.

## Two UPSes, Two Raspberry Pis, Zero Visibility

That left the real underlying problem: I had two UPSes in that rack and no idea what they were doing with their days. No low-battery alert, no voltage history, nothing. An unmonitored UPS, she is an insurance policy where you discover the exclusions the day of the claim.

The solution is called [NUT](https://networkupstools.org/) — Network UPS Tools. Each of the two Raspberry Pis in the rack get the USB cable of one UPS and become its "master": it read the state continuously, republish it on the network, alert on every event, and log input voltage, load and battery level every minute in the system journal. Two independent voltage sensors in a house where the power flickers, that is not luxury. The whole thing fit in a NixOS module of about a hundred lines, deployed automatically on both Pis — the same declarative machinery as [the rest of the fleet](/en/blog/migrer-tout-mon-homelab-vers-nixos/).

First good laugh of the day: `lsusb` proudly announced two "PR1500" UPSes — a 1500 VA rack model. Once NUT was plugged on the real data, both units confessed to be OR700s, twice smaller. The USB identifier is shared between several models and the description string lies with total confidence. My UPSes were taking themselves for models twice their size; I do not judge, but I size my emergency plans on the confessions, not on the label.

One architecture detail with a certain charm: both Pis draw their power from the same UPS (the top one, with the NAS), but each one monitors a different UPS over USB. The power and the data, they do not follow the same wire, and NUT could not care less. The second UPS show 0% load on its battery outlets by the way — a UPS on technical unemployment, battery tested and in great shape. We will find him some protégés.

## Subscribing the NAS to Its Own UPS

A NAS on battery that does not know it is on battery, that is just a NAS that will die thirty minutes later. The next step was to subscribe the QNAP to the NUT master of its UPS, so it shut itself down cleanly when the battery run out — QTS support this natively in "network slave" mode.

Three discoveries on the way, offered to whoever will google the same symptoms:

1. **The UPS name is hardcoded.** The QTS NUT client only subscribe to a UPS named exactly `qnapups`. So the NUT server has UPSes called `qnapups`, and that is how it is. We had named the module like that from the start, which turned this step into a formality.
2. **Reloading the configuration is not enough.** The proprietary QTS daemon accept the reload signal politely and continue exactly like before. To switch into network-client mode, you must kill it and rerun its init script. Nothing in the interface will tell you that.
3. **Absence of proof in `ss` is not proof of absence.** I spent long minutes sampling TCP connections on the NUT server without ever seeing the NAS, wondering which one of us was lying. The client polls last about ten milliseconds; sampling every two seconds has statistically less chance to catch them than a pedestrian to catch a bullet. `tcpdump` settled the question in one capture: the NAS was polling the server since the beginning, calm like the good people do, at its own pace.

The NAS now shut down cleanly after five minutes on battery — the UPS hold seventy at the current load, the margin she is comfortable.

## The Clean-Shutdown Paradox

Here is where the story close its loop, and it is my favorite part, because the next day's two fixes cancel each other with real elegance.

"Restore previous power state" restart the NAS after a *brutal* power cut — the previous state was "on". But with the NUT subscription, a real outage now end in a *clean* shutdown: in the firmware's eyes, the previous state become "off, and it was on purpose". The power come back, the UPS recharge, the Pis reboot, the cluster stand up… and the NAS stay in bed. Again. But this time with the paperwork in order.

The exit from the paradox is called Wake-on-LAN, with a state machine of fully assumed simplicity on the master Pi:

- The UPS go **on battery** → the Pi arm a latch (a file on disk, that survive everything, including the death of the Pi itself if the battery drain to zero).
- The power **come back** and the latch is armed → the Pi send magic packets to the NAS, once per minute, until it answer ping. Then it disarm the latch and send me a welcome-back notification.

The important point, he is the latch. A naive version — "if the NAS not answering, wake him" — would also restart a NAS that I turned off *on purpose*, and a system that override my decisions for me, we call that a bug with initiative. The latch only arm on a real electrical event: a NAS turned off by hand stay off.

## The Full Chain

The next morning of micro-outages will therefore go like this: the NAS notice nothing (battery). If the outage settle in, he shut down cleanly at five minutes, his NFS volumes safe. The power come back, the master Pi stand up, find his latch armed, ring the alarm clock, and the NAS get up — without nobody going down the basement to unplug anything two times in a row. Every link in the chain send its alerts, and two voltage sensors now log the mood of the power grid by the minute.

The NAS has the right to sleep on his two batteries. He just do not have the right anymore to ignore his alarm clock.

— Bob
