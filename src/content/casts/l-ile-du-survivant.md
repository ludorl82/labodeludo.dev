---
title: "L'île du survivant, débranchée pour vrai"
pubDate: 2026-08-05
description: "Le dernier test de débranchement du labo : la fiche tirée, la cascade d'arrêts qui part sur le signal de l'onduleur, un BMC égaré sur le mauvais VLAN, et le verrou qui clôt la panne tout seul."
cast: "/casts/survivor-island.cast"
poster: "npt:0:06"
caption: "Le dernier test de traction : cascade, BMC égaré, réparation in-band, et le verrou qui clôt la panne tout seul."
article: "l-ile-du-survivant"
frame: "none"
type: "reconstitution"
disclaimer: "⚠ Ceci n'est pas une capture en direct : reconstitution condensée à partir de la transcription réelle de la session (2026-08-05). Les invites sont textuelles, les temps d'attente sont compressés, et les noms d'hôtes et adresses sont fictifs."
---

Trois jours de pannes électriques, puis quatre débranchements volontaires pour
vérifier ce qui devait survivre à tout le reste : le routeur, le modem et un
seul Raspberry Pi, sur l'onduleur le moins chargé.

Cette session est la dernière des quatre. La cascade d'arrêts part sur le signal
natif de l'onduleur, le classificateur de permissions interrompt l'agent au
passage, et le réveil par IPMI bute sur un BMC qui n'est pas sur le VLAN où on
le cherche. La réparation se fait in-band, et la panne se referme d'elle-même
quand le verrou constate le retour du courant.
