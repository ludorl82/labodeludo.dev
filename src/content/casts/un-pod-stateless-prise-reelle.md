---
title: "Un pod stateless change de noeud, pour vrai"
pubDate: 2026-09-20
description: "La même éviction que dans la reconstitution, refaite pour vrai sur le cluster et captée telle quelle : cordon du noeud, redémarrage du déploiement, et le pod prêt sur un autre noeud en 12 secondes, chronomètre du shell à l'appui, et un second panneau qui le regarde renaître en direct."
cast: "/casts/stateless-move-real.cast"
poster: "npt:0:39"
caption: "En haut, cinq commandes ; en bas, le pod qui meurt et renaît en direct. 12 secondes entre l'ordre et le pod prêt ailleurs. Aucune de ces secondes ne déplace des données : il n'y en a plus dans le pod."
article: "un-pod-qui-voyage-leger"
session: "aucune"
frame: "none"
disclaimer: "✔ Ceci est une capture réelle, pas une reconstitution : enregistrée le 20 septembre 2026 avec asciinema dans une session tmux dédiée, sans montage. Les noms de machines sont les vrais, le nom d'utilisateur est raccourci en « ludo », et seules les pauses de plus de deux secondes sont raccourcies."
---

C'est le premier enregistrement de ce site qui n'est pas une reconstitution.
Les autres sont montés après coup à partir des transcriptions, et ils le
disent. Celui-ci a été capté tel quel, dans une session tmux ouverte pour
l'occasion, avec asciinema qui écoutait.

Le scénario est celui de [l'article](/blog/un-pod-qui-voyage-leger/), six
semaines plus tard, dans une session tmux coupée en deux : en haut les
commandes, en bas un `kubectl get pods -w` qui regarde. Le planificateur de
tâches tourne sur bob, je cordonne bob, je redémarre le déploiement, et le
panneau du bas montre l'ancien pod passer à Terminating pendant que le nouveau
passe par Pending, ContainerCreating et Running sur stella. Le déploiement est
en stratégie Recreate, donc l'ancien meurt avant que le nouveau soit créé,
exactement la séquence d'une éviction. Le `time` du shell donne le chiffre :
12,0 secondes entre l'ordre et le pod prêt sur l'autre noeud. La reconstitution
disait douze. Elle avait raison.

Ce qui a été touché après la prise, et rien d'autre : les pauses de plus de
deux secondes, raccourcies, l'identifiant du conteneur dans la barre tmux,
remplacé par un nom de la même longueur, et mon nom d'utilisateur, raccourci
en « ludo » à la même longueur aussi, pour rester cohérent avec le site. Bob et stella sont les vrais noms des
machines, qui sont ceux de mes chiens. Il a fallu sept prises : les premières
ont montré qu'une substitution de nom après coup casse le calcul du curseur de
zsh dès qu'elle change la longueur d'un mot dans une ligne en cours d'édition,
et qu'un grep sur le fichier ne prouve rien, parce que zsh émet les lettres une
à une. Le script vérifie donc l'écran, rejoué dans un émulateur, image par
image.
