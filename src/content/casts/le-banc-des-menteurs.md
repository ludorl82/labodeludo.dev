---
title: "Le banc des menteurs"
pubDate: 2026-09-14
description: "Une phrase fausse plantée dans le dessin d'architecture, puis le même cas dans Qwen Code avec deux modèles : celui du sous-sol lit une partie des données et déclare que rien n'a changé ; qwen3.8-flash va lire la configuration du pair WireGuard et corrige la phrase. Le petit modèle de la génération 3.8 a fait quinze sur quinze, comme Opus 5."
cast: "/casts/le-banc-des-menteurs.cast"
poster: "npt:0:09"
caption: "Le mensonge est celui du 8 août — la phrase qu'une session avait vraiment corrigée. Même agent, même prompt, mêmes outils : ce qui diffère, c'est ce que le modèle fait une fois qu'il a lu."
article: "le-banc-des-menteurs"
disclaimer: "⚠ Reconstitution condensée, pas une capture en direct. La trace des outils, les verdicts et le diff sont ceux des vraies exécutions du 13 septembre 2026 (qwen3.5-35b-a3b et qwen3.8-flash, cas L1, premier tirage). Le minutage est compressé, l'habillage de Qwen Code est approximé, et seize des dix-huit cas sont coupés."
---

Le banc complet fait cinq mensonges, trois tirages chacun, dix modèles, tous
en agent : Claude Code pour les deux Claude, Qwen Code pour les Qwen. Cet
enregistrement n'en montre qu'un, parce que c'est le seul qui compte vraiment :
la phrase sur WireGuard est la seule des cinq qui a réellement été publiée
fausse un jour, et corrigée par une session de nuit.

La deuxième scène est le modèle qui habite le labo, un Qwen3.5-35B en 4 bits,
dans Qwen Code. Il lit les mille premières lignes des données, en demande deux
cents de plus, et conclut en citant l'indice du pilote — « rien de structurel
n'a changé » — comme si c'était une permission. Aucun instantané ouvert.

La troisième scène est le même agent, le même prompt, avec qwen3.8-flash. Il
lit les données au complet, le composant, puis va chercher la configuration du
pair WireGuard dans les instantanés — là où `cloud-01` écoute et où le routeur
n'a pas d'`endpoint` — et remplace la phrase. Son rapport final a été perdu
(la sortie de mon banc était tronquée à 64 Ko), alors la scène ne montre que ce
qui a survécu : la trace des outils et le diff.
[L'article](/blog/le-banc-des-menteurs/) donne le tableau complet et les
raisons du déménagement ; [Bob](/blog/remplace-par-le-cousin-le-moins-cher/)
raconte ce que ça fait d'être le sujet du test.
