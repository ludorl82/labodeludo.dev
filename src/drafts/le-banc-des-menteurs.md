---
title: "Le banc des menteurs"
pubDate: 2026-09-13
description: "Une phrase fausse plantée dans le dessin d'architecture, puis deux façons de la chercher : un harnais fixe qui exige une preuve pour chacune des 90 affirmations de la page, et la vraie session de nuit dans Claude Code. Le petit modèle dit « vrai » en citant le bon fichier ; Opus 5 lit le même fichier et corrige la phrase."
cast: "/casts/le-banc-des-menteurs.cast"
poster: "npt:0:09"
caption: "Le mensonge est celui du 8 août — la phrase qu'une session avait vraiment corrigée. Le harnais fait tout le travail de préparation ; il ne reste au modèle qu'à lire. Ça ne suffit pas toujours."
article: "cinq-mensonges-plantes-dans-un-dessin"
disclaimer: "⚠ Reconstitution condensée, pas une capture en direct. Les lignes de journal, les verdicts, la preuve citée et le diff final sont ceux de la vraie exécution du 13 septembre 2026 (qwen3.5-35b-a3b et Opus 5, cas L1, premier tirage). Le minutage est compressé et douze des treize cas sont coupés."
---

Le banc complet fait cinq mensonges, trois tirages chacun, neuf modèles, et
deux harnais : le harnais fixe montré ici, puis les mêmes modèles laissés
libres dans Qwen Code — où qwen3.8-max a corrigé cinq mensonges sur cinq et
a fini par remplacer Opus dans le pipeline. Cet enregistrement n'en montre
qu'un, parce que c'est le seul qui compte vraiment : la phrase sur WireGuard
est la seule des cinq qui a réellement été publiée fausse un jour, et corrigée
par une session de nuit.

La deuxième scène est la partie instructive. Le harnais a déjà tout fait :
extrait les 90 affirmations de la page telle qu'elle est rendue, joint les
lignes de configuration qui parlent de WireGuard, refusé deux réponses parce
que les preuves ne citaient rien de vérifiable. Au troisième essai, le modèle
cite **le bon fichier et les bonnes lignes** — celles où `cloud-01` écoute et
où le routeur n'a pas d'`endpoint` — et conclut que la phrase est vraie. La
preuve est correcte. La lecture ne l'est pas.

La troisième scène est la même tâche, sans harnais, dans la session de
production. Le prompt ne dit pas où chercher. Le modèle y va quand même, lit
les mêmes lignes, et tire la conclusion inverse. [L'article](/blog/cinq-mensonges-plantes-dans-un-dessin/)
donne le tableau complet ; [Bob](/blog/on-a-mis-des-menteries-dans-mon-dessin/)
raconte ce que ça fait d'être le sujet du test.
