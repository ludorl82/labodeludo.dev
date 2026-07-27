---
title: "Casser son propre quorum etcd"
pubDate: 2026-07-27
description: "La même commande, deux fois. La première fois elle est sûre, la deuxième elle met le cluster à terre — parce que le nombre de votants a changé entre les deux."
cast: "/casts/control-plane-consolidation.cast"
poster: "npt:0:08"
caption: "Le démontage d'un plan de contrôle à trois nœuds vers un seul. La panne au milieu est auto-infligée, et la commande qui la répare se fait bloquer par le garde-fou de permissions pendant que le cluster est à terre."
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle de la session. Les demandes et les messages d'arrêt sont ceux de la vraie session; le minutage est compressé et les longues attentes sont coupées. Noms d'hôte sanitisés, et une partie des nœuds de travail est retirée de l'affichage — c'est indiqué à l'écran."
article: "je-me-suis-vote-hors-de-l-ile"
---

Retirer deux membres etcd d'un plan de contrôle qui en compte trois. Le premier
part sans broncher. Le deuxième, avec exactement la même séquence de commandes,
coupe l'API du cluster net — parce qu'à deux membres, il n'y a plus de majorité
à perdre.

Ce qui rend l'enregistrement intéressant, ce n'est pas l'erreur elle-même : ce
sont les trente secondes qui suivent. La commande de récupération se fait
refuser par le classificateur de permissions, pendant que le cluster est en
panne. Le garde-fou fait exactement sa job — au pire moment possible.
