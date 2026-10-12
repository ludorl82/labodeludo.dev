---
title: "Trois cartes, deux cerveaux"
pubDate: 2026-09-25
description: "Deux sessions autour de la voix de Bob : le soir où elle passe au modèle dense de 27 milliards de paramètres, réglé depuis un téléphone, puis la mesure du préfixe qui a montré où une horloge doit aller dans un prompt mis en cache, et ce que l'agent avait mal compris la première fois."
cast: "/casts/trois-cartes-deux-cerveaux.cast"
poster: "npt:1:48"
caption: "Le fil de deux sessions : la voix qui relit tout son prompt, le banc du modèle dense, trois lignes en haut du prompt, la place de traitement qu'on ne peut pas doubler, puis la mesure du 4 octobre et la cache chaude pour le mauvais prompt. L'agent s'arrête deux fois, et se corrige trois fois."
frame: "none"
type: "reconstitution"
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir des transcriptions réelles de deux sessions, le 25 septembre puis du 4 au 6 octobre 2026. Les demandes de Ludo sont citées mot pour mot, fautes comprises; les sorties d'outils sont réécrites et raccourcies, le minutage est compressé et les noms sont sanitisés."
article: ["trois-cartes-deux-cerveaux-une-horloge", "un-cerveau-plus-lent-pour-bob"]
---

Un soir de septembre, depuis un téléphone, une question simple : qu'est-ce qui
prend du temps quand on parle à la voix de la maison ? Le journal d'Ollama
répond que chaque question relit tout son prompt, plus de 5 000 jetons.
L'agent accuse d'abord l'architecture hybride du modèle, « cause probable, pas
prouvée ». Le banc du modèle dense le contredit : la cache fonctionne, ce sont
trois lignes en haut du prompt de la voix (la température, l'heure à la minute,
les prévisions) qui changent à chaque question.

La météo devient un outil, la relecture tombe à une vingtaine de jetons, et le
modèle dense remplace le modèle à mélange d'experts partout. Puis le chat du
site est soupçonné de vider la cache de la voix ; le remède proposé, deux
places de traitement, se heurte à un avertissement du journal : ce modèle n'en
a qu'une.

Neuf jours plus tard, pendant l'écriture des articles, le script de mesure
montre ce que `prompt_eval_count` cachait : l'heure à la fin du prompt système
ne suffit pas, parce qu'un modèle hybride ne reprend qu'à un point de contrôle.
L'agent corrige deux choses qu'il avait affirmées le 25 septembre, puis une
troisième : la cache ne se vidait pas, elle était chaude pour le mauvais
prompt, et le chat du site n'avait rien évincé.

La version courte est dans
[Un cerveau plus lent pour Bob](/blog/un-cerveau-plus-lent-pour-bob/) ; la
théorie, les journaux et les aveux, dans
[Trois cartes, deux cerveaux et une horloge à la mauvaise place](/blog/trois-cartes-deux-cerveaux-une-horloge/).
La mesure elle-même est montrée pour vrai dans
[L'heure dans le prompt, pour vrai](/casts/l-heure-dans-le-prompt-prise-reelle/).
