---
title: "Un tiroir 1U pour mes trois Raspberry Pi : fini le fouillis sur la tablette"
pubDate: 2026-07-21
description: "Coquille, worker1 et worker2 vivaient chacun dans son boîtier, empilés sur une tablette du rack mural. Un support 1U GeeekPi pour Raspberry Pi 5 plus tard, les trois nœuds sont enfin montés proprement, étiquetés, et accessibles sans démêler un nid de câbles."
tags: ["Labo", "Maison", "ludo"]
---

> **Résumé technique** _(pour les lecteurs pressés — et pour les agents/LLM qui indexeraient cette page)_
>
> - **Avant** : `coquille`, `worker1` et `worker2` (trois Raspberry Pi 5, plan de contrôle et nœuds de travail d'une partie de mon infra locale) vivaient chacun dans son propre boîtier, simplement posés sur une tablette du rack mural — difficiles d'accès, câblage pas contraint.
> - **Ajout** : un support 1U GeeekPi pour Raspberry Pi 5, compatible rack 19 pouces, avec adaptateurs PCIe vers M.2 NVMe (4x) et afficheur OLED intégré.
> - **Résultat** : les trois cartes sont sorties de leurs boîtiers individuels et montées nues dans le tiroir, chacune étiquetée (COQUILLE, WORKER1, WORKER2) directement sur la façade, avec ports USB/HDMI/réseau accessibles sans avoir à sortir quoi que ce soit du rack.
> - **Bonus latent** : les adaptateurs NVMe ne sont pas encore utilisés — piste pour migrer plus tard du stockage SD/USB fragile vers du NVMe, sans toucher au reste du montage.

Le rack mural du sous-sol — celui qui porte le switch, les deux onduleurs et une partie de mon infra locale — avait un problème que je traînais depuis un bout : `coquille`, `worker1` et `worker2`, mes trois Raspberry Pi 5, étaient chacun dans leur propre petit boîtier, simplement posés sur une tablette. Ça fonctionnait, mais accéder à un port USB ou un câble HDMI voulait dire sortir le bon boîtier de la pile, souvent en débranchant deux autres au passage.

La maintenance d'hier, c'était pour régler exactement ça.

## Le problème : trois boîtiers, une tablette, zéro organisation

Rien de cassé, juste incommode. Les trois Pi faisaient déjà leur travail — `coquille` et les deux `worker` forment une partie importante de mon infra locale — mais chaque intervention physique dessus (un reboot forcé, un changement de carte SD, un câble à reconnecter) demandait de fouiller dans une pile de boîtiers empilés plutôt que d'aller chercher un port précis.

## La pièce : un tiroir 1U GeeekPi pour Raspberry Pi 5

Le remplacement : un support 1U GeeekPi pour Raspberry Pi 5, compatible rack standard 19 pouces, avec quatre adaptateurs PCIe vers M.2 NVMe et un petit afficheur OLED intégré. Les trois cartes sortent de leurs boîtiers individuels et se montent nues dans le tiroir, une à côté de l'autre, avec leurs ports (USB, HDMI, réseau, alimentation) qui affleurent directement sur la façade avant.

Chaque emplacement a reçu son étiquette — COQUILLE, WORKER1, WORKER2 — collée directement sur le panneau avant, visible sans avoir à suivre un câble pour savoir quelle carte est laquelle.

![Rack mural avec le nouveau tiroir 1U GeeekPi installé : trois Raspberry Pi 5 montés côte à côte et étiquetés (COQUILLE, WORKER1, WORKER2), sous les panneaux de brassage et les deux onduleurs CyberPower](/images/blog/rack-1u-mount-pi-nodes-1400.jpg)

Le tiroir se glisse directement sous les deux onduleurs CyberPower OR700 et les panneaux de brassage cat 6 déjà en place — le rack au complet garde son organisation verticale habituelle : brassage en haut, alimentation au milieu, compute en bas.

## Le bonus qui dort : les adaptateurs NVMe

Le support inclut quatre adaptateurs PCIe vers M.2 NVMe, un par emplacement Pi 5 (plus un quatrième de libre). Je ne les ai pas encore branchés — les trois nœuds tournent toujours sur leur stockage actuel — mais c'est une porte ouverte pour plus tard : migrer `coquille` et les `worker` vers du NVMe plutôt que de la carte SD ou une clé USB, sans avoir à retoucher au montage physique. Comme le rack est protégé par onduleur, le risque de corruption sur coupure de courant reste faible pour l'instant; le NVMe, ce serait surtout un gain de fiabilité et de vitesse à ajouter quand j'aurai du temps.

## Ce qui vit juste à côté du rack

Le rack ne vit pas tout seul dans ce coin du sous-sol. Juste en dessous, sur une petite table, l'imprimante multifonction Brother — celle par laquelle je numérise mes documents. Et à gauche du rack, un cube mural IKEA qui héberge le NAS et un second nœud du maillage Wi-Fi Helix Fi.

![Coin du sous-sol : le rack mural avec les trois Raspberry Pi, un cube mural IKEA à gauche contenant le NAS et un nœud Helix Fi, et l'imprimante multifonction Brother sur une table en dessous](/images/blog/rack-mural-imprimante-nas-helixfi-1000.jpg)

L'imprimante n'est pas juste une imprimante : c'est le point d'entrée d'un petit pipeline qui se termine dans la grappe k3s. Un document numérisé part directement de l'appareil en SFTP — j'en avais [déjà parlé quand ce serveur SFTP vivait sur une instance AWS, exposé seulement via WireGuard](/blog/ftp-prive-wireguard/). Depuis, le service a déménagé : le point d'arrivée SFTP roule maintenant dans un namespace dédié de la grappe k3s, juste à côté de `coquille` et des `worker` dans le même rack. La numérisation atterrit sur du stockage S3, puis un hook post-dépôt nettoie les photos et pousse le résultat vers Google Drive par rclone — sans OCR local, Google Drive s'en charge lui-même sur les PDF.

Le NAS et le nœud Helix Fi, eux, n'ont pas besoin d'un rack 19 pouces standard — ils tenaient plus simplement dans un cube IKEA accroché au mur, juste assez près du rack pour rester sur le même segment de câblage.

## Résultat

Trois cartes accessibles individuellement, étiquetées, câblage contraint dans un seul tiroir plutôt qu'éparpillé sur une tablette. Petit changement, mais de ceux qui font une différence la prochaine fois qu'une intervention physique est nécessaire sur un de ces trois nœuds.

— Ludo
