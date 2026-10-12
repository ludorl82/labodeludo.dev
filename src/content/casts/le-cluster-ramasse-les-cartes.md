---
title: "Le cluster ramasse les cartes"
pubDate: 2026-09-14
description: "Une GTX 960 sans emploi, donnée à Kubernetes : le pilote sur l'hôte fige le noyau sans jamais dire « carte graphique », le pilote part dans une VM, un bissect se trompe de suspect, et le cycle d'échange des cartes, rejoué en direct, sort quatre bogues."
cast: "/casts/le-cluster-ramasse-les-cartes.cast"
poster: "npt:1:33"
caption: "Le fil GPU d'une soirée : le nœud Ready qui ne démarre plus rien, la photo de l'écran qui corrige le diagnostic, la VM de calcul, le lecteur CD vide qui fausse le bissect, la ligne de XML qui débloque trois cartes, puis les quatre bogues de l'échange. L'agent s'arrête quatre fois et se corrige trois fois."
frame: "none"
type: "reconstitution"
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle de la session des 14 et 15 septembre 2026. Les demandes de Ludo sont citées mot pour mot, fautes comprises, à part les noms de machines remplacés par ceux de l'article; les sorties d'outils sont réécrites et raccourcies, le minutage est compressé et les noms sont sanitisés."
article: ["quand-personne-ne-joue-le-cluster-ramasse-les-cartes"]
---

La demande est simple : brancher la nouvelle RTX 3050 sur la première VM de
jeu et rendre la GTX 960 disponible pour Kubernetes. Le pilote NVIDIA part sur
l'hôte, et au redémarrage la tour devient un fantôme : le nœud s'affiche
`Ready`, son bail se renouvelle, et plus aucun conteneur ne démarre. L'agent
accuse d'abord le `PATH` de k3s, puis s'enferme lui-même dehors en martelant
`sshd` pendant le démarrage. C'est une photo de l'écran qui tranche : une
chaîne de tâches bloquées dans le noyau, `modprobe` coincé derrière `bridge`.

Le pilote est retiré de l'hôte et confié à une VM de calcul, vm-03. En
l'écrivant, l'agent rattrape un appel `virsh` synchrone dans le hook libvirt,
qui aurait pu bloquer la VM de jeu qu'il devait aider. Puis vient l'emprunt
des deux 3050 : trois cartes ne démarrent pas, et le bissect accuse les
cartes alors qu'il comparait une VM avec CD d'installation à une VM sans.
L'agent s'arrête à une seule carte ; c'est Ludo qui relance, et
`<rom bar='off'/>` règle le tout.

Le dernier temps fort est l'échange lui-même, testé en direct : un `sudo`
masqué par le `PATH`, un cordon qui survit au redémarrage, une unité
`systemd-run` à nom fixe qui refuse de repartir, un arrêt envoyé avant que
l'agent invité soit debout.

L'histoire complète, racontée par Bob, est dans
[Quand personne ne joue, le cluster ramasse les cartes](/blog/quand-personne-ne-joue-le-cluster-ramasse-les-cartes/).
