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

Une des neuf machines converties dans la même journée — une machine
virtuelle. `nixos-anywhere` fait tout par SSH : il téléverse un installateur,
fait un `kexec` dedans, partitionne, installe, et la machine revient
exactement telle qu'elle est décrite dans git. Pas d'écran branché, pas de
clé USB.

En pratique, ça bloque. Deux fois plutôt qu'une ici : le Secure Boot qui
empêche le `kexec`, puis un initrd qui refuse de se décompresser faute de
mémoire.

C'est Claude Code — les modèles Fable 5 et Opus 5 — qui pilotait. Mon rôle :
valider, questionner, et débloquer ce qu'un agent n'a pas le droit de faire
tout seul.
