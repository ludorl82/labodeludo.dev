---
title: "La chaîne de nuit qui mentait"
pubDate: 2026-09-16
description: "Une journée sur le pipeline de nuit, et trois statuts verts qui disaient « tout va bien » pour une raison sans rapport avec le travail : une copie périmée qui réussissait, un refus de l'API lu comme un accord, un shell qui sortait à zéro sans rien exécuter."
cast: "/casts/la-chaine-de-nuit-qui-mentait.cast"
poster: "npt:1:43"
caption: "Le fil d'une journée : la garde qui n'avait jamais tourné, la carte graphique que personne n'avait comptée, le delta, le refus de l'API rapporté « déjà conforme », puis une ligne de .bashrc qui empêchait toutes les jobs de démarrer. L'agent s'arrête deux fois, et se corrige une fois."
frame: "none"
type: "reconstitution"
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle de la session du 16 septembre 2026. Les demandes de Ludo sont citées mot pour mot, fautes comprises; les sorties d'outils sont réécrites et raccourcies, le minutage est compressé et les noms sont sanitisés."
article: ["ce-que-coute-une-nuit-de-pipeline", "la-job-etait-verte"]
---

Tout part d'une question suggérée sous le chat du site, qui mène à un refus.
La garde censée l'empêcher existait dans le dépôt, mais elle n'avait jamais
tourné : le planificateur exécutait une copie du script faite à la main, vieille
de trois jours. La job était verte. Elle roulait le code du dimanche précédent.

La suite de la journée répète le même motif. Une session de relecture est
refusée par le filtre de contenu de l'API en douze secondes, le programme sort
à zéro, et le pilote rapporte « déjà conforme aux dépôts » ; le delta tout neuf
enregistre même ce passage comme point de départ. Le soir, chaque job lancée
par le planificateur meurt avec le code 70, parce que le bash de Debian lit
`~/.bashrc` sous ssh et que ce fichier fait `exec zsh` à sa troisième ligne.

Deux arrêts de l'agent sont gardés : une écriture refusée qui attend le feu vert
de Ludo, et une proposition de « mesurer d'abord » que Ludo écarte, les temps
étant déjà dans les transcriptions. Une correction aussi : l'optimisation
annoncée comme le gros levier n'en était pas un, les chiffres l'ont montré.

Les tableaux de coûts, session par session, sont dans
[Ce que coûte une nuit de pipeline](/blog/ce-que-coute-une-nuit-de-pipeline/) ;
le détail de la plomberie, dans
[Ma job était verte](/blog/la-job-etait-verte/).
