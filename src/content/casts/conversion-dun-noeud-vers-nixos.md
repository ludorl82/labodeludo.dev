---
title: "Une conversion de nœud vers NixOS"
pubDate: 2026-07-25
description: "Une machine réinstallée par SSH, sans écran ni clé USB. Le Secure Boot et un initrd trop gros sont les vrais obstacles."
cast: "/casts/nixos-migration.cast"
poster: "npt:0:06"
caption: "Une conversion de nœud du début à la fin, condensée en moins de deux minutes. Le Secure Boot et l'initrd qui refuse de se décompresser sont les vrais murs de cette session."
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle de la session. Les demandes et les messages d'arrêt sont ceux de la vraie session; le minutage est compressé et les longues attentes sont coupées. Noms d'hôte sanitisés."
article: "migrer-tout-mon-homelab-vers-nixos"
---

Une des neuf machines du parc, convertie de bout en bout par SSH avec
`nixos-anywhere` — pas d'écran branché, pas de clé USB, la machine se réinstalle
toute seule et revient sous NixOS.

Les deux murs de la session sont ceux qu'on ne voit pas venir : le Secure Boot
qui bloque le `kexec`, et un initrd qui refuse de se décompresser faute de
mémoire.
