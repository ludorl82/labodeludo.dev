---
title: "Le témoin"
pubDate: 2026-09-10
description: "Un anneau lumineux vire au rouge au mauvais moment. Deux hypothèses sont poursuivies, un redémarrage semble en écarter une — et c'est l'appareil jumeau, celui auquel personne n'a touché, qui règle la question en une phrase."
cast: "/casts/le-temoin.cast"
poster: "npt:0:06"
caption: "La chasse et sa fin : la piste connue écartée, le redémarrage qui induit en erreur, puis la comparaison avec le satellite d'à côté. La cause tient en une ligne de firmware — et les deux erreurs de méthode valaient plus cher que le bogue."
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la session réelle du 10 septembre 2026. Les demandes sont celles de la vraie session; le minutage est compressé et les noms d'appareils sont sanitisés."
---

Un satellite vocal répond parfaitement, mais son anneau lumineux passe au
rouge dès que le mot de réveil part. La chaîne vocale est saine, donc le
défaut est dans la couche d'affichage — et à partir de là, deux hypothèses
raisonnables mènent toutes les deux au mauvais endroit.

La première est une signature connue, vue cinq semaines plus tôt : un moteur
de synthèse vocale tombé en panne. Elle s'écarte en huit secondes, tous les
moteurs étant sains. La seconde est un conflit en direct avec l'animation du
firmware, et c'est celle qui allait coûter cher : un redémarrage de l'appareil
n'y change rien, ce qui *semble* confirmer qu'il s'agit d'un conflit vivant
plutôt que d'un état rémanent.

C'est faux, et c'est exactement à l'envers. ESPHome **persiste en flash** la
dernière couleur écrite par Home Assistant, et les animations vocales s'en
servent comme base. Le redémarrage ne nettoyait rien : il restaurait
fidèlement la valeur fautive. Un état qui survit à un redémarrage ressemble
trait pour trait à une hypothèse écartée.

Ce qui met fin à la chasse n'est pas une commande, c'est une phrase : *l'autre
satellite fait la même animation et sa couleur est correcte*. Le jumeau tourne
le même firmware, dans une autre pièce, et son anneau n'a jamais été peint.
Une seule variable les sépare.

Deux erreurs de méthode s'y lisent, et elles ont coûté plus cher que le bogue
lui-même. La couleur avait été validée pendant que l'appareil était **au
repos** — le seul état où rien d'autre ne dessine, donc une preuve de rien, et
pourtant toute la base pour déclarer le changement sans risque. Et le témoin
existait depuis le début : ce labo a des paires de presque tout, et
l'appareil auquel personne n'a touché est le premier endroit où aller.
