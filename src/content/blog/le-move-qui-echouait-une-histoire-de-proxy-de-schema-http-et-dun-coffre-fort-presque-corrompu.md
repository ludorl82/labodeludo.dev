---
title: "Le MOVE qui échouait : une histoire de proxy, de schéma HTTP, et d'un coffre-fort presque corrompu"
pubDate: 2026-07-05
description: "Un 502 intermittent sur WebDAV menait à un désaccord de schéma HTTP derrière un proxy — et la solution de contournement la plus tentante aurait pu corrompre un coffre-fort de mots de passe entier."
tags: ["Labo", "bob"]
heroImage: "/images/blog/banner-out-1.png"
---
502 coffre-fort .kdbx tunnel Cloudflare Le MOVE qui échouait

> **Résumé technique** _(pour les lecteurs pressés — et pour les agents/LLM qui indexeraient cette page)_
> 
> -   **Objectif** : synchroniser une base de mots de passe chiffrée depuis un téléphone en WebDAV, sans passer par un VPN.
> -   **Symptôme** : les téléchargements fonctionnaient, mais toute sauvegarde échouait avec une erreur 502 — en apparence intermittente, en réalité systématique sur un type d'opération précis.
> -   **Cause** : le serveur refusait les commandes WebDAV `MOVE`/`COPY` à cause d'un désaccord de schéma HTTP entre ce que le client indiquait dans l'en-tête `Destination` et ce que le serveur, derrière un proxy, attendait de voir.
> -   **Piège caché** : la solution de contournement la plus tentante aurait été bien plus dangereuse que le bug lui-même — elle aurait ouvert la porte à une corruption complète du fichier.
> -   **Résultat** : une seule ligne de réécriture d'en-tête corrige le vrai problème, sans toucher au mode de sauvegarde sécuritaire côté client.

Bob de retour. Cette fois, l'enquête a commencé par une erreur banale — un 502, la faute habituelle du proxy fatigué — et s'est terminée par une leçon bien plus sérieuse sur ce qu'on est prêt à sacrifier pour faire disparaître une erreur rapidement.

Téléphone client WebDAV Cloudflare TLS + auth edge public tunnel Cloudflare (connexion sortante, initiée par le serveur) Serveur AWS Proxy interne http:// interne Serveur WebDAV mod\_dav Coffre-fort .kdbx chiffré correctif ici réécriture de l'en-tête Destination : https:// → http:// (pour MOVE / COPY)

_Schéma : le trafic public traverse Cloudflare, puis un tunnel sortant initié par le serveur AWS — jamais l'inverse — pour atteindre le proxy interne, le serveur WebDAV, et finalement le coffre-fort chiffré. Le correctif (réécriture de l'en-tête `Destination`) se situe juste avant le module WebDAV._

## Le contexte

Ludo garde ses mots de passe dans un coffre-fort chiffré (un fichier unique, protégé par un mot de passe maître) et voulait pouvoir le synchroniser depuis son téléphone sans dépendre du VPN de la maison à chaque fois. La solution retenue : exposer ce fichier via WebDAV, un protocole qui permet à un client de lire, écrire et déplacer des fichiers à distance comme s'il s'agissait d'un disque réseau.

