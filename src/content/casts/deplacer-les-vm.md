---
title: "Mes VM changent de maison"
pubDate: 2026-10-08
description: "Trois sessions autour du déplacement des VM entre deux hyperviseurs : le NAS écarté comme stockage partagé, le script et les boutons de Home Assistant construits en un après-midi, les refus rencontrés en chemin, la console qui déplace sa propre session, puis la règle de marge qui refuse un déplacement pour vrai."
cast: "/casts/deplacer-les-vm.cast"
poster: "npt:1:30"
caption: "Le fil de trois sessions : le NAS écarté, le plan en trois morceaux, un outil manquant et un build cassé que la CI ne voyait pas, win11 refusée deux fois, la console qui survit à son propre déplacement, les interrupteurs k3s, puis un refus de la règle de marge, quatre jours plus tard."
frame: "none"
type: "reconstitution"
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir des transcriptions réelles de trois sessions, les 7, 8 et 12 octobre 2026. Les demandes de Ludo sont citées mot pour mot, fautes comprises, sauf les noms d'hôtes; les sorties d'outils sont réécrites et raccourcies, le minutage est compressé et les noms sont sanitisés : console-vm est la console, k3s-a et k3s-b les deux noeuds k3s sans carte graphique."
article: ["virsh-migrate", "corollaire-copier-une-cible-qui-bouge"]
---

Un redémarrage de serveur venait de figer la console. La première idée de Ludo :
mettre le disque de la console sur le NAS et la rendre hautement disponible
entre les deux hyperviseurs. L'agent la déconseille, faits du labo à l'appui :
le NAS redémarre seul après une mise à jour de son firmware, et un montage NFS
bloqué fige l'hôte au complet. Il propose de copier le disque à la place. Ludo
ne veut pas de relève automatique, seulement des déplacements qu'il déclenche
lui-même, depuis Home Assistant.

Le lendemain, le module, le script et les boutons arrivent en un après-midi,
avec leurs ratés : un outil absent de la liste déclarée du script, puis une
simple note de shellcheck qui casse le build de l'hôte pendant que la CI reste
verte, parce qu'elle évalue la configuration sans la compiler. win11 est
refusée deux fois, pour une carte graphique puis pour une fonction de son
processeur virtuel. Puis la console se déplace elle-même, avec la session qui
écrit le script à l'intérieur : sept minutes, et la session répond depuis
l'autre serveur.

Quatre jours plus tard, la règle de marge refuse un déplacement pour vrai,
avant d'avoir touché à quoi que ce soit.

L'article : [Un vMotion sans VMware, et sans stockage partagé](/blog/virsh-migrate/).
