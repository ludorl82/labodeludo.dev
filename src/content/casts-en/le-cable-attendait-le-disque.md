---
title: "The cable was waiting for the disk: four VM round trips"
pubDate: 2026-10-24
description: "An 18.8 GiB test VM goes back and forth between stella and vega, four times: on a SATA SSD then on an NVMe, through a direct 5 Gb/s cable then through the 1 Gb/s switch. Every minute, the receiving host reports what its disk writes and what its link receives."
cast: "/casts/le-cable-attendait-le-disque.cast"
poster: "npt:2:30"
caption: "On the A400, toward stella, the cable and the switch end the same: the disk drops to 55 MiB/s from the second minute, once its SLC cache is full. Toward vega, the same model, rested, writes at 228 MiB/s. On the NVMe, the cable makes the trip in 42 s, the switch in 2 min 58 s, at gigabit speed. The terminal text is in French."
article: "le-cable-attendait-le-disque"
session: "aucune"
frame: "none"
type: "prise-reelle"
court: "nvme-cast-en"
disclaimer: "✔ This is a real capture, made on October 24, 2026 with asciinema in a dedicated tmux session, with no editing. The migrations are real virsh migrate calls between stella and vega, on two test VMs with no operating system. The keystrokes were sent by a script and not typed by Ludo, the prompt is “ludo@labo”, only pauses longer than two seconds are shortened (23 minutes of tests become two and a half minutes), and the container ID in the tmux bar is replaced by a name of the same length. The terminal text and the narration are in French."
---

The `banc` script sends a test VM back and forth between stella and vega,
with `virsh migrate --live --copy-storage-all`, the same call `vm-move`
makes. During each trip, it asks the receiving host every minute what its
disk wrote and what its link received. The slower of the two sets the
duration.

Four cases: the VM's disk on the old SATA SSD (Kingston A400) or on the NVMe
(WD SN730), and the data through the direct 5 Gb/s cable or through the
1 Gb/s switch. On NVMe, the network decides, and the cable wins by four. On
the A400, the state of the receiving disk's SLC cache decides.

The full explanation is in [the article](/en/blog/le-cable-attendait-le-disque/).
