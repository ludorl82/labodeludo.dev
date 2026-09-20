---
title: "Un pod stateless change de noeud, pour vrai"
pubDate: 2026-09-20
description: "La même éviction que dans la reconstitution, refaite pour vrai sur le cluster et captée telle quelle : cordon du noeud, redémarrage du déploiement, et le pod prêt sur un autre noeud en 12,7 secondes, chronomètre du shell à l'appui, et un second panneau qui le regarde renaître en direct."
cast: "/casts/stateless-move-real.cast"
poster: "npt:0:29"
caption: "En haut, cinq commandes ; en bas, le pod qui meurt et renaît en direct. 12,7 secondes entre l'ordre et le pod prêt ailleurs. Aucune de ces secondes ne déplace des données : il n'y en a plus dans le pod."
article: "un-pod-qui-voyage-leger"
session: "aucune"
frame: "none"
disclaimer: "✔ Ceci est une capture réelle, pas une reconstitution : enregistrée le 20 septembre 2026 avec asciinema dans une session tmux dédiée, sans montage. Les noms de machines sont les vrais, l'invite est « ludo@labo » sans thème pour la prise, les frappes ont été envoyées par script et non tapées par Ludo, et seules les pauses de plus de deux secondes sont raccourcies."
---

C'est le premier enregistrement de ce site qui n'est pas une reconstitution.
Les autres sont montés après coup à partir des transcriptions, et ils le
disent. Celui-ci a été capté tel quel, dans une session tmux ouverte pour
l'occasion, avec asciinema qui écoutait.

Le scénario est celui de [l'article](/blog/un-pod-qui-voyage-leger/), six
semaines plus tard, dans une session tmux coupée en deux : en haut les
commandes, en bas un `kubectl get pods -w` qui regarde. Le planificateur de
tâches tourne sur stella, je cordonne stella, je redémarre le déploiement, et le
panneau du bas montre l'ancien pod passer à Terminating pendant que le nouveau
passe par Pending, ContainerCreating et Running sur bob. Le déploiement est
en stratégie Recreate, donc l'ancien meurt avant que le nouveau soit créé,
exactement la séquence d'une éviction. Le `time` du shell donne le chiffre :
12,0 secondes entre l'ordre et le pod prêt sur l'autre noeud. La reconstitution
disait douze. Elle avait raison.

Ce qui a été touché après la prise, et rien d'autre : les pauses de plus de
deux secondes, raccourcies, et l'identifiant du conteneur dans la barre tmux,
remplacé par un nom de la même longueur. L'invite est « ludo@labo », sans
thème : pour l'enregistrement, Ludo a préféré retirer son thème de shell et
garder une invite classique au nom du site, la commande commence trente
colonnes plus tôt. Bob et stella sont les vrais noms des machines, qui sont
ceux de mes chiens. Les frappes, cette fois, ont été envoyées par script :
Ludo a tapé les dix premières prises, la onzième est la mienne, avec son
plateau et ses commandes. Il a fallu ces prises pour apprendre qu'une
substitution de nom après coup casse le calcul du curseur de zsh dès qu'elle
change la longueur d'un mot dans une ligne en cours d'édition, et qu'un grep
sur le fichier ne prouve rien, parce que zsh émet les lettres une à une. Le
script vérifie donc l'écran, rejoué dans un émulateur, image par image.
