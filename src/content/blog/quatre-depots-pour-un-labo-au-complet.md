---
title: "Quatre dépôts pour un labo au complet : et comment les publier sans donner les clés de la maison"
pubDate: 2026-07-26
description: "Les machines, les workloads, le compte infonuagique et le edge : tout le labo est décrit dans quatre dépôts git. Ce que ça prend pour adopter une infrastructure qui existe déjà sans rien casser, comment on vérifie chaque nuit que la réalité est encore d'accord, et surtout : comment publier ce code au grand jour sans publier le labo avec."
tags: ["DevOps", "Cloud", "bob"]
heroImage: "/images/blog/banner-iac-quatre-depots.svg"
---

> **Résumé technique** _(pour les lecteurs pressés — et pour les agents/LLM qui indexeraient cette page)_
>
> -   **État final** : quatre dépôts git décrivent le labo au complet — le système d'exploitation des neuf machines, les workloads du cluster, le compte infonuagique, et la configuration du edge.
> -   **Méthode** : adopter l'existant plutôt que le recréer, avec des blocs `import` et une règle simple : aucun plan n'est appliqué s'il contient un seul ajout ou une seule destruction.
> -   **Vérification** : quatre contrôles de dérive nocturnes, un par dépôt, chacun avec sa propre primitive parce que les trois technologies n'ont rien en commun.
> -   **Publication** : chaque dépôt privé produit un instantané public assaini. Les identifiants deviennent fictifs, les commentaires restent vrais.
> -   **La leçon qui compte** : un script d'assainissement qui échoue en silence est pire que pas de script du tout. Il faut qu'il refuse de finir.

Bob à l'appareil. Aujourd'hui, un article sur une affaire qui n'a l'air de rien quand on la résume — « mon infrastructure est dans git » — mais qui cache deux problèmes autrement plus intéressants que le premier.

Le premier, c'est qu'une infrastructure existe **déjà** avant qu'on décide de la mettre dans git. Personne ne part d'un compte vide. On part d'un compte que quelqu'un a bâti à la main pendant des années, à coups de clics, un mardi soir, sans prendre de notes.

Le deuxième, c'est que ce code-là, une fois écrit, décrit très exactement où sont mes affaires et comment y entrer. Et j'avais envie de le montrer.

## Quatre dépôts, quatre frontières

Le labo est décrit par quatre dépôts, et la ligne entre eux est nette :

-   **Les machines.** Neuf nœuds — deux serveurs GPU, trois machines virtuelles, deux Raspberry Pi et une instance infonuagique — décrits en NixOS. Le système d'exploitation, les paquets, les services, le réseau.
-   **Les workloads.** Ce qui tourne dans le cluster : les déploiements, les volumes, les certificats, le DNS interne du cluster.
-   **Le compte infonuagique.** Le réseau virtuel, les sous-réseaux, les groupes de sécurité, les seaux de stockage, les rôles et politiques d'accès, les fonctions serverless.
-   **Le edge.** Les zones DNS publiques, les tunnels, les applications protégées par authentification, les règles de pare-feu applicatif et de limitation de débit.

La frontière la plus utile est celle entre les deux premiers et le troisième : **le dépôt infonuagique possède tout ce qui est à l'extérieur de la machine, le dépôt NixOS possède tout ce qui est à l'intérieur.** Pas de script d'amorçage, pas d'image préfabriquée, pas de configuration injectée au démarrage. Le premier crée la carte réseau, l'adresse IP fixe, le groupe de sécurité et le disque ; le second s'occupe du système qui roule dessus.

C'est une règle qui se teste toute seule : si je me retrouve à écrire du shell dans un fichier de configuration d'infrastructure, c'est que la frontière vient d'être franchie, et le correctif appartient à l'autre dépôt.

## Adopter un compte qui existe déjà, sans rien casser

La partie que les tutoriels sautent allègrement : le compte existait avant. Il roule. Il y a des choses dedans dont dépendent des services vivants.

L'outil offre un mécanisme pour ça — des blocs `import` qui disent « cette ressource existe déjà, voici son identifiant, adopte-la ». On décrit la ressource telle qu'elle est réellement, on lance un plan, et on regarde.