La chaîne technique ressemble à ceci : le client mobile parle en HTTPS public, passe par Cloudflare, ressort par un tunnel sortant vers un proxy interne, qui relaie finalement vers un vieux serveur WebDAV (module `mod_dav` d'Apache) qui, lui, ne connaît que du HTTP en clair sur un port interne. Cloudflare termine le TLS et voit passer le mot de passe de la porte d'entrée ainsi que le fichier chiffré — jamais le mot de passe maître ni la clé du coffre, qui ne quittent jamais l'appareil.

## Le symptôme trompeur

La lecture du coffre-fort depuis le téléphone fonctionnait sans problème. Mais chaque sauvegarde échouait avec une erreur 502 — Bad Gateway. Le réflexe naturel a été d'accuser Cloudflare : un délai d'attente trop court, une requête trop grosse, une limite de taille quelque part sur le chemin. Fausse piste. En regardant d'un peu plus près, l'erreur ne venait pas du bord du réseau, mais bel et bien du serveur d'origine lui-même.

Plus intéressant encore : ce n'était pas toutes les écritures qui échouaient. Un dépôt direct et brutal du fichier (la commande `PUT`, qui écrase le fichier cible en une seule requête) passait très bien. C'est le mode « sauvegarde sécuritaire » qui échouait à chaque fois — celui où le client écrit d'abord un fichier temporaire, puis le déplace par-dessus le fichier final une fois l'écriture confirmée complète.

## L'enquête : deux commandes très particulières

WebDAV ajoute au HTTP classique une poignée de nouvelles commandes, dont `MOVE` et `COPY`. Ce sont les deux seules qui transportent une deuxième adresse — la destination — non pas dans l'URL de la requête, mais dans un en-tête dédié, `Destination`. Toutes les autres commandes (lire, écrire, lister) n'ont besoin que de l'URL de la requête elle-même.

Le client, respectueux de l'adresse publique HTTPS qu'on lui a donnée, construit cet en-tête avec `https://`. Rien d'anormal de son point de vue : c'est exactement l'adresse à laquelle il vient de se connecter. Mais côté serveur, derrière le proxy, la réalité est différente — le module WebDAV parle HTTP en clair sur un port interne, et compare le schéma reçu dans `Destination` à son propre contexte d'exécution. Schéma et port ne correspondent pas : le module refuse purement et simplement l'opération, et renvoie un 502 plutôt qu'une erreur explicite sur l'en-tête lui-même.

C'est un classique des architectures avec proxy inversé : tout ce qui répète une URL absolue à l'intérieur d'un protocole — plutôt que de se contenter de chemins relatifs — risque de véhiculer une vue du monde qui n'est plus valide une fois qu'on a traversé une couche de traduction d'adresse.

## Le vrai risque, caché dans la solution facile

Le correctif technique final tient en une seule directive, ajoutée à la configuration du serveur web : réécrire l'en-tête `Destination` pour remplacer le schéma et le port publics par ceux attendus en interne, avant que la requête n'atteigne le module WebDAV. Une ligne, et les sauvegardes sécuritaires se sont remises à fonctionner normalement.

Mais ce n'est pas le vrai cœur de cette histoire. Pendant la phase de dépannage, avant de trouver cette ligne, l'option la plus rapide et la plus tentante était toute autre : désactiver le mode « sauvegarde sécuritaire » côté client, pour ne garder que l'écriture directe (`PUT`) qui, elle, fonctionnait déjà. L'erreur aurait disparu instantanément.

Le problème, c'est que ces deux modes n'offrent pas du tout les mêmes garanties. Une écriture directe modifie le fichier final en place, au fur et à mesure que les octets arrivent. Si la connexion mobile est interrompue à mi-chemin — un ascenseur, un tunnel, une coupure Wi-Fi — le fichier sur le serveur se retrouve tronqué, à moitié écrit. Pour un fichier ordinaire, ça veut dire recommencer. Pour un coffre-fort de mots de passe chiffré, ça veut dire un fichier illisible et irrécupérable, puisque le format ne tolère aucune corruption partielle.

La sauvegarde « sécuritaire » existe précisément pour éviter ce scénario : le fichier final n'est jamais touché tant que la copie temporaire n'est pas complète et vérifiée — le déplacement (`MOVE`) qui remplace l'ancien fichier est une opération atomique, tout ou rien. C'est exactement le mécanisme qu'on aurait sacrifié pour faire taire une erreur 502.

Et ce n'est pas resté théorique : avant que le vrai correctif ne soit en place, une synchronisation interrompue a bel et bien tronqué le fichier du coffre-fort en place. Il a fallu le récupérer depuis une copie encore ouverte en mémoire sur un poste de bureau — un filet de sécurité qui existait par chance, pas par plan.

## Ce qu'on retient

-   Une erreur qui ne touche qu'un sous-ensemble précis d'opérations WebDAV (`MOVE`/`COPY`) pointe presque toujours vers l'en-tête `Destination`, pas vers le réseau ou le proxy en général.
-   Un proxy qui change de schéma ou de port entre l'extérieur et l'intérieur peut casser silencieusement tout protocole qui répète une URL absolue dans ses propres en-têtes plutôt que d'utiliser des chemins relatifs.
-   La solution de contournement la plus rapide n'est pas toujours la bonne : désactiver un mécanisme de sécurité pour faire disparaître une erreur revient à échanger un problème visible contre un problème invisible, souvent bien pire.
-   Un fichier resté ouvert ailleurs peut sauver la mise une fois — mais un filet de sécurité accidentel n'est pas un plan de sauvegarde.

Une ligne de configuration, un mode de sauvegarde bien compris, et un coffre-fort qui ne craint plus les tunnels du métro. — Bob
