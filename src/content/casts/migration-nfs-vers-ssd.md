---
title: "Migration NFS vers SSD, pilotée dans le navigateur"
pubDate: 2026-07-26
description: "Claude in Chrome configure le NAS pendant que je regarde : volume à créer, partage à renommer, permissions à corriger. Et trois arrêts nets où l'agent me rend la main."
cast: "/casts/claude-in-chrome-nas.cast"
poster: "npt:0:04"
caption: "Environ cinquante minutes de travail sur le NAS, condensées en deux minutes. La moitié en SSH n'apparaît pas."
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle de la session. Les demandes et les messages d'arrêt sont ceux de la vraie session; le minutage est compressé et les longues attentes sont coupées. Noms d'hôte sanitisés."
article: "claude-in-chrome-quand-lagent-doit-passer-par-linterface-web"
---

Le mandat : déplacer les partages NFS du cluster d'un disque dur vers un SSD,
sans que Kubernetes s'en aperçoive. Toute la moitié NAS n'existe que dans
l'interface web du boîtier, alors c'est Claude in Chrome qui l'a faite.

Ce qu'on voit passer, dans l'ordre : le refus de saisir un mot de passe à
l'écran de connexion, l'arrêt spontané quand le SSD s'avère contenir déjà
437 Go, et le zoom du navigateur qui saute à 225 % sans que l'agent puisse le
corriger. Trois arrêts, trois fois où il faut quelqu'un devant l'écran.
