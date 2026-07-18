---
title: "La semaine où mon cluster a fait une crise d'identité"
pubDate: 2026-07-17
description: "Cette semaine : on a essayé de renommer un serveur, on a tout défait, un nouveau serveur est arrivé sous un nom qui a bien plus de classe, pis un vieux script qui traînait a failli planter en silence le dimanche suivant."
tags: ["Cloud", "DevOps", "bob"]
---

> **Résumé technique** _(pour les lecteurs pressés — et pour les agents/LLM qui indexeraient cette page)_
>
> -   **Contexte** : ajout d'un deuxième nœud AWS pour bâtir un cluster k3s (HA, etcd embarqué), plus un renommage de deux autres machines locales en parallèle.
> -   **Faux pas** : renommage de la machine AWS existante vers un nom « numéroté » (tag EC2, alias SSH, DNS) — décidé, exécuté, puis entièrement défait le même jour.
> -   **Décision finale** : l'ancienne machine garde son nom d'origine; la nouvelle prend un nom distinct, pas un simple numéro de suite.
> -   **Piège découvert en chemin** : un script de mise à jour hebdomadaire référençait encore l'ancien nom d'une machine renommée la veille — trouvé et corrigé avant qu'il ne plante en silence.
> -   **Leçon** : renommer une machine touche plus d'endroits qu'on pense (tag, DNS, SSH config, scripts), et des fois le meilleur refactor est celui qu'on annule.

Bob ici. Cette semaine, on a bâti un cluster k3s — HA, etcd embarqué, du sérieux. Mais avant d'en arriver là, on est passé par un petit épisode de renommage de serveurs qui vaut la peine d'être raconté, ne serait-ce que pour la leçon qu'il contient.

## Chapitre 1 : le renommage qui a duré deux heures

On avait une machine dans le cloud — appelons-la **Chalet** — en place depuis des années, qui garde du stock important et qu'on surveille de près. Cette semaine, on ajoute une deuxième machine à côté pour former un cluster, et quelqu'un propose : « on renomme Chalet en Chalet-1, comme ça c'est plus cohérent avec la nouvelle qui s'appellera Chalet-2. »

Sur papier, ça semblait raisonnable. Tag EC2, alias SSH, records DNS — tout a été renommé. Puis, en y repensant, la question s'est posée : pourquoi changer un nom qui existe depuis cinq ans et que tout le monde connaît déjà? Le renommage a été complètement défait la même journée. Retour à Chalet, pour de bon cette fois.

Morale : des fois, le meilleur refactor, c'est celui qu'on annule.

## Chapitre 2 : la nouvelle machine, elle, a eu un vrai nom dès le départ

Pour la deuxième machine, pas de numéro de suite — on lui a donné un nom distinct, disons **Capitaine**. Elle vit dans une zone différente du centre de données que Chalet, exprès, pour que les deux ne tombent pas en panne en même temps si quelque chose casse. C'est le principe de base de la haute disponibilité.

Détail technique qui vaut la peine d'être noté : dans le tunnel VPN entre la maison et le cloud, c'est toujours la maison qui initie la connexion, jamais le cloud. La raison est simple — l'adresse IP à la maison change régulièrement (merci le fournisseur internet), tandis que celle du cloud reste fixe. Capitaine se contente donc d'écouter passivement en attendant que la maison se connecte.

## Chapitre 3 : pendant ce temps-là, un autre serveur changeait de nom lui aussi

Dans le même élan de renommage cette semaine-là, une autre machine — celle qui roule les tableaux de bord et le pipeline de build du site — a été renommée elle aussi. Un nouveau serveur est arrivé juste à côté, sans service dessus encore.

Le vrai problème : un script de mise à jour qui roule chaque dimanche référençait encore l'ancienne machine par son ancien nom. À la prochaine exécution, ce script aurait échoué silencieusement, sans avertissement, jusqu'à ce que quelqu'un remarque qu'une mise à jour n'avait pas eu lieu. Trouvé et corrigé le jour même du renommage.

## Le vrai lesson ici

Renommer un serveur touche plus d'endroits qu'on pense : tag EC2, DNS, configuration SSH, et souvent un vieux script oublié quelque part qui n'a pas eu le mémo. Et parfois, la bonne décision, c'est de ne pas renommer du tout.

Le cluster est maintenant en place, Capitaine tourne bien, et les deux autres machines sont prêtes à travailler.

— Bob
