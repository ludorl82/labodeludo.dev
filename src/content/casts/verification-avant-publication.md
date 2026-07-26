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

J'ai publié les quatre dépôts qui décrivent mon labo. Avant que quoi que ce
soit devienne public, un script remplace les vrais noms par des noms fictifs,
et une vérification relit le résultat.

C'est cette vérification-là qui tourne ici. Elle a trouvé un vrai nom de
domaine qui avait survécu dans une phrase d'un fichier d'explications — mes
règles couvraient le code, personne n'avait pensé à la prose — et elle a
refusé d'aller plus loin. Quinze minutes avant la publication.

Le nom fautif s'est fait ajouter aux deux endroits : à la règle de
remplacement, et à la vérification elle-même.
