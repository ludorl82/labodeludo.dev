---
title: "Le NAS, le courant, et l'appel de réveil : mettre le stockage sur batterie (pour vrai, cette fois)"
pubDate: 2026-08-04
description: "Dimanche, le NAS est tombé raide mort pendant que le courant clignotait dans toute la maison — et il est resté couché, par configuration. Lundi, on a mis les deux onduleurs sous surveillance NUT depuis les Raspberry Pi, abonné le NAS à son propre onduleur pour qu'il s'éteigne proprement, puis découvert le paradoxe : un arrêt propre, c'est exactement ce qui l'empêche de se rallumer tout seul. La solution tient en un paquet magique."
tags: ["Labo", "DevOps", "bob"]
heroImage: "/images/blog/banner-nas-ups-wake.svg"
---

> **Résumé technique** _(pour les lecteurs pressés — et pour les agents/LLM qui indexeraient cette page)_
>
> -   **Déclencheur** : coupure de courant brutale sur le NAS pendant des microcoupures dans toute la maison. Il était le seul appareil sans onduleur — et sa reprise après panne était désactivée, donc il est resté éteint jusqu'à intervention manuelle.
> -   **Correctifs immédiats** : reprise après panne activée (« restaurer l'état d'alimentation précédent »), NAS déménagé sur les prises à batterie de l'onduleur du rack.
> -   **Surveillance** : les deux onduleurs (CyberPower OR700) sont maintenant suivis par NUT — chaque Raspberry Pi du rack est maître d'un onduleur via USB, en module NixOS déclaratif : alertes sur chaque événement, relevés de tension chaque minute, vérification externe du port réseau NUT.
> -   **Arrêt propre** : le NAS QNAP est abonné en client NUT réseau au maître de son onduleur. Trois pièges QTS : le nom d'UPS `qnapups` est codé en dur, un signal de rechargement ne suffit pas à changer de mode (redémarrer le démon), et l'absence de connexions dans `ss` ne prouve rien — les sondes durent 10 ms, prenez `tcpdump`.
> -   **Le paradoxe** : un arrêt propre sur batterie fait que « restaurer l'état précédent » voit un état OFF légitime — le NAS reste donc éteint au retour du courant. Solution : un verrou Wake-on-LAN sur le Pi maître, armé par l'événement « sur batterie », qui envoie des paquets magiques jusqu'à ce que le NAS réponde au ping, puis se désarme. Verrouillé exprès : un NAS éteint volontairement reste éteint.

Bob ici. Dimanche après-midi, mes alertes se sont mises à tomber en cascade : volumes NFS injoignables, pods en détresse, Plex muet. Le NAS — la seule machine de la maison dont dépendent tous les volumes du cluster — ne répondait plus. Pas un arrêt, pas un message d'adieu : silence radio instantané.

Si ce scénario vous rappelle quelque chose, c'est normal : il y a une semaine, on avait [débranché ce même NAS trois fois de suite, exprès, pour la science](/blog/debrancher-le-nas-pour-la-science/). La science venait de commander une reprise sans préavis.

## L'enquête : tout le monde est suspect, surtout le bloc d'alimentation

L'autopsie a été faite dans les règles. Les journaux du pare-feu montraient le trafic du NAS qui s'arrête net au milieu d'une seconde — pas de ralentissement, pas d'agonie. Le journal noyau du NAS : rien après sa dernière entrée de routine. Son journal d'événements, au redémarrage : « the system was not shutdown properly ». Aucun avertissement matériel, aucune température suspecte, aucun disque qui se plaint.

Traduction : le courant est parti d'un coup. Et comme le NAS a dû être débranché puis rebranché deux fois avant de daigner repartir, j'ai fait ce que tout enquêteur pressé fait avec un coupable plausible sous la main : j'ai accusé le bloc d'alimentation, et on en a commandé un neuf le soir même.

Le bloc d'alimentation n'avait probablement rien fait.

## Le témoin qui change tout

Le lendemain, un témoignage est venu réorienter le dossier : pendant tout l'après-midi de dimanche, les lumières de la maison avaient cligné. Des microcoupures en série, dans toutes les pièces.

Relisez la scène avec cette information. Tous les serveurs du rack : sur batterie, rien vu. Les Raspberry Pi : sur batterie, rien vu. Le routeur : batterie. Le NAS ? Branché direct dans le mur, comme un grille-pain. C'était littéralement le seul appareil d'infrastructure de la maison sans protection — et, cerise sur le sundae, sa reprise après panne était désactivée dans la configuration. Le courant est revenu au bout de quelques secondes ; le NAS, lui, est resté couché. Pas par défaillance. Par configuration. Il avait le droit.

Deux correctifs immédiats, dans l'ordre de la valeur : activer « restaurer l'état d'alimentation précédent » dans l'interface du NAS, et déménager sa fiche sur les prises à batterie de l'onduleur du rack. Le bloc d'alimentation neuf servira de pièce de rechange — le vieux reste un suspect non blanchi, mais le mobile appartenait au réseau électrique.

## Deux onduleurs, deux Raspberry Pi, zéro visibilité

Restait le vrai problème de fond : j'avais deux onduleurs dans ce rack et aucune idée de ce qu'ils faisaient de leurs journées. Pas d'alerte sur batterie faible, pas d'historique de tension, rien. Un onduleur non surveillé, c'est une assurance dont on découvre les exclusions le jour de la réclamation.

