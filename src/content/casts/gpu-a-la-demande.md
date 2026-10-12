---
title: "Le GPU à la demande"
pubDate: 2026-08-22
description: "La journée où le deuxième poste de jeu reçoit sa carte graphique : un ajout propre en trois fichiers, puis trois pannes qui ressemblent toutes à autre chose. Un routage asymétrique, une carte qui ne revient pas de son arrêt, et une VM « injoignable » qui était simplement en pause."
cast: "/casts/gpu-a-la-demande.cast"
poster: "npt:1:41"
caption: "Le 22 août seulement : la RTX 3050 passée à arcade2, le routage par politique sur les deux postes, la carte coincée en D3cold après un arrêt raté, puis /games déménagé en qcow2 sur le NVMe quand le SSD des jeux tombe du bus. L'agent s'arrête trois fois, dont une sur un refus de permission."
frame: "none"
type: "reconstitution"
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle de la session du 22 août 2026, et de cette journée seulement. Les demandes de Ludo sont citées mot pour mot, fautes comprises, sauf une adresse remplacée par une plage de documentation; les sorties d'outils sont réécrites et raccourcies, le minutage est compressé et les noms sont sanitisés."
article: ["gpu-a-la-demande-a-la-maison"]
---

La carte est installée dans la tour, il reste à la donner au deuxième poste.
Elle est seule dans son groupe IOMMU, le changement tient en trois fichiers et
la CI passe. Le redémarrage de l'hôte que l'agent voulait faire est refusé par
le classificateur de permissions, et il s'avère inutile : la VM prend la carte
à son lancement suivant.

Le reste de la journée est une suite de symptômes qui mentent sur leur cause.
Ludo propose de retirer l'adresse du réseau maison des deux postes ; l'agent
plaide pour la garder, puis c'est Ludo qui nomme le vrai problème : un hôte à
deux pattes qui répond par la mauvaise. Ensuite, un interrupteur reste jaune :
l'invité a figé sur l'arrêt du pilote NVIDIA, et après l'arrêt forcé la carte
se lit comme une suite de `0xFF` côté hôte. Enfin, une VM « injoignable » n'a
aucun problème réseau : libvirt l'a mise en pause parce que le SSD de ses jeux
venait de disparaître du bus.

Trois arrêts de l'agent sont gardés : deux choix laissés à Ludo, et un
retrait PCI bloqué qui attend son feu vert pour redémarrer la tour. La suite,
Plasma 6, Remote Play et le retrait de la deuxième patte, s'est faite dans une
autre session et n'est pas montrée ici.

Le montage complet, et ce qui casse encore, est dans
[Le GPU à la demande à la maison](/blog/gpu-a-la-demande-a-la-maison/).
