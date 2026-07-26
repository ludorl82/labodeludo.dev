---
title: "La vérification qui refuse de publier"
pubDate: 2026-07-26
description: "Le dernier filet avant qu'un dépôt devienne public : un domaine oublié, un refus net, et la correction ajoutée des deux côtés."
cast: "/casts/iac-sanitize-gate.cast"
poster: "npt:0:06"
caption: "La vérification finale avant publication : elle trouve un domaine oublié, refuse de continuer, et le nom fautif se fait ajouter à la fois à la règle de remplacement et à la vérification elle-même."
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle de la session. Les demandes sont celles de la vraie session; le minutage est compressé et les longues attentes sont coupées. Et le domaine attrapé à l'écran est déjà le nom fictif — publier une démonstration de détecteur de fuites avec la vraie valeur dedans aurait été un brin ironique."
article: "quatre-depots-pour-un-labo-au-complet"
---

Les dépôts d'infrastructure sont publiés en public après passage dans un script
de sanitisation. Ce qu'on voit ici, c'est la vérification finale qui tourne
après coup : elle relit le résultat, trouve un nom de domaine que la règle de
remplacement avait manqué, et refuse d'aller plus loin.

Le geste intéressant est la correction : le nom fautif est ajouté à la fois à la
règle de remplacement et à la vérification elle-même, pour que le prochain
oubli soit attrapé au même endroit.
