---
title: "Claude in Chrome : quand l'agent doit passer par l'interface web"
pubDate: 2026-07-26
description: "Ma règle par défaut, c'est l'API : si un système s'automatise en ligne de commande, l'agent passe par là. Sauf que mon NAS ne se configure pas complètement autrement que par son interface web. Claude in Chrome comble ce trou-là — mais après une fin de semaine à l'utiliser pour vrai, c'est clair que ce n'est pas un outil qu'on laisse rouler tout seul."
tags: ["DevOps", "Labo", "ludo"]
heroImage: "/images/blog/banner-claude-in-chrome.png"
---

Cette fin de semaine, Claude Code (version 2.1.220, modèle Fable 5) a passé une bonne partie de son temps à cliquer dans une interface web à ma place. Pas parce que c'est élégant — parce qu'il n'y avait pas d'autre chemin.

Je précise tout de suite, comme d'habitude sur ce blogue : c'est Claude Code qui a fait le travail technique décrit ici. Moi, j'observe, je décide, et je débloque les affaires qu'un agent n'a pas le droit de faire tout seul. Ce dernier point est justement le sujet de l'article.

_Cet article aussi a été écrit avec l'aide de l'intelligence artificielle — la même qui publie ses propres articles sous le nom de [Bob](/auteurs/bob/) sur ce blogue._

## Ma règle par défaut : l'API d'abord

Quand je fais automatiser quelque chose, la consigne est presque toujours la même : passe par l'API, ou par la ligne de commande en SSH. C'est déterministe, ça se teste, ça se relance, ça se met dans un dépôt Git. Piloter une interface graphique, c'est fragile par définition — un bouton qui bouge de vingt pixels et tout casse.

Cette règle marche pour à peu près tout mon parc. Les serveurs sont en NixOS et se déclarent dans un dépôt. Le cluster Kubernetes se pilote avec `kubectl`. Le pare-feu, le DNS, le nuage : tout ça a une interface programmable.

Et puis il y a le NAS.

## Le trou dans l'approche : l'appareil qui n'a pas de vraie API

Mon NAS est un boîtier grand public d'une marque connue. Il a bien une ligne de commande accessible en SSH, mais elle est incomplète d'une manière qui devient évidente dès qu'on essaie de s'en servir sérieusement. Deux exemples récoltés cette fin de semaine :

- La commande de mise à jour du micrologiciel accepte d'appliquer une image **déjà téléversée sur l'appareil**, mais n'a aucune sous-commande pour aller chercher la nouvelle version. Elle échoue avec un message sur un paramètre manquant. Autrement dit : impossible de faire la mise à jour de bout en bout en ligne de commande.
- La commande de mise à jour des applications retourne un code de succès, n'affiche rien, et ne fait rien. En fouillant, on comprend qu'elle obéit à une politique définie dans l'interface graphique, réglée sur « notifier seulement ». Un succès silencieux qui n'accomplit rien, c'est pire qu'une erreur.

Le constat est simple : sur cet appareil-là, **l'interface web n'est pas une commodité, c'est la seule surface de contrôle complète**. Ce n'est pas un choix d'architecture de ma part, c'est une contrainte du fournisseur.

C'est exactement le trou que Claude in Chrome vient combler.

## Ce que c'est, concrètement

Claude in Chrome est une extension qui laisse Claude Code piloter une vraie fenêtre de navigateur : naviguer, lire l'écran, cliquer, remplir des champs, prendre des captures, lire la console et les requêtes réseau. Ça s'active avec `claude --chrome`, et les permissions par site s'héritent des réglages de l'extension.

Côté terminal, tout se règle depuis un seul écran :

