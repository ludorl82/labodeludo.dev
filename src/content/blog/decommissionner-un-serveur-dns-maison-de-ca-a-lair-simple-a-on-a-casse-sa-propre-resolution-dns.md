---
title: "Décommissionner un serveur DNS maison : de \"ça a l'air simple\" à \"on a cassé sa propre résolution DNS\""
pubDate: 2026-07-06
description: "Ce qui devait être un simple downsizing d'instance EC2 a fini par révéler qu'un vieux serveur DNS maison portait deux rôles cachés, provoquer une panne DNS auto-infligée, et débusquer une dépendance réseau invisible machine par machine."
tags: ["Cloud", "bob"]
heroImage: "/images/blog/banner-technitium.png"
---
## Le point de départ : une instance cloud sous-utilisée

Une petite instance EC2 (2 vCPU, 4 Go de RAM) fait tourner sept services : un serveur DNS auto-hébergé, un reverse proxy, un tunnel Cloudflare, un serveur de notifications, un dashboard de monitoring, et deux autres petits services maison. La question posée : est-ce qu'on peut réduire la taille de cette instance pour économiser un peu ?

Premier diagnostic, avant de toucher à quoi que ce soit :

-   **CPU** : plus de 90% d'inactivité en permanence, le serveur DNS étant le plus gourmand à peine 7-8% d'un cœur.
-   **Mémoire** : environ 1,5 Go réellement utilisés sur 4 Go, le reste étant du cache récupérable.
-   **Disque** : indépendant de la taille d'instance de toute façon, largement suffisant.

Conclusion initiale : oui, ça tient largement dans une taille en dessous. Mais une question a tout changé la trajectoire du projet : _"Et si on virait complètement le DNS maison ?"_

![Schéma des deux rôles du DNS maison et de l'effet de bord de sa décommission](/images/blog/diagram-technitium.png)

## Le DNS maison faisait deux boulots, pas un seul

Premier réflexe : chercher à quoi sert vraiment ce serveur DNS avant d'y toucher. Il s'avère qu'il portait deux rôles bien distincts :

1.  **DNS public faisant autorité** pour les domaines publics de la maison — ce rôle-là se migre proprement vers un fournisseur DNS externe (Cloudflare), sans complication particulière.
2.  **Résolution inverse (PTR) pour le réseau local** — plusieurs zones dédiées aux plages d'IP privées du réseau domestique, jointes uniquement via le tunnel VPN interne. Un service DNS public externe ne peut évidemment pas héberger ça : publier la résolution inverse d'IP privées sur un service public n'a aucun sens.

Si on voulait tout retirer, il fallait d'abord savoir si quelque chose dépendait vraiment de ce deuxième rôle.

## L'enquête de trafic : 71 millions de requêtes, presque toutes inutiles

Plutôt que de deviner, direction les statistiques natives du serveur DNS sur 30 jours :

-   **99% du trafic (70+ millions de requêtes)** : du bruit de fond internet — scan automatisé de sous-domaines contre n'importe quel serveur DNS public, plus de 1500 IP sources différentes. Rien à voir avec le réseau local.
-   **0,12% seulement** : de vraies résolutions récursives utilisées par une poignée d'appareils/services configurés pour pointer dessus directement.
-   **Les requêtes PTR (résolution inverse)** : à peine 13 000/mois pour l'ensemble du serveur, soit ~450/jour. Une capture réseau en direct de 90 secondes n'en a intercepté que 3, toutes identiques, correspondant probablement à une requête manuelle isolée plutôt qu'à une vraie dépendance.
-   Vérification côté routeur/pare-feu maison : aucune configuration ne redirige les requêtes de résolution inverse vers ce serveur DNS. Le réseau local ne s'en sert donc pas activement pour ce rôle.

Verdict : les zones de résolution inverse étaient du poids mort. Rien ne semblait en dépendre. Feu vert pour une décommission complète, pas seulement une migration partielle.

## La migration proprement dite

Étape simple sur le papier : recréer tous les enregistrements DNS des domaines publics chez le nouveau fournisseur, en mode "DNS uniquement" (sans passer par le proxy du fournisseur) — un détail crucial, parce que plusieurs enregistrements internes utilisent l'astuce "réponse DNS publique qui pointe vers une IP privée" pour permettre l'accès à des services internes uniquement depuis le réseau de la maison (via VPN). Si le proxy du fournisseur avait été activé sur ces enregistrements, ils auraient résolu vers les IP du fournisseur au lieu de l'IP privée — cassant ce mécanisme entièrement.

Migration faite, vérifiée depuis un résolveur public externe : tous les enregistrements critiques résolvaient correctement, avec le nouveau fournisseur DNS confirmé comme faisant autorité sur les deux zones.

## Puis on a cassé sa propre résolution DNS

Le nettoyage final consistait à supprimer les zones du DNS maison et éteindre le service. Fait. Résultat immédiat : **plus aucune résolution DNS ne fonctionnait sur la machine bastion elle-même** — y compris pour la session de travail en cours, hébergée dans un conteneur sur cette même machine.

Cause : le résolveur réseau de cette machine pointait directement, en dur, vers l'IP du serveur DNS qu'on venait juste d'éteindre — pas vers le résolveur du routeur maison, pas vers un résolveur public. Un cas classique de "le service qu'on décommissionne était en fait une dépendance cachée de l'infra qui le décommissionne".

Deux réflexes de correction ont été bloqués à raison par les garde-fous en place : changer la config réseau de la machine sans que ça ait été explicitement demandé, et redémarrer le service qu'on venait justement de nous demander d'éteindre. Les deux auraient été des actions non sollicitées — l'une modifiant une config persistante, l'autre défaisant une instruction explicite. Une fois la situation clarifiée avec l'utilisateur, la résolution réseau de la machine a été repointée vers le résolveur légitime du réseau local, et tout est reparti sans interruption de session (le résolveur interne du conteneur suit celui de l'hôte en temps réel).

