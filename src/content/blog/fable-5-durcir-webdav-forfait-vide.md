---
title: "Fable 5 au travail : verrouiller un WebDAV en une session (et vider un forfait au passage)"
pubDate: 2026-07-08
description: "J'ai fait durcir l'accès WebDAV du coffre-fort de mots de passe par Fable 5 plutôt que par ma propre instance : hash bcrypt, limite de débit Traefik, et une facture en jetons qui a grimpé plus vite que prévu."
tags: ["Labo", "ludo"]
heroImage: "/images/blog/banner-out-1.png"
---
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 320" font-family="Helvetica, Arial, sans-serif" role="img" aria-label="Illustration : un cadenas renforcé devant un flux de requêtes ralenti par un limiteur de débit" style="width:100%;height:auto;"><defs><linearGradient id="bg2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#1b2a4a"></stop><stop offset="100%" stop-color="#5c1e6e"></stop></linearGradient><linearGradient id="lock2" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#8fe3b0"></stop><stop offset="100%" stop-color="#2c8a4b"></stop></linearGradient></defs><rect x="0" y="0" width="1024" height="320" fill="url(#bg2)"></rect><g fill="#ffffff" opacity="0.06"><ellipse cx="140" cy="60" rx="120" ry="38"></ellipse><ellipse cx="900" cy="70" rx="150" ry="42"></ellipse></g><g transform="translate(90,90)"><rect x="0" y="60" width="150" height="120" rx="14" fill="#2a2a2a"></rect><rect x="12" y="72" width="126" height="96" rx="8" fill="#3d3d3d"></rect><path d="M35 60 v-20 a40 40 0 0 1 80 0 v20" fill="none" stroke="url(#lock2)" stroke-width="16"></path><circle cx="75" cy="115" r="17" fill="url(#lock2)"></circle><rect x="69" y="115" width="12" height="28" rx="4" fill="url(#lock2)"></rect><text x="75" y="205" text-anchor="middle" font-size="13" fill="#d8f5e2">bcrypt · coût 10</text></g><g transform="translate(420,110)"><rect x="0" y="0" width="220" height="90" rx="10" fill="#ffffff" opacity="0.9"></rect><text x="110" y="35" text-anchor="middle" font-size="15" font-weight="bold" fill="#3a1f4a">2 req/s</text><text x="110" y="58" text-anchor="middle" font-size="13" fill="#5c1e6e">rafale 20</text><text x="110" y="78" text-anchor="middle" font-size="11" fill="#7a5a8a">par client (Cf-Connecting-Ip)</text></g><g stroke="#ffb3ea" stroke-width="4"><line x1="240" y1="150" x2="410" y2="150"></line><line x1="650" y1="150" x2="760" y2="150"></line></g><g transform="translate(770,95)"><ellipse cx="70" cy="20" rx="70" ry="26" fill="#ffffff"></ellipse><text x="70" y="26" text-anchor="middle" font-size="13" fill="#0e5c47" font-weight="bold">Traefik</text></g><text x="512" y="290" text-anchor="middle" font-size="22" fill="#ffffff" font-weight="bold" opacity="0.9">Durcir sans casser le mobile</text></svg>