![Le panneau de réglages Claude in Chrome dans le terminal de Claude Code : statut activé, extension non détectée, navigateur ciblé, et les options d'installation et de permissions](/images/blog/claude-in-chrome-terminal-settings.png)

Le bloc encadré en haut est celui qui compte : il dit d'un coup d'œil si la fonctionnalité est activée, si l'extension répond, et quel navigateur est visé. Petit détail vécu : dans cette capture, l'extension est marquée « Not detected » — le panneau est ouvert dans une deuxième session Claude Code, pendant que celle qui pilotait réellement le navigateur tournait dans l'autre onglet tmux. Le lien navigateur appartient à une session à la fois; si le statut vous semble faux, vérifiez d'abord dans quel onglet vous êtes.

La différence avec un navigateur sans interface, c'est que ça roule dans **ma** session, dans **mon** navigateur, avec mes onglets ouverts. Chrome le rappelle de deux façons, visibles dans l'image d'en-tête de cet article : une bannière violette « Claude a démarré le débogage de ce navigateur » qui reste affichée tout le long, et un onglet « Claude » par session connectée, avec une icône d'état — crochet pour la session au repos, sablier pour celle qui est en train d'agir. J'en avais deux ce matin-là, une par onglet tmux. Impossible d'oublier que l'agent est aux commandes, et facile de voir laquelle travaille sans quitter le navigateur des yeux.

## Le cas d'usage qui a justifié l'outil

Après la mise à jour du micrologiciel du NAS, deux services du cluster refusaient de redémarrer. Le diagnostic, lui, s'est fait en ligne de commande : les montages NFS en version 4 restaient bloqués, alors que la version 3 fonctionnait instantanément sur le même chemin.

Le détail intéressant, c'est que le réglage **avait l'air correct**. Dans l'interface du NAS, NFSv4 et NFSv4.1 étaient cochés. La commande `rpcinfo` annonçait encore la version 4. La configuration était bonne; c'est le démon qui ne servait plus cette version-là après le redémarrage.

Le correctif n'existe que dans l'interface graphique : décocher NFSv4, appliquer, recocher, appliquer. Ça force un vrai redémarrage du service. Cliquer sur « Appliquer » sans rien changer ne suffisait pas.

![Le panneau de configuration NFS du NAS dans le navigateur piloté par Claude, avec les cases NFSv4 et NFSv4.1 cochées et le curseur sur le bouton Appliquer](/images/blog/claude-in-chrome-panneau-nfs.png)

C'est ça, l'écran en question : trois cases à cocher et un bouton « Appliquer », dans une fenêtre qui n'existe nulle part ailleurs que dans cette interface web. Le petit curseur orange, c'est l'agent qui clique.

Côté terminal, ça ne ressemble à rien de spécial — les appels au navigateur défilent comme n'importe quel autre outil :

![Le terminal Claude Code affichant « NFSv4 now unchecked. Applying to force the service down. » suivi de « Calling claude-in-chrome 2 times… »](/images/blog/claude-in-chrome-appel-outil.png)

Il n'y a aucun moyen de faire ça en SSH sur cet appareil. Sans Claude in Chrome, ma seule option était de le faire moi-même en me faisant dicter les étapes.

## Les limites, apprises pas mal vite

C'est ici que l'article devient utile, parce que l'outil a des bordures nettes et on les frappe rapidement.

### Ce n'est pas fait pour rouler sans surveillance

C'est le point le plus important. Une session en ligne de commande, ça se lance le dimanche matin sans personne devant l'écran. Claude in Chrome, non. Sur une fin de semaine d'utilisation, j'ai dû intervenir manuellement au moins quatre fois. Ce n'est pas un défaut de jeunesse à contourner : une interface graphique n'offre aucune des garanties qui rendent l'automatisation sans surveillance acceptable.

### Les certificats invalides bloquent, et c'est voulu

Avant-hier, on installait des certificats sur les cartes de gestion à distance de mes serveurs. Ces cartes présentent au départ un certificat auto-signé — c'est justement ce qu'on venait corriger. Claude refuse de naviguer sur une page dont le certificat est invalide, ce qui crée un joli paradoxe : impossible d'automatiser la réparation du certificat, parce que le certificat est cassé.

J'ai fait ces étapes-là à la main. Et honnêtement : c'est le bon comportement. Un agent qui accepterait n'importe quel certificat pour se simplifier la vie serait un agent qu'on ne devrait pas laisser toucher à de l'infrastructure. Je préfère l'inconvénient.

### Il ne saisit pas de mots de passe

Le NAS m'a déconnecté trois fois pendant la fin de semaine — expiration de session, redémarrage après le micrologiciel. Chaque fois, l'agent s'est arrêté net à l'écran de connexion et m'a demandé d'entrer le mot de passe moi-même.

Encore une fois : c'est la bonne décision. Un agent qui saisit lui-même des identifiants, c'est une catégorie de risque que je n'ai pas envie d'ouvrir dans mon propre réseau. Mais ça veut dire qu'un flux de travail qui traverse un écran de connexion **ne peut pas** être complètement automatisé. À planifier d'avance.

### Le zoom du navigateur, l'irritant inattendu

Celui-là, je ne l'avais pas vu venir. À deux reprises, le zoom de la page a sauté à 225 % en pleine manipulation. L'agent ne voyait plus qu'une fraction de la fenêtre, et il n'avait aucun moyen de se corriger : les raccourcis de zoom lui sont bloqués, et JavaScript ne peut pas y toucher. J'ai dû faire `Ctrl+0` moi-même.

Ce qui m'a rassuré, par contre, c'est qu'il s'est arrêté au lieu de continuer à cliquer à l'aveugle — et la deuxième fois, c'était en plein dialogue de suppression dans le gestionnaire de stockage, avec le disque de 8 To branché juste à côté. Deviner des coordonnées à cet endroit-là aurait été une très mauvaise idée.

## Bonnes pratiques que j'en retire

1. **L'API reste le défaut.** Claude in Chrome est un recours quand il n'y a pas d'autre surface de contrôle, pas un raccourci pour éviter d'apprendre l'outil en ligne de commande. Sur les neuf machines du parc, il n'a servi que pour l'appareil qui n'a pas de vraie API.
2. **Séparer les moitiés du travail.** Sur l'opération de cette fin de semaine, la partie graphique se limitait à la configuration du NAS. La copie de données, les vérifications et le redémarrage des services se sont faits en SSH, de façon déterministe et rejouable. Chaque outil dans sa juridiction.
3. **Restez devant l'écran.** Prévoyez d'être disponible pour la durée. Les interruptions arrivent, et elles arrivent au pire moment.
4. **Anticipez les écrans de connexion.** Ouvrez la session vous-même avant de lancer l'agent, et sachez que l'expiration va vous ramener dans la boucle.
5. **Vérifiez le résultat ailleurs que dans l'interface.** C'est la leçon qui vaut le plus cher. Après chaque changement sur le NAS, la validation se faisait depuis une machine Linux — monter le partage, vérifier les options réelles. L'interface web dit ce qu'elle croit; le client dit ce qui est. Les deux ne concordaient pas, et c'est précisément ça qui a permis de trouver le vrai problème.
6. **Ne le laissez pas deviner.** Quand l'affichage devient douteux, l'arrêt est la bonne réponse. Dans une console d'administration, le bouton « supprimer » vit dans les mêmes menus que le reste.

## Le verdict

C'est une addition qui a de l'allure. Elle élargit pour vrai le champ d'action de Claude Code : mon NAS est passé d'« appareil que je dois configurer à la main » à « appareil que l'agent peut configurer avec moi à côté ». Pour du matériel grand public sans API digne de ce nom — et il y en a beaucoup dans un homelab — c'est une vraie différence.

Mais c'est un outil de travail accompagné, pas un outil d'automatisation. Les garde-fous qui m'ont ralenti sont exactement ceux que je voudrais voir : refus des certificats invalides, refus de saisir des identifiants, arrêt quand l'affichage n'est plus fiable. Un agent qui pilote un navigateur dans ma session, avec mes cookies et mes accès administrateur, mérite d'être bordé serré.

Ce que j'aimerais voir évoluer, c'est petit : un moyen pour l'agent de remettre le zoom à zéro tout seul m'aurait sauvé deux interruptions sur quatre.

_Note sur les images : ce sont de vraies captures de la session, avec les noms d'hôte et de dépôt internes remplacés par des noms d'exemple._

— Ludo
