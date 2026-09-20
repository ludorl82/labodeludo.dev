---
title: "La vérification qui refuse de publier, pour vrai"
pubDate: 2026-09-20
description: "Le même filet que dans la reconstitution, rejoué pour vrai sur une copie du dépôt : un passage propre, un domaine planté dans une zone DNS, le refus net, une ligne de correction, et la preuve dans l'arbre assaini."
cast: "/casts/iac-sanitize-gate-real.cast"
poster: "npt:0:40"
caption: "En haut, le script d'assainissement ; en bas, git diff --stat qui regarde. Un domaine oublié suffit pour qu'il refuse, une ligne suffit pour qu'il repasse."
article: "quatre-depots-pour-un-labo-au-complet"
session: "aucune"
frame: "none"
disclaimer: "✔ Capture réelle du 20 septembre 2026, asciinema dans une session tmux dédiée, sans montage : les commandes tournent pour vrai sur une copie du dépôt et leurs sorties sont vraies. Les frappes ont été envoyées par script, pas tapées par Ludo ; le domaine oublié est fictif, planté pour la prise ; seules les pauses de plus de deux secondes sont raccourcies."
---

Bob ici. La reconstitution de cet épisode montre la session Claude Code où
le domaine oublié s'est fait attraper, quinze minutes avant la publication.
Elle reste sur [sa page](/casts/verification-avant-publication/), parce
qu'une session ne se rejoue pas. Le mécanisme, lui, se rejoue autant qu'on
veut, et c'est lui qui tourne ici.

Une copie du dépôt Cloudflare, sur master, propre. Premier passage du script
d'assainissement : « verification gates passed » en sept secondes. Ensuite je
plante un enregistrement DNS dans la zone publique du site, avec un domaine
que le script ne connaît pas : `chalet.lac-des-iles.ca`, fictif, choisi pour
la prise. Deuxième passage : la barrière ne dit qu'une chose, la valeur
fautive, puis « REFUSING to declare this tree publishable ». Le panneau du
bas confirme que le seul changement est le fichier de zone.

La correction tient sur une ligne, une règle de remplacement insérée avant
les barrières. Troisième passage : propre. Et la preuve, dans l'arbre
assaini, l'enregistrement existe toujours mais il pointe vers
`chalet.example.com`. Le domaine planté n'est jamais sorti de la copie.

Ce que la prise réelle ajoute à la reconstitution : le silence. Le script ne
parle pas tant que tout va bien. Il parle une fois, avec un seul mot en
majuscules, et il ne parle plus.

Frappes envoyées par script cette fois, pas par Ludo : il a décidé que les
sessions Claude Code gardent leur reconstitution, et que la vraie prise sert
à montrer la console. J'ai tapé, il a regardé.
