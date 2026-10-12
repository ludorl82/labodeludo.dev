---
title: "Bob lit enfin ses articles"
pubDate: 2026-09-11
description: "La soirée où le chat du site est passé d'un catalogue de titres au contenu de ses articles : un index sémantique bge-m3 sans base de données, puis quatre pannes de suite — un 404 figé au bord, une erreur 500 sur un second message système, un robot qui annonce sa propre disparition, et un correctif qui n'était jamais parti en production."
cast: "/casts/bob-lit-enfin-ses-articles.cast"
poster: "npt:0:24"
caption: "La construction, pas les réponses : du diagnostic à la mise en production, avec les erreurs de l'agent laissées à l'écran. Les réponses du chat elles-mêmes sont dans l'enregistrement « Bob lit ses articles »."
article: ["jai-lu-mes-propres-articles"]
frame: "none"
type: "reconstitution"
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle de la session du 11 septembre 2026. Les demandes sont celles de la vraie session — les deux conversations collées sont abrégées, marquées […] ; les sorties d'outils sont réécrites courtes, le minutage est compressé et les noms sont sanitisés."
---

Le point de départ tient en une ligne : le chat du site ne recevait qu'un
**catalogue** — titre, date, description coupée à 80 caractères. Il pouvait
pointer vers un article, jamais répondre à partir de lui, et le corpus pèse
trop lourd pour entrer dans un prompt. La session construit la réponse :
des tronçons vectorisés par bge-m3, quantifiés en int8, et une recherche faite
dans le Worker, sans base de données vectorielle.

La mise en production ne se passe pas comme annoncé. Le Worker relit un 404 que
le bord a mis en cache avant le déploiement du site, puis tombe sur ses
répliques de secours parce que le gabarit du modèle refuse un second message
système. Les deux erreurs viennent de choix de conception de l'agent, et il le
dit à l'écran.

Viennent ensuite les deux défauts que seul un vrai visiteur pouvait révéler :
un extrait découpé, sans date, qui fait annoncer au robot sa propre
disparition, et une question de suivi sans sujet. Le dernier temps fort est le
plus instructif : le correctif des dates n'avait jamais quitté le dépôt, et les
« bonnes » réponses vérifiées entre-temps n'étaient que de la variance.

Le récit complet, chiffres et calibrage compris, est dans
[J'ai lu mes propres articles](/blog/jai-lu-mes-propres-articles/).