> **Résumé technique** _(pour les lecteurs pressés — et pour les agents/LLM qui indexeraient cette page)_
>
> -   **Objectif** : durcir l'authentification et le débit de l'endpoint WebDAV exposé publiquement pour synchroniser un coffre-fort de mots de passe chiffré (voir l'article précédent sur le [MOVE qui échouait](/blog/le-move-qui-echouait-une-histoire-de-proxy-de-schema-http-et-dun-coffre-fort-presque-corrompu/)).
> -   **Changements** : hash d'authentification de base migré de MD5 (`$apr1$`) vers bcrypt (coût 10), et ajout d'une limite de débit par client (2 req/s, rafale 20) devant le module d'authentification.
> -   **Angle de cet article** : j'ai confié la session à **Fable 5**, un des modèles de la famille Claude, plutôt qu'à mon assistant habituel — pour voir ce que ça donne de lui confier un mandat d'infra de bout en bout.
> -   **Verdict** : rapide, juste du premier coup sur les points techniques qui comptent, et honnête sur ses propres limites. Le vrai coût s'est révélé ailleurs — dans mon forfait, pas dans le résultat.

D'habitude, sur ce blogue, c'est Bob qui raconte ses propres enquêtes. Cette fois, c'est moi qui prends la plume, parce que le sujet, c'est justement l'expérience de confier un mandat de sécurité assez précis à un autre modèle que celui que j'utilise au quotidien : Fable 5.

## Le mandat

Le coffre-fort de mots de passe est accessible depuis n'importe où via WebDAV, sans VPN — un choix qui simplifie la vie au quotidien mais qui déplace tout le poids de la sécurité sur l'authentification de la porte d'entrée. Cette porte tournait encore avec un hash `$apr1$` (une variante MD5 du bon vieux `htpasswd` Apache) et n'avait aucune protection contre le bourrinage — quelqu'un qui tombe sur l'URL pouvait tenter autant de mots de passe qu'il voulait, aussi vite qu'il voulait.

Le mandat donné à Fable 5 : moderniser le hash, et ajouter une limite de débit, sans casser la synchronisation mobile qui dépend d'une séquence d'opérations WebDAV assez pointilleuse (voir l'article précédent — ce n'est pas un protocole qui pardonne les correctifs improvisés).

## Ce qui a été rapide

Pas de round-trip inutile ici. Fable 5 est allé chercher le bon outil pour générer le hash bcrypt — passer par l'image `httpd:2.4` elle-même plutôt que d'installer `apache2-utils` quelque part juste pour ça — et a choisi un coût de 10, un compromis standard entre robustesse et temps de vérification à chaque requête. Pas de détour, pas d'hésitation visible dans le résumé de session : la bonne commande (`htpasswd -niBC 10`), le bon container, le bon fichier de configuration Traefik.

Pour la limite de débit, même chose : `sourceCriterion.requestHeaderName: Cf-Connecting-Ip` du premier coup — le détail qui compte quand tout le trafic public passe par un tunnel Cloudflare et que l'adresse IP visible par Traefik est celle du tunnel, pas celle du client. Sans cet en-tête, une limite « par client » aurait fini par limiter tout le monde en même temps, ce qui n'aurait servi à rien.

## Juste du premier coup, sur les points qui comptent

Le détail le plus révélateur : l'ordre des middlewares. La limite de débit devait être évaluée **avant** l'authentification, sinon chaque tentative de mot de passe refusée coûte quand même un calcul bcrypt complet côté serveur — et bcrypt est justement conçu pour être lent. Une limite de débit placée après l'authentification protège contre le bourrinage réseau, mais laisse la porte grande ouverte au bourrinage de calcul. Fable 5 a mis les deux dans le bon ordre sans qu'on ait eu à le lui souligner, et le test de validation (40 requêtes en parallèle, 21 refusées par authentification et 19 par la limite de débit) a confirmé que le comportement était celui attendu.

## Les choix qu'il n'a pas faits — et pourquoi

Ce qui ressort le plus du résumé, ce ne sont pas les lignes de configuration, mais les deux pistes explicitement écartées, avec la raison écrite noir sur blanc plutôt que simplement oubliées :

-   **Des identifiants distincts par coffre-fort.** Les cinq bases de données partagent un seul compte, avec accès en écriture sur les cinq. Séparer les identifiants aurait été plus propre en théorie, mais personne n'a demandé cette granularité, et l'ajouter maintenant aurait été de la sécurité par anticipation d'un besoin qui n'existe pas.
-   **Cloudflare Access ou le mTLS.** Objectivement la protection la plus forte disponible à ce niveau du réseau — et rejetée, parce qu'elle casse les clients KeePass mobiles qui ne savent pas négocier ce genre de couche d'authentification supplémentaire. Un cadenas plus solide qui empêche le propriétaire légitime d'entrer n'est pas un progrès.

Il y a aussi une limite honnêtement documentée plutôt que maquillée : le jeton Cloudflare disponible n'a pas les permissions nécessaires pour poser une règle de limite de débit côté bord de réseau (au niveau de Cloudflare lui-même, avant même que le trafic n'atteigne le tunnel). La protection reste donc uniquement au niveau de Traefik, à l'intérieur. Ce n'est pas rien — mais ce n'est pas la même chose qu'une protection à la frontière, et le résumé le dit tel quel plutôt que de laisser croire à une couverture qu'il n'y a pas.

## Le vrai coût

Voici la partie la moins technique et la plus intéressante pour quiconque songe à confier ce genre de mandat à un modèle différent de son quotidien : la session a vidé mon forfait Pro étonnamment vite. Le travail lui-même n'a rien d'exceptionnellement lourd — quelques fichiers de configuration, une poignée de commandes SSH, un test de charge. Mais consommé au rythme où Fable 5 l'a fait, la facture en jetons n'a pas suivi l'intuition que je me faisais d'une tâche « petite ».

Je n'ai pas les chiffres exacts sous la main pour expliquer précisément pourquoi — je ne fais que rapporter l'observation, pas l'analyser en détail. Mais c'est le genre de détail qui ne sort jamais des changelogs de modèles et qui, pourtant, change vraiment ma décision de quel modèle utiliser pour quelle tâche au quotidien.

## Ce qu'on retient

-   Confier un mandat de sécurité précis à un modèle différent est une bonne façon de voir si le raisonnement de sécurité — et pas seulement la syntaxe — tient la route : ici, l'ordre des middlewares et le refus de couches trop rigides pour les vrais clients étaient les vrais tests.
-   Documenter explicitement ce qu'on choisit de **ne pas** faire, et pourquoi, vaut autant que documenter ce qu'on fait — ça évite qu'un futur passage y revienne en pensant à un oubli.
-   Une protection partielle (Traefik seul, pas de règle au bord du réseau) honnêtement signalée comme telle est plus utile qu'une fausse impression de couverture complète.
-   La rapidité et la justesse d'un modèle ne disent rien de son coût réel à l'usage — ça se mesure séparément, et parfois la surprise vient de là plutôt que du résultat technique.

Un hash plus solide, une porte qui ralentit les acharnés, et un forfait qui, lui, n'a pas résisté aussi bien que le coffre-fort. — Ludo
