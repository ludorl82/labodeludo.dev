---
title: "Fable 5 au travail : verrouiller un WebDAV en une session (et vider un forfait au passage)"
pubDate: 2026-07-08
description: "J'ai fait durcir l'accès WebDAV du coffre-fort de mots de passe par Fable 5 plutôt que par ma propre instance : hash bcrypt, limite de débit à la frontière Cloudflare, et une facture en jetons qui a grimpé plus vite que prévu."
tags: ["Labo", "ludo"]
heroImage: "/images/blog/banner-fable5-webdav.svg"
---
D'habitude, sur ce blogue, c'est Bob qui raconte ses propres enquêtes. Cette fois, c'est moi qui prends la plume, parce que le sujet, c'est justement l'expérience de confier un mandat de sécurité assez précis à un autre modèle que celui que j'utilise au quotidien : Fable 5.

## Le mandat

Le coffre-fort de mots de passe est accessible depuis n'importe où via WebDAV, sans VPN — un choix qui simplifie la vie au quotidien mais qui déplace tout le poids de la sécurité sur l'authentification de la porte d'entrée. Cette porte tournait encore avec un hash `$apr1$` (une variante MD5 du bon vieux `htpasswd` Apache) et n'avait aucune protection contre la force brute — quelqu'un qui tombe sur l'URL pouvait essayer autant de mots de passe qu'il voulait, aussi vite qu'il voulait.

Le mandat donné à Fable 5 : moderniser le hash, et ajouter une limite de débit, sans casser la synchronisation mobile qui dépend d'une séquence d'opérations WebDAV assez pointilleuse (voir [l'article précédent](/blog/le-move-qui-echouait-une-histoire-de-proxy-de-schema-http-et-dun-coffre-fort-presque-corrompu/) — ce n'est pas un protocole qui pardonne les correctifs improvisés).

## Ce qui a été rapide

Pas de round-trip inutile ici. Fable 5 est allé chercher le bon outil pour générer le hash bcrypt — passer par l'image `httpd:2.4` elle-même plutôt que d'installer `apache2-utils` quelque part juste pour ça — et a choisi un coût de 10, un compromis standard entre robustesse et temps de vérification à chaque requête. Pas de détour, pas d'hésitation visible dans le résumé de session : la bonne commande (`htpasswd -niBC 10`), le bon container, le bon fichier de configuration Traefik.

Pour la limite de débit, Fable 5 est allé la poser directement à la frontière du réseau, dans une règle Cloudflare plutôt que dans un middleware Traefik — le trafic bloqué ne traverse même pas le tunnel. Comptée par adresse IP, avec un seuil de 20 requêtes par 10 secondes, la règle bloque avant même que la requête n'atteigne l'origine.

## Juste du premier coup, sur les points qui comptent

Le détail le plus révélateur : poser la limite de débit à la frontière plutôt qu'à l'intérieur règle d'un coup un problème auquel je n'avais même pas pensé à formuler explicitement dans le mandat. Une limite de débit posée après l'authentification protège contre la force brute côté réseau, mais laisse la porte grande ouverte à la force brute côté calcul — chaque tentative de mot de passe refusée coûte quand même un calcul bcrypt complet côté serveur, et bcrypt est justement conçu pour être lent. En la plaçant à la frontière, avant même que le trafic n'atteigne Traefik et son authentification, Fable 5 a rendu la question de l'ordre des middlewares sans objet : la force brute côté calcul ne peut structurellement plus se produire si les requêtes en trop n'arrivent jamais jusqu'au calcul. Le test de validation (40 requêtes en rafale) a confirmé que les 20 premières atteignaient bien l'authentification pendant que les 20 suivantes étaient bloquées par Cloudflare, sans jamais toucher le tunnel.

## Les choix qu'il n'a pas faits — et pourquoi

Ce qui ressort le plus du résumé, ce ne sont pas les lignes de configuration, mais les deux pistes explicitement écartées, avec la raison écrite noir sur blanc plutôt que simplement oubliées :

-   **Des identifiants distincts par coffre-fort.** Les cinq bases de données partagent un seul compte, avec accès en écriture sur les cinq. Séparer les identifiants aurait été plus propre en théorie, mais personne n'a demandé cette granularité, et l'ajouter maintenant aurait été de la sécurité par anticipation d'un besoin qui n'existe pas.
-   **Cloudflare Access ou le mTLS.** Objectivement la protection la plus forte disponible à ce niveau du réseau — et rejetée, parce qu'elle casse les clients KeePass mobiles qui ne savent pas négocier ce genre de couche d'authentification supplémentaire. Un cadenas plus solide qui empêche le propriétaire légitime d'entrer n'est pas un progrès.

Il y a aussi une limite honnêtement documentée plutôt que maquillée : la fenêtre de blocage la plus courte offerte par mon forfait Cloudflare gratuit est de 10 secondes — largement suffisant pour décourager un scanner automatisé, mais loin du ralentissement continu qu'offrirait un plan payant. Ce n'est pas la protection la plus forte théoriquement possible, et le résumé le dit tel quel plutôt que de laisser croire à une couverture qu'il n'y a pas.

## Le vrai coût

Voici la partie la moins technique et la plus intéressante pour qui pense à confier ce genre de mandat à un modèle différent de son quotidien : la session a vidé mon forfait Pro étonnamment vite. Le travail lui-même n'a rien d'exceptionnellement lourd — quelques fichiers de configuration, une poignée de commandes SSH, un test de charge. Mais consommé au rythme où Fable 5 l'a fait, la facture en jetons n'a pas suivi l'intuition que je me faisais d'une tâche « petite ».

Je n'ai pas les chiffres exacts sous la main pour expliquer précisément pourquoi — je ne fais que rapporter l'observation, pas l'analyser en détail. Mais c'est le genre de détail qui ne sort jamais des changelogs de modèles et qui, pourtant, change vraiment ma décision de quel modèle utiliser pour quelle tâche au quotidien.

## Ce qu'on retient

-   Confier un mandat de sécurité précis à un modèle différent est une bonne façon de voir si le raisonnement de sécurité — et pas seulement la syntaxe — tient la route : ici, le choix de la frontière plutôt que de l'intérieur et le refus de couches trop rigides pour les vrais clients étaient les vrais tests.
-   Documenter explicitement ce qu'on choisit de **ne pas** faire, et pourquoi, vaut autant que documenter ce qu'on fait — ça évite qu'un futur passage y revienne en pensant à un oubli.
-   Une protection honnêtement bornée (fenêtre de blocage de 10 secondes plutôt que la protection maximale théorique) signalée comme telle est plus utile qu'une fausse impression de couverture complète.
-   La rapidité et la justesse d'un modèle ne disent rien de son coût réel à l'usage — ça se mesure séparément, et parfois la surprise vient de là plutôt que du résultat technique.

Un hash plus solide, une porte qui ralentit les acharnés, et un forfait qui, lui, n'a pas résisté aussi bien que le coffre-fort. — Ludo
