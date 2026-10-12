---
title: "Le pipeline appuie sur apply"
pubDate: 2026-07-31
description: "Un outil choisi par dépôt, une porte anti-destroy testée contre un vrai enregistrement DNS, puis le même merge livré côté NixOS par comin, sans personne au clavier."
cast: "/casts/iac-apply.cast"
poster: "npt:0:14"
caption: "Le choix d'un outil par dépôt, la porte anti-destroy testée contre un enregistrement réel, puis le même merge livré côté NixOS par comin, sans personne au clavier."
article: "laisser-le-pipeline-appuyer-sur-apply"
type: "reconstitution"
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle de la session. Les demandes et les messages d'arrêt sont ceux de la vraie session; le minutage est compressé et les longues boucles de surveillance sont coupées. Noms d'hôte sanitisés; l'enregistrement DNS montré était un jetable créé pour ce test."
---

Quatre dépôts d'infrastructure déjà décrits en code, mais chaque apply passait
encore à la main. La session ferme la boucle : GitHub Actions avec OIDC pour le
nuage, Argo CD pour le cluster, comin pour NixOS.

La porte n'a pas été crue sur parole. Une première PR crée un enregistrement TXT
jetable, et il résout sur l'internet public après la fusion. Une seconde PR le
supprime, et le job refuse. Deux fois dans la journée, le classificateur de
permissions de Claude Code rend aussi la main : une fois sur `tofu apply`, une
fois sur la lecture d'un secret.
