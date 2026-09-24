---
title: "La réponse par la mauvaise patte, pour vrai"
pubDate: 2026-09-25
description: "La panne du SSH qui gèle, rejouée pour vrai et captée telle quelle : la règle 102 retirée d'un hôte à deux pattes, une session du Mac qui se tait 40 secondes et ne revient jamais, la fiche de pfSense qui fond de 30 secondes à zéro, puis la règle remise et la même session qui passe, avec une fiche gardée 24 heures."
cast: "/casts/la-mauvaise-patte-real.cast"
poster: "npt:0:58"
caption: "Trois panneaux : les commandes en haut, la fiche que pfSense tient sur la session au milieu, la narration en bas. Sans la règle 102, 20 paquets dans un sens, zéro dans l'autre, et une fiche qui expire à 30 secondes. Avec la règle, les deux sens, et une fiche gardée 24 heures."
article: "la-reponse-par-la-mauvaise-patte"
session: "aucune"
frame: "none"
disclaimer: "✔ Ceci est une capture réelle, faite le 24 septembre 2026 avec asciinema dans une session tmux dédiée, sans montage. vm-02, mac et routeur sont des alias SSH vers les vraies machines, et le filtre anonymise, visible à l'écran, remplace à la volée les vraies adresses par celles de l'article; fiche est un petit script qui lit la table d'états de pfSense (pfctl -ss -vv) à travers ce filtre. Pour rejouer la panne, la règle 102 a été retirée de vm-02 le temps de la prise, puis remise. Les frappes ont été envoyées par script et non tapées par Ludo, l'invite est « ludo@labo », seules les pauses de plus de deux secondes sont raccourcies, l'identifiant du conteneur dans la barre tmux est remplacé par un nom de même longueur, et un chiffre de la narration (22:0, repris de l'article) a été corrigé en 20:0 pour correspondre à l'écran."
---

La panne de [l'article](/blog/la-reponse-par-la-mauvaise-patte/), rejouée le jour
même, pour vrai. Le client est le Mac, le seul appareil qui soit uniquement sur le
VLAN 50 : `ssh -J mac vm-02` fait ouvrir la connexion TCP par le Mac, vers
l'adresse VLAN 10 de vm-02, en passant par pfSense. C'est exactement le chemin
qui gelait.

En haut, les commandes. On lit d'abord les trois règles du module sur vm-02, on
retire la 102, puis le Mac envoie une ligne après 40 secondes de silence. Au
milieu, un `watch` qui relit toutes les deux secondes la fiche que pfSense tient
sur cette session : `SYN_SENT:CLOSED`, vingt paquets dans un sens, zéro dans
l'autre, et une échéance qui fond de 30 secondes à zéro. La fiche disparaît, la
ligne ne passe jamais, et l'essai est coupé par son propre délai à 60 secondes.

Ensuite, la règle remise, et le même essai. Cette fois, la fiche passe à
`ESTABLISHED:ESTABLISHED`, avec des paquets dans les deux sens et une échéance à
24 heures, et la ligne arrive après ses 40 secondes de silence.

Ce qui a été touché après la prise, et rien d'autre : les pauses de plus de deux
secondes, l'identifiant du conteneur dans la barre tmux, et un chiffre de la
narration, que j'avais repris de l'article (22:0) alors que l'écran disait 20:0.
Les adresses, elles, sont fictives dès l'écran : elles passent par le filtre
`anonymise` qu'on voit dans les commandes.
