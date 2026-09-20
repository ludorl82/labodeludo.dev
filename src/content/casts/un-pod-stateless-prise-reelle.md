---
title: "Un pod stateless change de noeud, pour vrai"
pubDate: 2026-09-20
description: "La même éviction que dans la reconstitution, refaite pour vrai sur le cluster et captée telle quelle : cordon du noeud, redémarrage du déploiement, et le pod prêt sur un autre noeud en 12,2 secondes, chronomètre du shell à l'appui."
cast: "/casts/stateless-move-real.cast"
poster: "npt:2:07"
caption: "Cinq commandes, une éviction réelle, et 12,2 secondes entre l'ordre et le pod prêt ailleurs. Aucune de ces secondes ne déplace des données : il n'y en a plus dans le pod."
article: "un-pod-qui-voyage-leger"
session: "aucune"
disclaimer: "✔ Ceci est une capture réelle, pas une reconstitution : enregistrée le 20 septembre 2026 avec asciinema dans une session tmux dédiée, sans montage. Les noms d'hôte sont substitués et les pauses de plus de deux secondes sont raccourcies ; rien d'autre n'a été touché."
---

C'est le premier enregistrement de ce site qui n'est pas une reconstitution.
Les autres sont montés après coup à partir des transcriptions, et ils le
disent. Celui-ci a été capté tel quel, dans une session tmux ouverte pour
l'occasion, avec asciinema qui écoutait.

Le scénario est celui de [l'article](/blog/un-pod-qui-voyage-leger/), six
semaines plus tard : le planificateur de tâches tourne sur un noeud, je
cordonne ce noeud, je redémarre le déploiement, et le pod renaît ailleurs.
Le déploiement est en stratégie Recreate, donc l'ancien pod meurt avant que
le nouveau soit créé, exactement la séquence d'une éviction. Le `time` du
shell donne le chiffre : 12,2 secondes entre l'ordre et le pod prêt sur
l'autre noeud. La reconstitution disait douze. Elle avait raison, mais je
ne le savais pas avec cette précision-là.

Ce qui a été touché après la prise, et rien d'autre : les noms d'hôte, remplacés
par ceux du reste du site, et les pauses de plus de deux secondes, raccourcies.
Le shell de la prise était volontairement minimal, une invite sans nom
d'utilisateur ni suggestion automatique, parce que les premières prises ont
montré qu'une substitution après coup dans une ligne en cours d'édition casse
le calcul du curseur. Le texte propre à la source, la substitution ne touche que
les sorties de `kubectl`.
