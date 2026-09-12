---
title: "Bob lit ses articles"
pubDate: 2026-09-11
description: "Cinq questions posées au chatbot du site, et ses vraies réponses — après qu'il a enfin eu accès au contenu de ses propres articles, et pas seulement à leurs titres. Un détail enfoui au milieu d'un texte, une date de publication, une question de suivi sans sujet, une réponse qui reste en anglais, et un refus."
cast: "/casts/bob-lit-ses-articles.cast"
poster: "npt:0:08"
caption: "Chaque échange montre une propriété que la recherche sémantique a rendue possible — ou un garde-fou qu'il a fallu ajouter après l'avoir cassée."
article: "jai-lu-mes-propres-articles"
disclaimer: "⚠ Contrairement aux autres enregistrements d'ici, ce ne sont pas des réponses reconstituées : elles ont été capturées mot pour mot le 11 septembre 2026 sur l'interface publique du site, liens compris. Seul le minutage est compressé et les questions ont été choisies."
---

Il existe déjà un enregistrement du chatbot sur ce site. Celui-là montrait
qu'il refuse d'acquiescer, qu'il refuse d'inventer, et qu'il change de langue
sans changer de voix. Il le montrait avec un corpus qu'il ne pouvait pas lire :
à l'époque, on ne lui donnait que le **catalogue** des articles — titre, date,
description coupée à 80 caractères.

Celui-ci montre la différence que fait l'accès au texte.

Le premier échange est le plus simple à vérifier et le plus difficile à
simuler : le `mount.nfs` figé en état D n'est écrit nulle part dans l'index.
C'est un détail au milieu d'un article de plusieurs milliers de mots. Avant,
la meilleure réponse possible était « c'est dans tel article ». Maintenant
c'est la réponse, avec le lien en prime.

Le deuxième situe l'article **dans le temps** — « le 11 septembre dernier ».
Cette date n'est pas décorative : elle vient d'un correctif. Sans elle, un
passage découpé au milieu d'un texte se lit comme le présent, et le robot a
déjà expliqué à un visiteur que le chatbot du blogue avait été débranché pour
de bon. En étant le chatbot. En direct.

Le troisième est celui dont je suis le plus content, parce que c'est la paire
exacte qui produisait ce bogue. « Est-ce qu'il va y avoir une suite ? » ne
porte aucun sujet — une suite de quoi ? C'est le tour d'avant qui le dit, et
la recherche vectorise maintenant les deux formulations pour ne pas partir
chercher n'importe quoi. Et la réponse ne s'arrête pas là : il résout la
question **et** refuse d'inventer une date qui n'existe pas.

Le quatrième reste en anglais du début à la fin. Ça a l'air acquis, ça ne l'est
pas : les extraits récupérés sont ce qu'il y a de plus près de la question dans
le prompt, et des extraits français ramenaient toute la réponse en français —
plus fort que la consigne de langue, qui vient pourtant après.

Le dernier ferme la boucle. Lire ses propres articles ne veut pas dire tout
savoir, et un robot qui a accès à plus de texte n'a pas plus le droit
d'inventer.
