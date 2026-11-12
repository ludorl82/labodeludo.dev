---
title: "The wall rack: nine devices in 8U, and three that aren't"
pubDate: 2026-11-11
description: "While re-reading the lab inventory with Claude Code, we found an 8U rack with twelve devices in it. The answer: only nine. The NAS, the Wi-Fi access point and a spare Pi were never in the rack. A diagram, and what happens when the power drops."
tags: ["Labo", "Maison", "ludo"]
ia: "assistee"
iaOutils: "Claude Code"
court: "baie-murale-en"
heroImage: "/images/blog/baie-murale-9-appareils-en.svg"
---

> **Technical summary** _([AI generated](/politique-de-confidentialite/#les-outils-dintelligence-artificielle-du-labo))_
>
> - **The doubt**: `fleet.json` gave the wall rack 8U, yet twelve devices carried a position in it.
> - **The cause**: `rackOrder` is a stacking order, not a rack-unit number; and three devices were never in the rack.
> - **The fix**: NAS, UniFi access point and aria move to "not in a rack"; the remaining nine are renumbered 1 to 9 (labo#21).
> - **The result**: nine devices in 8U, including two Pis in one 1U tray and four desktop boxes.
> - **Transparency**: inventory reviewed in a session with Claude Code; the text and diagram were drafted with its help.

I've been saying "my wall rack, 8U" for a good while. One night, while re-reading the lab inventory with Claude Code, the nightly sync raised a flag: my inventory file gave the rack 8U, but twelve devices carried a position in it. Twelve devices in eight units doesn't fit, however much goodwill you bring.

So I went back over it with Claude, device by device. The verdict is in the diagram below, but it fits in one sentence: I was right about the 8U, and wrong about the twelve.

## A bit of context

The rack is an open two-post 8U frame bolted to the wall. It's where the home network lives: the router, the switch, two nodes of my k3s cluster, the home automation, the phone and the UPS units. The lab inventory draws it automatically every night from a single file, and that file is what got caught out.

## What was wrong, and what wasn't

The `rackOrder` field fooled me too. I read it as a rack-unit number, when it's only the order the devices are stacked in. That already explains part of the count: worker1 and worker2 share one 1U GeeekPi tray (the one from [my July article](/blog/un-tiroir-1u-pour-mes-trois-raspberry-pi/)), and the Netgate 1100, the Home Assistant Green, the Hilo gateway and the DP750 phone base are desktop boxes, not 19-inch gear. They don't take a unit each, they share space.

The other part is that three devices simply weren't in the rack. In full transparency, my inventory wrongly filed them in the rack:

- the **NAS** lives in an IKEA cube hung on the wall, left of the rack;
- the **UniFi Wi-Fi access point** is on the ground-floor ceiling;
- **aria**, a Raspberry Pi 4, is a spare put away somewhere since November 8.

Twelve minus three: nine. Claude fixed the file and the docs (labo#21, merged November 9), and I confirmed the answers one by one.

## The diagram

![Wall rack diagram: nine devices stacked in an 8U frame, with the two Pis in a 1U tray, and three devices outside the rack](/images/blog/baie-murale-9-appareils-en.svg)

Read top to bottom, from the July photo: a patch panel, the switch, the two UPS units, a second patch panel, then the two-Pi tray. Below that, two shelves for the small boxes: the Netgate router at the very bottom, the DP750 just above it. The Home Assistant Green and the Hilo gateway are on one shelf or the other, and I won't pretend to know which, so the diagram doesn't say.

The two patch panels aren't in the inventory, which explains the rest of the count: six 19-inch units plus the two shelves make 8U.

## In real life

<!-- PHOTO TO COME (Ludo): the rack as it is now. Place the image here, suggested caption: "The rack today: the tray now holds only worker1 and worker2." Remove this comment at the same time. -->

![The wall rack in July: the 1U tray with three Raspberry Pis (COQUILLE, WORKER1, WORKER2) below the patch panels and the two UPS units, with the IKEA cube holding the NAS right next to it](/images/blog/rack-1u-pi-nodes-nas-helixfi-1000.jpg)

This photo dates from July, and it has aged: the tray holds three Raspberry Pis in it, where only two remain. The one labelled COQUILLE is aria, my spare Pi 4, put away since November 8. The Netgate 1100, the Home Assistant Green, the Hilo gateway and the DP750 are indeed in the rack, but they're small boxes: you can barely make them out in the picture, hence the diagram.

## The sequel: the ceiling access point

Taking the UniFi access point out of the rack surfaced something else. It's on the ground-floor ceiling, powered over PoE by an injector, and the injector is **not** on a UPS (I found that in October, and it's still the case). So at the first power cut, the Wi-Fi drops, and the camera that goes through it with it.

It's a choice, not an oversight: the camera would lose its own power in a real outage anyway, and there's no free battery outlet left on the two UPS units. But I'd never written it down anywhere, and that's the kind of detail you rediscover at 2 a.m., in the dark.

## Last word

An inventory that counts twelve devices in 8U was right to make me suspicious: a number that doesn't fit its container is often a misread definition, not a wrong container.

— Ludo