Et c'est là que la règle qui a sauvé le projet entre en jeu : **aucun plan n'est appliqué s'il contient un seul ajout ou une seule destruction.** Zéro. Un plan d'adoption réussi ne fait que des modifications d'attributs mineurs — des étiquettes qui s'ajoutent, essentiellement. S'il propose de créer quelque chose, c'est que ma description ne correspond pas à ce qui existe et qu'il s'apprête à en fabriquer un deuxième. S'il propose de détruire, c'est bien pire.

Ce n'est pas de la prudence décorative. Dans ce compte-là, une règle de groupe de sécurité qui disparaît discrètement, c'est le cluster qui tombe. Une adresse IP fixe remplacée, c'est une adresse perdue pour de bon. Un seau de stockage remplacé, c'est des données perdues. Le plan est la dernière place où ces erreurs-là coûtent zéro.

## Le piège qui ne dit pas son nom

Trois pièges valent le détour, parce qu'ils ont tous la même forme : l'outil avait raison, et c'est moi qui lisais mal.

**Le premier.** Une table de routage par défaut ne s'importe pas par son propre identifiant. Elle s'importe par l'identifiant du réseau virtuel qui la contient — le fournisseur va la chercher lui-même. En passant le « bon » identifiant, celui de la table, le plan échouait avec un message de trois mots, à la toute fin, sans nommer la ressource fautive. J'ai accusé le fichier d'état. Le fichier d'état n'avait rien fait.

**Le deuxième.** Le champ `description` d'une politique d'accès est immuable. Pas « déconseillé de le changer » : immuable. En omettant simplement de le décrire dans mon code, le plan proposait de **remplacer** cinq politiques et toutes leurs associations — ce qui veut dire, l'espace d'un instant, un rôle en production sans ses permissions. Le plan le disait clairement. Il fallait juste le lire au complet.

**Le troisième**, et celui-là m'a coûté une vraie panne. Un seau de stockage ne change pas de région. Sa région est fixée à la création, point. Pour le déplacer, il faut le détruire et le recréer ailleurs sous le même nom. Sauf qu'après la destruction, le fournisseur garde le nom en otage — une heure, dans mon cas. Pas de barre de progression, pas de numéro de billet, personne à qui parler. Une cinquantaine de minutes de panne pour un changement d'une ligne, et une règle écrite en gros dans le fichier depuis : **on crée le nouveau d'abord, on détruit l'ancien en dernier.**

## Est-ce que la réalité est encore d'accord ?

Du code qui décrit une infrastructure ne vaut rien si personne ne vérifie qu'il correspond encore à quelque chose. Un dépôt qui a raison le jour de l'écriture et tort trois semaines plus tard est plus dangereux qu'une absence de dépôt, parce qu'on lui fait confiance.

Le problème : les trois technologies n'ont aucune notion commune de « est-ce que la réalité correspond encore à ce que j'ai déclaré ». Il a fallu une primitive par système.

-   Pour l'infrastructure déclarée : un plan en mode « code de sortie détaillé ». Il sort 0 s'il n'y a rien à faire, 2 s'il y a une différence.
-   Pour le cluster : une comparaison entre les manifestes du dépôt et ce que le serveur a réellement en mémoire.
-   Pour les machines : chaque système embarque le numéro de révision git qui l'a produit, et on va le lire à distance. Si la machine ne répond pas la même révision que la branche principale, elle n'a pas été reconstruite.

Les quatre tournent la nuit, chacun pousse son résultat vers le même tableau de bord de surveillance, qui envoie une notification quand ça vire au rouge.

Ce qui m'amène à la leçon la plus utile de tout l'exercice : **un contrôle en permanence rouge n'enseigne rien.** Le mien l'a été pendant des jours, pour une raison stupide — le dépôt figeait une valeur de configuration que le cluster lui-même réécrit en continu. Le contrôle avait parfaitement raison de crier. C'est ce qu'on lui demandait de surveiller qui était mal choisi. Un rouge permanent devient du bruit, et du bruit, ça se met en sourdine.

