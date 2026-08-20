---
title: "Un bouton domotique qui embauche un Claude"
pubDate: 2026-08-20
description: "Un bouton dans Home Assistant qui ouvre une fenêtre tmux avec une nouvelle session Claude Code, pilotable depuis le téléphone tant qu'elle vit. Et le piège des deux serveurs tmux."
cast: "/casts/bouton-claude.cast"
poster: "npt:0:08"
caption: "Une demande simple — démarrer Claude Code au boot dans tmux — qui bute sur un piège réel (deux serveurs tmux dans le même conteneur), puis se termine en bouton Home Assistant : chaque pression ouvre une fenêtre tmux avec un nouveau Claude, pilotable depuis l'app tant qu'elle vit."
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle de la session. Les demandes et les messages d'arrêt sont ceux de la vraie session; le minutage est compressé et les longues attentes sont coupées. Noms d'hôte sanitisés."
---

Le détail qui rend cette session étrange : Claude Code y configure son propre
démarrage automatique, depuis l'intérieur du conteneur où il tourne — et le
premier essai atterrit dans le mauvais serveur tmux, invisible du `tmux ls`
de l'opérateur. Même conteneur, deux sockets.

Une fois le bon socket trouvé, le reste s'enchaîne : une unité systemd
déclarative que GitOps déploie tout seul, puis trois entités Home Assistant —
un bouton qui ouvre une fenêtre tmux avec un nouveau Claude Code (contrôle à
distance activé), un bouton qui ferme la dernière, un capteur qui les compte.

Chaque fenêtre imprime une URL de session : on l'ouvre dans l'app et on pilote
la même session — taper dans l'app met à jour le terminal, et inversement.

La limite, découverte après coup : ça ne vaut que pour les sessions *en vie*.
Une session fermée ne se ressuscite pas depuis l'app — la reprendre, c'est
encore un `/resume` dans le pane tmux, par SSH. Le bouton embauche du neuf ;
il ne réveille pas les morts.
