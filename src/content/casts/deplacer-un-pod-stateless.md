---
title: "Un pod stateless change de nœud en 12 secondes"
pubDate: 2026-08-07
description: "Le même drain, deux fois. Avant : le pod est riveté au disque de son nœud et son remplaçant reste Pending devant huit nœuds libres. Après la migration de son état vers S3 : prêt sur un autre nœud en 12 secondes."
cast: "/casts/stateless-move.cast"
poster: "npt:0:12"
caption: "Le même drain, avant et après : le pod riveté à son disque qui reste Pending devant huit nœuds libres, puis le pod stateless qui est prêt sur un autre nœud 12 secondes après l'éviction — parce qu'il n'y a plus rien à déménager."
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une simulation pédagogique. La migration vers S3 est réelle et les deux comportements montrés sont véridiques, mais les drains ont été rejoués pour l'enregistrement, le minutage est condensé, le stockage d'origine est simplifié en « disque local », et les noms d'hôte sont fictifs."
article: "un-pod-qui-voyage-leger"
---

Drainer le nœud où tourne mon planificateur de tâches, avant et après avoir
sorti son état vers S3.

Avant, le drain « réussit » — et le pod de remplacement reste `Pending` pour
toujours : `volume node affinity conflict`. Ses données vivent sur le disque
du nœud qu'on vient de vider, alors huit nœuds en santé donnent zéro candidat.
La seule sortie est de remettre le nœud en service.

Après, la même éviction se règle en 12 secondes, historique intact — et aucune
de ces secondes ne sert à déplacer des données, parce qu'il n'y en a plus dans
le pod. C'est toute la différence entre un workload qui *garde* son état et un
workload qui le confie à un service dont c'est le métier.
