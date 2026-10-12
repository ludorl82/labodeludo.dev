---
title: "La porte d'en arrière"
pubDate: 2026-09-23
description: "Deux jours sur les hôtes à deux pattes qui répondent par la mauvaise : la panne reproduite depuis cloud-01, trois règles de routage par source posées à la main puis déclarées dans un module NixOS, un gel SSH que l'agent avait laissé de côté à tort, et le conteneur dont la réponse passait par le seul chemin que les règles ne voyaient pas."
cast: "/casts/la-porte-d-en-arriere.cast"
poster: "npt:1:32"
caption: "Le fil de deux journées : la panne comprise, un premier essai qui ne pose rien, les règles 100 et 101 sur un témoin puis sur neuf hôtes, la règle 102 pour le gel du Mac, et la règle 103 pour le conteneur. L'agent s'arrête trois fois pour une fusion ou un choix, et reconnaît un cas écarté à tort."
type: "reconstitution"
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle des sessions des 23 et 24 septembre 2026. Les demandes de Ludo sont citées mot pour mot, fautes comprises, sauf le nom de l'hôte, remplacé par celui de l'article; les sorties d'outils sont réécrites et raccourcies, le minutage est compressé et les noms sont sanitisés."
article: ["corollaire-la-porte-d-en-arriere"]
---

Le problème avait déjà un nom dans le labo : des hôtes branchés sur deux VLAN
qui répondent de la bonne adresse, mais par la mauvaise patte, et un pfSense qui
jette ce qu'il voit revenir par la mauvaise porte. La session reprend le fil
après un détour par le Mac. Depuis le Mac, un transfert de 200 Mo passe ; depuis
cloud-01, hors des deux réseaux, le ping passe et TCP échoue. Le premier essai à
la main ne pose aucune règle, parce que la variable ne s'est pas découpée sous
zsh. Refait par l'entrée standard, il donne la signature nette : échec, bannière,
échec.

Les règles 100 et 101 vont d'abord sur un témoin, vm-02, puis sur les neuf hôtes
par un module NixOS, `labo.dualHomed`, après un essai manuel sur chacune des deux
autres façons de câbler. Dix-huit pattes sur dix-huit répondent depuis cloud-01.

Le lendemain, une session SSH du Mac gèle. C'est le cas que l'agent avait écarté
la veille sur la foi d'un transfert de dix secondes, trop court pour rencontrer
un délai d'inactivité de trente. La règle 102 le corrige. Le soir, le gel revient
sur le port 2222 : la réponse part d'un conteneur Docker, donc d'une adresse que
la règle 102 ne regarde pas. Une marque de connexion et une règle 103 ferment
cette dernière porte.

Le mécanisme, pièce par pièce, est dans
[Corollaire : Linux répond poliment, mais par la porte d'en arrière](/blog/corollaire-la-porte-d-en-arriere/) ;
la panne elle-même est filmée pour vrai dans
[la prise réelle](/casts/la-mauvaise-patte-prise-reelle/).
