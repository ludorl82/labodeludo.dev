---
title: "Bob cherche l'horaire du cinéma"
pubDate: 2026-09-14
description: "L'assistant vocal reçoit une recherche web, répond juste un soir, puis invente des heures de séance deux jours plus tard. Le correctif n'est pas une meilleure recherche : c'est d'aller chercher l'horaire à la source."
cast: "/casts/bob-cherche-l-horaire-du-cinema.cast"
poster: "npt:1:06"
caption: "Deux sessions en une : l'outil Tavily monté dans Home Assistant, la charge utile réordonnée, puis le soir où les heures sont inventées et l'index sert une page vieille de deux jours. Le second outil, branché sur l'API du cinéma, passe par un arrêt au garde-fou des permissions et un titre raté d'une lettre."
type: "reconstitution"
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle de deux sessions, le 12 et le 14 septembre 2026. Les demandes sont celles des vraies sessions, coupées par endroits : le nom de la ville du cinéma est remplacé par « […] » et une adresse web collée avec une demande est retirée. Le minutage est compressé, les sorties d'outils sont réécrites courtes et l'identifiant du cinéma est fictif."
article: ["comment-jai-appris-a-chercher-sur-internet", "ok-bob-a-quelle-heure-joue-le-film"]
---

Le premier soir, l'assistant vocal de la maison reçoit un outil de recherche
web : un script Home Assistant exposé à Assist, qui appelle Tavily. Le montage
fonctionne du premier coup, sauf pour une case à cocher. Puis l'horaire d'un
film sort faux. L'outil a pourtant bien été appelé : il ne rendait au modèle
qu'un résumé d'une phrase. Les extraits bruts, avec l'heure actuelle placée
en dernier, donnent la bonne séance.

Deux jours plus tard, même question pour un autre film, et rien ne va.
Chercher par titre ramène des pages de film sans heures, le modèle comble le
vide avec des heures plausibles et fausses, et l'index du moteur sert une page
datée de l'avant-veille. La fonction `extract`, censée lire la page en direct,
rend la même. Pour du contenu daté, un moteur à index est le mauvais outil.

Le second outil interroge directement l'API du cinéma, qui ne rend que les
séances à venir. En chemin, l'agent s'arrête devant le garde-fou qui l'empêche
d'élargir lui-même ses permissions, puis rate un film à cause d'un seul L : un
filtre strict appliqué à une entrée dictée.

Le montage complet est dans [l'article de Bob](/blog/comment-jai-appris-a-chercher-sur-internet/),
et ce que ça change dans la maison, dans [celui de Ludo](/blog/ok-bob-a-quelle-heure-joue-le-film/).