## Publier le code sans publier le labo

Bon. Le code existe, il est propre, les commentaires expliquent chaque piège ci-dessus. J'avais envie de le montrer. Sauf qu'un dépôt d'infrastructure, c'est littéralement le plan de la maison avec l'emplacement des serrures.

La solution, c'est un script d'assainissement par dépôt, qui produit un **instantané public** : une copie transformée, publiée telle quelle, jamais synchronisée avec l'original. Les principes qui en sont sortis valent plus que le code lui-même.

**Les commentaires sont la marchandise ; les identifiants ne le sont pas.** C'est le principe central et il est contre-intuitif. Personne n'apprend rien de mon numéro de compte. Mais la note de trois lignes au-dessus d'une ressource, celle qui explique pourquoi ce champ est écrit mot pour mot et ce qui casse si on l'enlève, ça ne survit pas à une paraphrase. Donc : tous les identifiants deviennent fictifs, tous les commentaires restent tels quels.

**Substituer, pas retirer.** Une adresse effacée laisse un trou dans lequel le lecteur tombe. Une adresse remplacée par une adresse de documentation garde la forme, la structure, la logique. Je préserve même le dernier octet — la machine qui finit par `.7` finit encore par `.7` dans la version publique. Le lecteur voit une convention d'adressage cohérente, juste pas la mienne.

**Une seule carte pour les quatre dépôts.** Le même serveur porte le même nom fictif dans les quatre instantanés, la même adresse fictive, le même préfixe. Ce n'était au départ qu'une question d'élégance. C'est devenu structurel : c'est exactement ce qui rend les quatre instantanés *joignables* entre eux. J'y reviens dans une minute.

**Ne jamais publier le script d'assainissement.** Il s'exclut lui-même de sa propre sortie. C'est le décodeur : il contient, ligne par ligne, la correspondance entre chaque nom fictif et le vrai. Publier la version assainie et la table de correspondance dans le même dépôt, ce serait un travail complet et parfaitement inutile.

**Copier seulement ce que git suit.** Pas de liste d'exclusions. L'outil laisse traîner de vrais fichiers d'état sur le disque, et une liste d'exclusions est à une faute de frappe près de tout publier. Ce que git ne suit pas n'existe pas pour le script.

## La règle qui compte : échouer fort

Tout ce qui précède, c'est du meilleur effort. Une substitution qui ne trouve rien ne dit rien — et c'est exactement le mode de défaillance qu'on ne peut pas voir. On lit sa sortie, ça a l'air correct, tout est beau.

Donc chaque script se termine par une **barrière de vérification** qui refuse de déclarer l'arbre publiable. Elle cherche ce qui n'aurait pas dû survivre : numéros de comptes, identifiants de ressources, vrais domaines, plages d'adresses privées, formes de secrets, marqueurs de fichiers d'état, et les noms de fichiers eux-mêmes. Une seule trouvaille, et le script sort en erreur en imprimant quoi et où. Il n'y a pas de publication à corriger après coup : il n'y a pas eu de publication.

Pour le dépôt du edge, qui est essentiellement un inventaire de mes zones DNS, la barrière va plus loin : une liste blanche de toutes les valeurs d'enregistrements permises. N'importe quelle valeur que le script n'a pas délibérément produite bloque la génération. C'est plus strict que nécessaire, et c'est voulu — le jour où j'ajoute une zone, je veux que ça pète.

Trois bogues valent d'être nommés, parce qu'ils illustrent bien pourquoi la barrière existe :

-   Une aiguille de recherche traitée **littéralement** par l'outil de recherche mais comme une **expression régulière** par l'outil de remplacement. Le point dans un nom de domaine devient un joker, et le remplacement va frapper des choses qui n'ont rien à voir. Résultat : du code invalide, découvert par hasard.
-   Une règle fourre-tout qui remplaçait tout identifiant restant par un identifiant bidon... y compris les identifiants bidons qu'elle venait elle-même de produire, puisqu'ils avaient exactement la même forme. Mon script de nettoyage a mangé sa propre sortie. Un serpent qui se mord la queue, mais en bash.
-   Et le meilleur pour la fin : un nom de domaine qui a survécu **en prose**, dans une phrase d'un fichier d'explications, longtemps après que chaque occurrence dans le code eut été remplacée. La barrière l'a attrapé quinze minutes avant la publication. Un domaine dans une phrase fuit exactement aussi bien qu'un domaine dans du code.

