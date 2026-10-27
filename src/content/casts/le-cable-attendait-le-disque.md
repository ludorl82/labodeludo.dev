---
title: "Le câble attendait le disque : quatre allers-retours de VM"
pubDate: 2026-10-24
description: "Une VM d'essai de 18,8 Gio fait l'aller-retour entre stella et vega, quatre fois : sur un SSD SATA puis sur un NVMe, par un câble direct de 5 Gb/s puis par la switch de 1 Gb/s. À chaque minute, l'hôte d'arrivée dit ce que son disque écrit et ce que son lien reçoit."
cast: "/casts/le-cable-attendait-le-disque.cast"
poster: "npt:2:30"
caption: "Sur l'A400, vers stella, le câble et la switch finissent pareil : le disque tombe à 55 Mio/s dès la deuxième minute, quand son cache SLC est plein. Vers vega, le même modèle reposé écrit à 228 Mio/s. Sur le NVMe, le câble fait l'aller en 42 s, la switch en 2 min 58 s, au débit du gigabit."
article: "le-cable-attendait-le-disque"
session: "aucune"
frame: "none"
type: "prise-reelle"
court: "nvme-cast"
disclaimer: "✔ Ceci est une capture réelle, faite le 24 octobre 2026 avec asciinema dans une session tmux dédiée, sans montage. Les migrations sont de vrais appels à virsh migrate entre stella et vega, sur deux VM d'essai sans système. Les frappes ont été envoyées par script et non tapées par Ludo, l'invite est « ludo@labo », seules les pauses de plus de deux secondes sont raccourcies (23 minutes de tests deviennent deux minutes et demie), et l'identifiant du conteneur dans la barre tmux est remplacé par un nom de même longueur."
---

Le script `banc` lance une VM d'essai en aller-retour entre stella et vega,
avec `virsh migrate --live --copy-storage-all`, le même appel que `vm-move`.
Pendant chaque trajet, il interroge l'hôte d'arrivée toutes les minutes : ce
que son disque a écrit, ce que son lien a reçu. Le plus lent des deux fixe la
durée.

Quatre cas : le disque de la VM sur l'ancien SSD SATA (Kingston A400) ou sur
le NVMe (WD SN730), et les données par le câble direct de 5 Gb/s ou par la
switch de 1 Gb/s. Sur NVMe, le réseau décide, et le câble gagne par quatre.
Sur l'A400, c'est l'état du cache SLC du disque d'arrivée qui décide.

L'explication complète est dans [l'article](/blog/le-cable-attendait-le-disque/).