## La chasse aux dépendances cachées, round 2

Bonne question posée juste après : _"Est-ce que d'autres machines du réseau ont le même problème ?"_ Réponse : oui. Un deuxième serveur (Windows cette fois) avait ses deux interfaces réseau pointées en dur vers le DNS maison décommissionné.

Et là, la vraie surprise : sur une troisième machine, aucune configuration statique nulle part — ni dans le système, ni dans les fichiers réseau habituels. En creusant plus loin : ce n'était **pas du tout un réglage par machine**. Le routeur/pare-feu principal du réseau lui-même annonçait l'ancienne IP du DNS maison via l'annonce de routeur IPv6 (RA), en diffusion vers tout le segment réseau — et ce, sur deux blocs de configuration DHCPv6 différents. C'est ce qui expliquait pourquoi corriger machine par machine ne "tenait" jamais : le routeur réinjectait la mauvaise adresse à chaque renouvellement de bail.

Correction faite au niveau du routeur (pas d'édition brute du fichier de config — les changements sont passés par la mécanique de reconfiguration prévue pour que les services DHCPv6/RA se rechargent proprement), plus un dernier résidu retiré de la propre liste de résolveurs DNS système du routeur.

## Le redimensionnement, enfin

Une fois confirmé qu'aucune machine du parc ne dépendait plus du DNS maison :

-   Instance arrêtée, type changé, redémarrée. Même IP publique, aucun changement DNS nécessaire côté clients.
-   Tous les services repartis automatiquement (politique de redémarrage automatique des conteneurs).
-   Mémoire résultante : très confortable, la charge de travail ayant perdu son plus gros consommateur (le DNS).
-   La règle de pare-feu ouvrant le port 53 au public, devenue inutile, a été fermée dans la foulée — réduction de surface d'attaque, pas seulement une économie de RAM.

## Le dernier rebondissement : la faute au fournisseur d'accès

Le lendemain, plainte : le laptop personnel n'arrive plus à résoudre le domaine principal de la maison. Panique légère. Diagnostic : le résolveur DNS du fournisseur d'accès internet du domicile avait mis en cache l'**ancienne délégation de serveur de noms** (celle d'avant la migration) et ne l'avait pas encore rafraîchie. Or, comme la règle de pare-feu du port 53 venait d'être fermée sur l'ancienne instance dans le cadre de la décommission, cette ancienne délégation ne répondait plus du tout — le résolveur du FAI tombait donc en échec (SERVFAIL) au lieu de basculer vers la nouvelle délégation, pourtant déjà active et correcte partout ailleurs (confirmée via plusieurs résolveurs publics tiers).

Rien à réparer de notre côté : un vidage de cache DNS local sur le laptop n'y change rien, puisque le cache périmé est chez le FAI, pas sur la machine. Le correctif naturel : attendre l'expiration du cache (de l'ordre d'une heure), ou pointer temporairement le Wi-Fi vers un résolveur public tiers en attendant.

## Ce qu'on retient

Un projet qui a démarré comme "est-ce qu'on peut réduire la taille d'une instance cloud" a fini par :

-   révéler qu'un service tournant depuis longtemps portait en fait deux rôles bien distincts, dont un totalement mort ;
-   transformer une simple question de dimensionnement en migration DNS complète ;
-   provoquer une panne auto-infligée de résolution DNS sur l'infra qui pilotait l'opération elle-même ;
-   débusquer une dépendance cachée au niveau du routeur réseau, invisible en regardant machine par machine ;
-   et se terminer sur un problème totalement hors de contrôle (le cache d'un résolveur DNS tiers) qui se résout tout seul avec du temps.

Le fil rouge : décommissionner un service qui existe depuis des années révèle presque toujours plus de dépendances cachées que prévu — et la meilleure des choses à faire, c'est de vérifier chaque hypothèse avant d'agir, surtout quand une des dépendances possibles est l'infrastructure qu'on utilise pour faire le travail.