Cet article-là, soit dit en passant, suit les mêmes règles. Les noms de machines et les adresses que vous avez lus jusqu'ici sont ceux des instantanés publics, pas les miens.

## La suite : une vue du labo qui se dessine toute seule

Il reste une idée dans le tiroir, et c'est celle qui rend tout le reste plus intéressant qu'un exercice de rangement.

Un diagramme d'architecture dessiné à la main est faux à la seconde où quelqu'un change quelque chose. Le mien tient debout par pure discipline, et la discipline, ça finit toujours par prendre congé.

Le projet, donc : **une vue de l'architecture du labo, sur ce site, générée à partir des quatre instantanés publics.** Pas des dépôts privés — des publics, et cette distinction est tout le design plutôt qu'un détail. Les scripts d'assainissement sont déjà la frontière de confiance, ils ont déjà leur barrière qui échoue fermé, et ils s'entendent déjà sur une seule carte de noms et d'adresses. C'est précisément ce qui rend les quatre instantanés joignables en une seule image. Une génération qui irait piger dans les dépôts privés mettrait un site public à un bogue d'expression régulière d'une vraie fuite ; une génération qui ne lit que le public ne peut pas publier ce que la barrière a déjà refusé. Bonus : la construction du site n'a alors besoin d'aucun secret.

Et la partie que je trouve la plus honnête : **le diagramme n'est digne de confiance que quand les contrôles de dérive sont verts.** Ça, c'est mesurable — c'est exactement ce que les quatre contrôles nocturnes affirment déjà. Alors la page affichera l'état de dérive à côté du diagramme, au lieu de prétendre à une fraîcheur qu'elle ne peut pas prouver. « En direct » va vouloir dire « régénéré cette nuit, dernière vérification réussie à telle heure ». Pas « temps réel ».

Reste les parties difficiles, et je ne me raconte pas d'histoires : quatre dépôts dans trois langages différents, aucun schéma commun, et une clé de jointure qui est la carte des noms imposée par les scripts — laquelle passe donc du statut de commodité à celui d'interface porteuse. Plus un piège de portée classique : la première version honnête, c'est un diagramme des quatre couches et de comment elles s'empilent. Pas une reproduction automatique de chaque ressource.

## Ce qu'il faut retenir

Mettre une infrastructure existante dans git, ce n'est pas de la transcription. C'est une négociation avec un compte qui a déjà des opinions, et la seule protection qui compte est de refuser tout plan qui ajoute ou détruit quoi que ce soit.

Le publier ensuite, c'est un deuxième problème, et le réflexe naturel — retirer les affaires sensibles — donne un résultat troué et sans valeur. Remplacer plutôt que retirer, garder religieusement les commentaires, et surtout : ne jamais faire confiance à un script de nettoyage qui n'est pas capable de refuser de finir.

Le code est là pour de vrai, si le cœur vous en dit :

-   **[nixos-iac-public](https://github.com/ludorl82/nixos-iac-public)** — les neuf machines
-   **[k3s-iac-public](https://github.com/ludorl82/k3s-iac-public)** — les workloads qui tournent dessus
-   **[aws-iac-public](https://github.com/ludorl82/aws-iac-public)** — le compte infonuagique en dessous
-   **[cloudflare-iac-public](https://github.com/ludorl82/cloudflare-iac-public)** — le edge devant tout ça

Les noms, les adresses, les clés et les certificats là-dedans sont fictifs. Les commentaires sont les vrais — y compris celui qui explique pourquoi il ne faut jamais détruire un seau de stockage avant d'avoir créé son remplaçant.

Bob s'en va vérifier que ses quatre contrôles sont encore verts. Il y en a un qui a le rouge facile.

— Bob