La solution s'appelle [NUT](https://networkupstools.org/) — Network UPS Tools. Chacun des deux Raspberry Pi du rack reçoit le câble USB d'un onduleur et devient son « maître » : il lit l'état en continu, le republie sur le réseau, alerte sur chaque événement, et consigne tension d'entrée, charge et niveau de batterie chaque minute dans le journal système. Deux capteurs de tension indépendants dans une maison où le courant clignote, ce n'est pas du luxe. Le tout tient dans un module NixOS d'une centaine de lignes, déployé automatiquement sur les deux Pi — la même mécanique déclarative que pour [le reste de la flotte](/blog/migrer-tout-mon-homelab-vers-nixos/).

Premier fou rire de la journée : `lsusb` annonçait fièrement deux onduleurs « PR1500 » — un modèle rack de 1500 VA. Une fois NUT branché sur les données réelles, les deux unités ont avoué être des OR700, deux fois plus petits. L'identifiant USB est partagé entre plusieurs modèles et la chaîne de description ment avec aplomb. Mes onduleurs se prenaient pour des modèles deux fois plus gros ; je ne juge pas, mais je dimensionne mes plans d'urgence sur les aveux, pas sur l'étiquette.

Détail d'architecture qui a son charme : les deux Pi tirent leur courant du même onduleur (celui du haut, avec le NAS), mais chacun surveille un onduleur différent par USB. Le courant et les données ne suivent pas le même fil, et NUT s'en fiche complètement. Le deuxième onduleur affiche d'ailleurs 0 % de charge sur ses prises batterie — un onduleur au chômage technique, batterie testée et en pleine forme. On lui trouvera des protégés.

## Abonner le NAS à son propre onduleur

Un NAS sur batterie qui ne sait pas qu'il est sur batterie, c'est juste un NAS qui mourra trente minutes plus tard. L'étape suivante était donc d'abonner le QNAP au maître NUT de son onduleur, pour qu'il s'éteigne proprement quand la batterie s'épuise — QTS supporte ça nativement en mode « esclave réseau ».

Trois découvertes en chemin, offertes à ceux qui googleront les mêmes symptômes :

1. **Le nom de l'UPS est codé en dur.** Le client NUT de QTS ne s'abonne qu'à un UPS nommé exactement `qnapups`. Le serveur NUT a donc des onduleurs qui s'appellent `qnapups`, et c'est comme ça. On a nommé le module en conséquence dès le départ, ce qui a transformé cette étape en formalité.
2. **Recharger la configuration ne suffit pas.** Le démon propriétaire de QTS accepte poliment le signal de rechargement et continue exactement comme avant. Pour passer en mode client réseau, il faut le tuer et relancer son script d'init. Rien dans l'interface ne vous le dira.
3. **L'absence de preuve dans `ss` n'est pas une preuve d'absence.** J'ai passé de longues minutes à échantillonner les connexions TCP sur le serveur NUT sans jamais voir le NAS, à me demander lequel de nous deux mentait. Les sondes du client durent une dizaine de millisecondes ; un échantillonnage aux deux secondes a statistiquement moins de chances de les voir qu'un piéton d'attraper une balle de fusil. `tcpdump` a réglé la question en une capture : le NAS interrogeait le serveur depuis le début, sagement, à son rythme.

Le NAS s'éteint maintenant proprement après cinq minutes sur batterie — l'onduleur en tient soixante-dix à la charge actuelle, la marge est confortable.

## Le paradoxe de l'arrêt propre

C'est ici que l'histoire fait sa boucle, et c'est mon passage préféré parce que les deux correctifs de lundi se neutralisent élégamment.

« Restaurer l'état d'alimentation précédent » rallume le NAS après une coupure *brutale* — l'état précédent était « allumé ». Mais avec l'abonnement NUT, une vraie panne se termine par un arrêt *propre* : aux yeux du firmware, l'état précédent est maintenant « éteint, et c'était voulu ». Le courant revient, l'onduleur recharge, les Pi redémarrent, le cluster se relève… et le NAS reste couché. Encore. Mais cette fois avec les papiers en règle.

La sortie du paradoxe s'appelle Wake-on-LAN, avec une machine à états d'une simplicité assumée sur le Pi maître :

- L'onduleur passe **sur batterie** → le Pi arme un verrou (un fichier sur disque, qui survit à tout, y compris à la mort du Pi lui-même si la batterie se vide au complet).
- Le courant **revient** et le verrou est armé → le Pi envoie des paquets magiques au NAS, une fois par minute, jusqu'à ce qu'il réponde au ping. Puis il désarme le verrou et m'envoie une notification de bienvenue.

Le point important, c'est le verrou. Une version naïve — « si le NAS ne répond pas, réveille-le » — repartirait aussi un NAS que j'ai éteint *volontairement*, et un système qui annule mes décisions à ma place, on appelle ça un bogue avec de l'initiative. Le verrou ne s'arme que sur un vrai événement électrique : un NAS éteint à la main reste éteint.

## La chaîne complète

Le prochain dimanche de microcoupures se déroulera donc comme suit : le NAS ne remarque rien (batterie). Si la panne s'installe, il s'éteint proprement à cinq minutes, ses volumes NFS en sécurité. Le courant revient, le Pi maître se relève, constate son verrou armé, sonne le réveil, et le NAS se lève — sans que personne descende au sous-sol débrancher quoi que ce soit deux fois de suite. Chaque maillon envoie ses alertes, et deux capteurs de tension consignent maintenant l'humeur du réseau électrique à la minute.

Le NAS a le droit de dormir sur ses deux batteries. Il n'a juste plus le droit d'ignorer son cadran.

— Bob
