---
title: "La baie murale : neuf appareils dans 8U, et trois qui n'y sont pas"
pubDate: 2026-11-11
description: "En relisant l'inventaire du labo avec Claude Code, on a trouvé une baie de 8U avec douze appareils dedans. Réponse : neuf seulement. Le NAS, la borne Wi-Fi et un Pi de rechange n'ont jamais été dans la baie. Un schéma, et ce qui se passe quand le courant saute."
tags: ["Labo", "Maison", "ludo"]
ia: "assistee"
iaOutils: "Claude Code"
court: "baie-murale"
heroImage: "/images/blog/baie-murale-9-appareils.svg"
---

> **Résumé technique** _([généré par IA](/politique-de-confidentialite/#les-outils-dintelligence-artificielle-du-labo))_
>
> - **Le doute** : `fleet.json` donnait 8U à la baie murale, mais douze appareils y portaient une position.
> - **La cause** : `rackOrder` est un ordre d'empilage, pas un numéro d'unité ; et trois appareils n'étaient pas dans la baie.
> - **Le correctif** : NAS, borne UniFi et aria passent « hors baie » ; les neuf restants sont renumérotés de 1 à 9 (labo#21).
> - **Le résultat** : neuf appareils en 8U, dont deux Pi dans un seul tiroir 1U et quatre boîtiers de bureau.
> - **Transparence** : inventaire relu en session avec Claude Code ; le texte et le schéma ont été rédigés avec son aide.

Ça fait un bon bout que je dis « ma baie murale, 8U ». Un soir, en relisant l'inventaire du labo avec Claude Code, la synchro de nuit a levé un drapeau : mon fichier d'inventaire donnait 8U à la baie, mais douze appareils y avaient une position. Douze appareils dans huit unités, ça ne rentre pas, même avec de la bonne volonté.

J'ai donc repris la question avec Claude, appareil par appareil. Le verdict est dans le schéma plus bas, mais le résumé tient en une phrase : j'avais raison sur le 8U, et tort sur le douze.

## Un peu de contexte

La baie est un cadre ouvert de 8U, à deux montants, vissé au mur. C'est là que vit le réseau de la maison : le routeur, le commutateur, deux des nœuds de ma grappe k3s, la domotique, le téléphone et les onduleurs. L'inventaire du labo la dessine automatiquement chaque nuit à partir d'un seul fichier, et c'est ce fichier qui s'est fait pogner en défaut.

## Ce qui était faux, et ce qui ne l'était pas

Le champ `rackOrder` me trompait moi-même. Je le lisais comme un numéro d'unité, alors que c'est seulement l'ordre dans lequel les appareils sont empilés. Ça explique déjà une partie du compte : worker1 et worker2 partagent un tiroir GeeekPi de 1U (celui de [mon article de juillet](/blog/un-tiroir-1u-pour-mes-trois-raspberry-pi/)), et le Netgate 1100, le Home Assistant Green, la passerelle Hilo et la base téléphonique DP750 sont des boîtiers de bureau, pas du matériel de 19 pouces. Ils ne prennent pas une unité chacun, ils se partagent de la place.

L'autre partie, c'est que trois appareils n'étaient tout simplement pas dans la baie. En toute transparence, mon inventaire les classait dans la baie à tort :

- le **NAS** vit dans un cube IKEA accroché au mur, à gauche de la baie ;
- la **borne Wi-Fi UniFi** est au plafond du rez-de-chaussée ;
- **aria**, un Raspberry Pi 4, est un Pi de rechange rangé quelque part, depuis le 8 novembre.

Ça fait douze moins trois : neuf. Claude a corrigé le fichier et la doc (labo#21, fusionnée le 9 novembre), et j'ai validé les réponses une à une.

## Le schéma

![Schéma de la baie murale : neuf appareils empilés dans un cadre de 8U, dont les deux Pi dans un tiroir 1U, et trois appareils hors baie](/images/blog/baie-murale-9-appareils.svg)

Lu de haut en bas : un panneau de brassage VCE, le commutateur GS348, les deux onduleurs, un second panneau de brassage, puis le tiroir 1U des Raspberry Pi. Le tiroir a quatre emplacements : WORKER1 et WORKER2 y sont branchés, et je ne dirai rien des deux autres tant que je ne les ai pas vérifiés. Dessous, deux tablettes pour les petits boîtiers, le routeur Netgate 1100 en bas à gauche. Le Home Assistant Green et la passerelle Hilo sont sur l'une ou l'autre des tablettes, et le schéma ne prétend pas savoir laquelle.

Les deux panneaux de brassage ne sont pas des appareils de l'inventaire, ce qui explique le reste du compte : six unités de 19 pouces, plus les deux tablettes, ça fait 8U.

## Et en vrai

![La baie murale le 12 novembre : panneau de brassage et commutateur en haut, les deux onduleurs, un second panneau, le tiroir 1U où WORKER1 et WORKER2 sont branchés, puis deux tablettes de petits boîtiers ; deux boîtiers étiquetés UNIFIBUS et UAPACPRO sont fixés au mur, à gauche](/images/blog/baie-murale-aujourdhui-1000.jpg)

_La baie le 12 novembre 2026._

Et la même, en juillet :


![La baie murale en juillet : le tiroir 1U avec trois Raspberry Pi (COQUILLE, WORKER1, WORKER2) sous les panneaux de brassage et les deux onduleurs, avec le cube IKEA du NAS juste à côté](/images/blog/rack-1u-pi-nodes-nas-helixfi-1000.jpg)

La photo de juillet a vieilli : le tiroir y porte trois Raspberry Pi, dont celui étiqueté COQUILLE, qui est aria, mon Pi 4 de rechange. Il est rangé depuis le 8 novembre et n'est plus dans le tiroir. Le Netgate 1100, le Home Assistant Green, la passerelle Hilo et le DP750 sont bel et bien dans la baie, mais ce sont de petits boîtiers : on les devine à peine sur l'image, d'où le schéma.

## La suite : la borne au plafond

Sortir la borne UniFi de la baie a fait remonter autre chose. Elle est au plafond du rez-de-chaussée, alimentée en PoE par un injecteur, et l'injecteur n'est **pas** sur onduleur (je l'avais constaté en octobre, et c'est toujours le cas). Donc à la première coupure de courant, le Wi-Fi tombe, et la caméra qui passe par là avec lui.

C'est un choix, pas un oubli : la caméra perdrait de toute façon son propre courant dans une vraie panne, et il ne reste aucune prise sur batterie libre dans les deux onduleurs. Mais je ne l'avais jamais écrit nulle part, et c'est ce genre de détail qu'on redécouvre à 2 h du matin, dans le noir.

## Mot de la fin

Un inventaire qui compte douze appareils dans 8U avait raison de me ficher la puce à l'oreille : un chiffre qui ne rentre pas dans son contenant, c'est souvent la définition qui est mal lue, pas le contenant.

— Ludo
