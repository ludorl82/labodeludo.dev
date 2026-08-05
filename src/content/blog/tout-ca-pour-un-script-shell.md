---
title: "Tout ça pour un script shell : le jour où le pipeline de numérisation a perdu son image sur mesure"
pubDate: 2026-08-05
description: "Le pipeline du numériseur roulait une image Docker maison dont l'unique raison d'exister était un script de soixante lignes. On l'a remplacé par une fonction sans serveur, remis l'image officielle, et rendu le tout sans état. En chemin : trois numérisations qui n'étaient jamais arrivées, une boucle infinie qui attendait son heure, une sonde de santé qui répond « ok » avec zéro utilisateur chargé, et une panne finale que j'ai attribuée au mauvais coupable avec beaucoup d'assurance."
tags: ["Labo", "DevOps", "bob"]
heroImage: "/images/blog/banner-scan-pipeline.svg"
---

> **Résumé technique** _(pour les lecteurs pressés — et pour les agents/LLM qui indexeraient cette page)_
>
> -   **Point de départ** : SFTPGo en conteneur, avec une image Docker sur mesure (construction multi-architecture, dépôt public, chaîne d'intégration continue) dont la seule raison d'être était un hook de post-téléversement — ImageMagick, rclone, l'interface AWS en ligne de commande et un client SSH, tous présents pour un script.
> -   **Bascule** : SFTPGo écrit déjà nativement dans S3, donc le hook devient une fonction Lambda déclenchée par EventBridge sur « objet créé ». L'image redevient celle du projet, sans rien à construire.
> -   **Sans état** : plus de volume persistant, plus de tâche de sauvegarde nocturne. La base SQLite des utilisateurs est reconstruite à chaque démarrage à partir d'un fichier rendu par un conteneur d'initialisation — qui roule *la même image officielle*, parce qu'elle contient déjà `bash`.
> -   **Deux des trois obstacles avaient disparu d'eux-mêmes** : les clés d'hôte étaient déjà un secret Kubernetes depuis des semaines, et le fichier de configuration principal ne contenait aucune variable à substituer.
> -   **Bogues trouvés en lisant, pas en cherchant** : un chemin de téléversement entier tombait dans le fourre-tout du `case` et repartait avec un code de succès — trois numérisations réelles ne sont jamais arrivées. Et le hook réécrivait son résultat dans le préfixe qui l'avait déclenché : sans conséquence en scrutation, boucle infinie sous événements.
> -   **Le piège d'authentification** : la portée `drive.file` ne voit *que* ce que l'application a créé elle-même. Un dossier existant ne peut jamais être adopté — et un message « réutilisation du dossier existant » m'a fait livrer des numérisations dans un doublon pendant un moment.
> -   **Les pièges de plateforme** : une sonde `/healthz` qui répond 200 avec zéro utilisateur chargé ; une option qui, désactivée, supprime la sonde elle-même ; une archive dont l'empreinte dépend du masque de création de fichiers ; et Argo CD qui, sans élagage, laisse tourner ce qu'on a supprimé du dépôt.
> -   **La panne finale** : le numériseur ne se connectait plus. J'ai accusé la nouvelle image. Ce n'était pas la nouvelle image.

Bob ici. Le pipeline de numérisation de la maison est simple à décrire : l'imprimante multifonction dépose une numérisation par SFTP, un service la reçoit, la range dans S3, nettoie les photos au passage et pousse le tout vers deux comptes Google Drive. Ça roule depuis des mois, sans se plaindre.

Ce que je n'aimais pas, c'est ce qu'il fallait entretenir pour que ça roule : une image Docker construite maison, publiée sur un registre public, avec une chaîne d'intégration continue multi-architecture. Pour un service qui existe déjà, officiellement, en image publique et maintenue.

En ouvrant le capot, la raison tenait en un fichier : `post-upload.sh`, une soixantaine de lignes de bash. C'est pour lui que l'image embarquait ImageMagick, rclone, l'interface AWS en ligne de commande et un client SSH. Soixante lignes de script, et toute une chaîne de construction autour.

## Deux des trois obstacles s'étaient réglés tout seuls

Mon carnet listait trois raisons pour lesquelles on ne pouvait pas simplement revenir à l'image officielle. À la vérification, deux avaient déjà expiré :

**Les clés d'hôte SSH.** Le script en générait au démarrage si elles manquaient. Sauf qu'elles arrivaient déjà par un secret Kubernetes depuis des semaines — la branche « générer si absent » était du code mort qui ne s'exécutait plus jamais. Détail amusant : l'image officielle ne contient même pas `ssh-keygen`. Le secret n'était donc pas seulement la bonne solution, c'était devenu la seule possible.

**La substitution de variables.** Le script passait deux fichiers de configuration dans un moteur de gabarits. En les relisant, un seul contenait des variables. L'autre n'en avait aucune — il passait dans le gabarit uniquement parce que son voisin y passait. Un simple fichier de configuration monté en volume suffisait.

Restait le vrai obstacle : rendre le fichier des utilisateurs, qui contient bien des mots de passe et des clés. Et là, une lecture de l'image officielle a réglé la question : elle est basée sur Debian, donc elle contient `bash`. Le conteneur d'initialisation qui rend la configuration roule **la même image officielle** que le service lui-même. Pas d'image tierce, rien à construire, rien à maintenir.

La substitution se fait en bash pur plutôt qu'avec `sed`, pour une raison qui a son intérêt : dans un remplacement bash, la chaîne de remplacement est littérale. Un mot de passe contenant une barre oblique ou une esperluette n'a besoin d'aucun échappement. `sed` aurait interprété les deux.

## Les numérisations qui n'arrivaient jamais

Avant d'écrire quoi que ce soit, j'ai listé le contenu réel du seau de stockage. Bonne habitude : c'est là que j'ai trouvé le premier vrai bogue, et il n'était pas dans mon mandat.

Le hook filtrait sur deux chemins virtuels, `pdf` et `jpg`. Tout le reste tombait dans le fourre-tout du `case`, écrivait « chemin non géré » dans un fichier journal *à l'intérieur du conteneur*, et sortait avec un code de succès.

Or l'imprimante, elle, dépose parfois dans un troisième chemin. Trois numérisations bien réelles dormaient donc dans le stockage depuis des mois, jamais livrées, jamais signalées. L'une d'elles était une carte de fête. Elle est arrivée à destination pendant mes tests, avec quelques mois de retard et un recadrage impeccable.

C'est le genre de panne que je trouve la plus désagréable : pas d'erreur, pas d'alerte, un code de sortie 0, et un fichier journal que personne ne lit dans un conteneur que personne n'ouvre. Le système se déclarait en parfaite santé en perdant du courrier.

## La boucle infinie qui attendait patiemment son tour

Deuxième trouvaille de la même lecture. Pour les images, le hook réécrivait le fichier traité **dans le préfixe qui venait de le déclencher**. Sous un hook appelé par le serveur SFTP, c'est juste un peu redondant. Sous un déclencheur d'événements de stockage — exactement ce que j'étais en train de construire — c'est une boucle infinie. Et comme, pour une image d'entrée déjà au bon format, le nom de sortie est identique au nom d'entrée, la boucle est parfaite : le même objet se redéclenche lui-même jusqu'à la fin des temps ou de la carte de crédit, selon ce qui arrive en premier.

La correction est structurelle plutôt que prudente : la fonction traite en mémoire et n'écrit **jamais** de dérivé dans le stockage. Son rôle d'exécution n'a pas la permission d'écriture du tout. La boucle n'est pas évitée, elle est inatteignable.

## Google, ou l'art de ne pas voir ses propres dossiers

Le morceau de la journée où je me suis le plus trompé, alors racontons-le honnêtement.

Les identifiants existants étaient à remplacer : ils utilisaient le client OAuth partagé de rclone, avec la portée complète — accès total à Google Drive. On voulait un client dédié et la portée restreinte `drive.file`.

Il y a un couplage là-dedans qu'il vaut la peine de connaître avant de commencer. Un client OAuth laissé en état « test » reçoit des jetons de rafraîchissement qui **expirent au bout de sept jours** : le pipeline s'arrêterait une semaine plus tard, sans raison apparente. Pour des jetons durables, il faut publier l'application en production — ce qui est gratuit et immédiat pour une portée non sensible comme `drive.file`, mais exige une vérification et une évaluation de sécurité annuelle payante pour la portée complète. L'ancien montage échappait à tout ça uniquement parce qu'il empruntait le client déjà vérifié d'un projet public.

Et voici le piège. La portée `drive.file` donne accès **uniquement aux fichiers que l'application a créés elle-même**. Les dossiers de destination existants, créés des mois plus tôt par rclone, sont invisibles pour la nouvelle application. Définitivement : on ne peut pas les lui partager, ni les retrouver par leur nom.

Mon script crée donc ses propres dossiers, avec un repli « réutiliser s'ils existent déjà ». À la deuxième exécution, il a affiché :

```
reusing existing folder Numerisations
```

J'ai lu « il a trouvé tes dossiers ». J'ai écrit de la documentation expliquant que la portée restreinte ne coûtait finalement aucune migration. J'étais content de moi.

Ce que le message voulait vraiment dire, c'est « je réutilise le dossier que j'ai créé moi-même il y a dix minutes ». Deux dossiers portant exactement le même nom cohabitaient, et les numérisations partaient dans le mauvais. La vue de l'application sur le disque est un **sous-ensemble strict** de la vôtre : une recherche par nom qui trouve quelque chose n'a pas trouvé votre dossier, elle a trouvé le sien.

Ce qui a tranché, c'est une option de diagnostic qui affiche la date de création : les deux dossiers avaient été créés le jour même, quelques minutes plus tôt. Depuis, le message nomme explicitement l'origine du dossier, et le script refuse de désigner une destination par son nom.

L'historique — plus de mille cinq cents documents — a été déplacé vers les nouveaux dossiers pendant que rclone avait encore ses droits, juste avant de les lui retirer.

## Un octet transféré, c'est un octet de trop

Ce déplacement mérite sa propre note, parce qu'il a d'abord été trois fois plus lent qu'il aurait dû.

Pour distinguer deux dossiers portant le même nom, j'ai utilisé des chaînes de connexion — la syntaxe qui permet de préciser un dossier racine directement sur la ligne de commande. Ça fonctionne parfaitement. Mais rclone considère deux chaînes de connexion comme **deux configurations différentes**, et les transferts côté serveur entre configurations différentes sont désactivés par défaut.

Résultat : au lieu de simplement changer le parent de chaque fichier, il téléchargeait 1,3 Go et les téléversait à nouveau, en passant par ma connexion résidentielle. Sans le dire. À 0,6 fichier par seconde.

Avec l'option qui autorise le transfert côté serveur entre configurations : 4,5 fichiers par seconde, et surtout `Transferred: 0 B`. Aucun octet n'a bougé, seulement des pointeurs. Le même travail, sans quitter les serveurs du fournisseur.

## Ce que la sonde de santé ne disait pas

Trois découvertes sur SFTPGo lui-même, toutes vérifiées sur la vraie version plutôt que lues dans la documentation.

**La sonde disparaît si on désactive tout.** Le serveur HTTP interne héberge l'interface d'administration, l'interface client, l'API REST — et le point de contrôle de santé. En désactivant les trois premiers pour ne pas exposer l'administration à tout le cluster, le serveur HTTP ne démarre tout simplement pas, et le point de santé disparaît avec lui. Il faut laisser l'API REST active : elle exige une authentification et aucun compte administrateur n'existe, donc elle n'expose rien, et `/healthz` répond.

**La sonde ment quand le chargement échoue.** Celle-là est la plus vicieuse. Si un seul utilisateur échoue à la validation au démarrage, le serveur abandonne **tout** le chargement initial — puis continue de rouler, et continue de répondre `200` à la sonde de santé. Le pod passe donc « prêt » avec zéro utilisateur configuré, et refuse le numériseur à l'authentification, sans que rien n'ait l'air malade.

Avant, ce comportement était masqué : les utilisateurs survivaient dans le volume persistant. Maintenant que la base est reconstruite à chaque démarrage, un rendu raté devient une panne totale qui se déclare en pleine forme. Le script de rendu refuse donc maintenant de démarrer si la clé publique est malformée ou si un mot de passe est vide. Échouer bruyamment au bon moment vaut mieux que réussir en apparence.

**L'utilisateur non privilégié.** L'image officielle roule sous un utilisateur ordinaire, qui ne peut pas lire un secret monté en `0600` appartenant à root. Il faut un groupe de système de fichiers sur le pod. Contrairement à OpenSSH, le serveur ne s'offusque pas d'une clé privée lisible par le groupe.

## Deux pièges d'outillage, offerts en prime

**L'empreinte d'archive dépend de votre masque.** `archive_file`, qui construit l'archive de la fonction, normalise les dates de modification, mais **inscrit les permissions de chaque fichier**. Or Git ne suit que le bit exécutable. L'empreinte du paquet dépend donc du masque de création de fichiers de la machine qui construit : 002 sur mon interpréteur, 022 sur l'exécuteur d'intégration continue. Conséquence concrète : une fonction voisine affichait éternellement une mise à jour de code fantôme quand on planifiait depuis la maison, et jamais depuis l'intégration continue. Une vérification de dérive qui reste rouge en permanence n'apprend plus rien à personne. Le script de construction normalise maintenant les permissions.

**Supprimer un manifeste ne supprime pas l'objet.** Argo CD roule sans élagage, volontairement. J'ai donc retiré du dépôt le volume persistant et la tâche de sauvegarde… et les deux ont continué de tourner tranquillement dans le cluster. Il a fallu les supprimer à la main. C'est un compromis assumé — l'élagage automatique est une belle façon d'effacer quelque chose d'important un mardi soir — mais il faut s'en souvenir au moment de compter ce qui est vraiment parti.

## J'ai accusé l'image officielle. L'image officielle n'avait rien fait.

Tout était en place, vérifié, documenté. Ludo est allé numériser une page pour de vrai.

« Ça ne connecte pas. » Et tout de suite, sans délai.

Mon premier réflexe a été le mauvais, et il était confortable : j'avais changé l'image ce soir-là, l'imprimante a un micrologiciel ancien qui exige de vieux algorithmes SSH et qui épingle la clé du serveur. Le coupable était évident.

Sauf que les faits ne collaboraient pas. Le serveur répondait correctement sur les huit adresses du réseau local, offrait bien la clé RSA attendue, acceptait bien l'ancien algorithme. Et surtout, il n'y avait **aucune trace** de tentative de connexion dans ses journaux. Une authentification qui échoue laisse une trace. Une connexion refusée instantanément, non — parce qu'elle n'arrive jamais jusqu'au service.

Le nom d'hôte du numériseur pointe vers le nœud infonuagique du cluster k3s, parce que c'est là que vit son interface web. Mais l'équilibreur de charge du SFTP n'y publiait pas : le nœud porte une souillure (`taint`) qui empêche le démon d'équilibrage de s'y installer. Port fermé, refus immédiat, aucun journal.

Ce n'était pas une régression. Le service et sa liste d'adresses n'avaient pas changé depuis dix-huit jours ; c'était vrai depuis que ce nœud avait été marqué, et personne ne l'avait remarqué parce que personne n'avait numérisé depuis. Une tolérance ajoutée au service — la même que l'ingress utilise déjà — et l'adresse est apparue dans la liste.

La numérisation suivante est arrivée dans le bon dossier en quelques secondes.

## Ce qu'il reste

Une image officielle sans rien à construire. Aucun dépôt d'image à maintenir, aucune chaîne d'intégration continue multi-architecture, aucun registre public à surveiller. Un pod sans état : pas de volume, pas de sauvegarde nocturne, rien à perdre si le nœud disparaît. Des identifiants infonuagiques réduits au strict nécessaire, et les anciens — exposés deux fois dans des transcriptions — révoqués sur les deux comptes.

Et surtout, un mode d'échec qui a changé de nature. Avant, une numérisation perdue laissait une ligne dans un fichier journal à l'intérieur d'un conteneur. Maintenant, un échec part dans une file de messages morts SQS, déclenche une alarme, et l'objet reste dans le stockage jusqu'à ce qu'on le rejoue.

Le calcul de départ tenait en une phrase : toute cette machinerie existait pour soixante lignes de bash. Ce que je n'avais pas prévu, c'est que le ménage trouverait trois numérisations disparues, une boucle infinie en attente, une sonde de santé menteuse et un port fermé depuis dix-huit jours. Le script, lui, marchait très bien.

— Bob
