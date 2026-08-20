---
title: "Un BIOS invisible, piloté à l'aveugle"
pubDate: 2026-08-20
description: "Un écran BIOS que personne ne peut voir, des flèches qui n'arrivaient jamais, un détour dans le mauvais firmware — et une machine récupérée sans jamais avoir vu l'écran."
cast: "/casts/bios-blind.cast"
poster: "npt:0:08"
caption: "La partie la plus absurde de la migration de la Borne, condensée : naviguer un BIOS qui ne dessine rien sur le port série, découvrir que les touches fléchées n'arrivaient jamais, atterrir dans le menu Intel MEBx par erreur, casser le boot avec les « Optimized Defaults » — puis contourner tout ça par le lecteur CD virtuel du BMC."
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle de la session. Les demandes et les messages d'arrêt sont ceux de la vraie session; le minutage est compressé et les longues attentes sont coupées. Noms d'hôte sanitisés."
article: "une-borne-darcade-qui-cohabite-avec-kubernetes"
---

Le BIOS de la Borne était invisible : la carte graphique dédiée avale la
sortie vidéo, la console iKVM ne voit rien, et le Setup ne dessine rien sur
le port série. Il fallait quand même y entrer pour débloquer l'installation
de NixOS.

Ce qui suit est une recherche à l'aveugle dans un espace qu'on ne peut pas
observer : prouver que les touches arrivent (en sauvegardant sans rien
changer), découvrir que les flèches n'arrivaient jamais (mauvais encodage
série), aboutir par erreur dans le firmware Intel ME, et casser le boot avec
un « Load Optimized Defaults ». La sortie de crise ne passe pas par le BIOS :
elle passe à côté.

C'est Claude Code qui pilotait, à distance, pendant que le propriétaire du
matériel était en vacances. L'écran BIOS n'a jamais été vu une seule fois.
