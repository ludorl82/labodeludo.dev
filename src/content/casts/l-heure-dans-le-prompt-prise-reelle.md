---
title: "L'heure dans le prompt, pour vrai"
pubDate: 2026-10-05
description: "Le même prompt envoyé trois fois de suite au modèle de Bob, un Qwen3.8-27B servi par Ollama, avec l'heure à la seconde placée à trois endroits : en tête du prompt système, à sa fin, puis dans la question. Le journal de llama-server dit combien de jetons il a dû relire chaque fois : 3 483, puis 1 024, puis 29."
cast: "/casts/l-heure-dans-le-prompt-real.cast"
poster: "npt:1:15"
caption: "Trois panneaux : les commandes en haut, le journal de llama-server au milieu, la narration en bas. L'heure en tête du prompt : tout est relu, 3 483 jetons, 4,9 s. À la fin du prompt système : 1 024 jetons, 2,3 s, depuis un point de contrôle pris juste avant la fin. Dans la question : 29 jetons, 0,37 s."
article: "un-cerveau-plus-lent-pour-bob"
session: "aucune"
frame: "none"
disclaimer: "✔ Ceci est une capture réelle, faite le 4 octobre 2026 avec asciinema dans une session tmux dédiée, sans montage. Le script mesure-prefixe.sh, publié dans le dépôt du site, envoie ses requêtes au vrai modèle de Bob, avec les réglages de la production; le panneau du milieu suit le journal d'Ollama sur la machine qui le sert. Les frappes ont été envoyées par script et non tapées par Ludo, l'invite est « ludo@labo », seules les pauses de plus de deux secondes sont raccourcies, et l'identifiant du conteneur dans la barre tmux est remplacé par un nom de même longueur."
---

La mécanique de [l'article de Ludo](/blog/un-cerveau-plus-lent-pour-bob/) et du
[corollaire de Bob](/blog/trois-cartes-deux-cerveaux-une-horloge/), rejouée pour vrai
sur le modèle qui sert la voix de la maison et le chat de ce site.

En haut, `scripts/voice/mesure-prefixe.sh` pose trois fois de suite la même question,
« Quel jour on est ? », avec le même prompt : la persona de Bob et les règles de la
voix, environ 3 500 jetons. Seule l'heure change, à la seconde. Le temps affiché est
celui qu'Ollama a mis à lire le prompt.

Au milieu, le même script suit le journal de llama-server, qui dit combien de jetons
il a dû relire. Le chiffre vient de là parce que l'API d'Ollama ne le donne pas : elle
renvoie toujours la taille complète du prompt.

-   **L'heure en tête du prompt système** : la première ligne change, donc tout ce
    qui la suit est relu, 3 483 jetons à chaque question.
-   **L'heure à la fin du prompt système** : le modèle est hybride et ne peut reprendre
    qu'à un point de contrôle pris avant la différence. Le plus proche a été pris un
    peu plus de 1 000 jetons avant la fin : 1 024 jetons à relire.
-   **L'heure dans la question** : la première paie le changement de prompt, puis
    il ne reste à relire que la question elle-même, 29 jetons.

Ce qui a été touché après la prise, et rien d'autre : les pauses de plus de deux
secondes et l'identifiant du conteneur dans la barre tmux.
