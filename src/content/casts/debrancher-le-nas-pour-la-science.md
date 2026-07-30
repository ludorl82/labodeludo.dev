---
title: "Débrancher le NAS pour la science"
pubDate: 2026-07-30
description: "Trois coupures de courant volontaires du NAS pour vérifier des sondes de vivacité fraîchement posées. Chaque coupure trouve quelque chose que la précédente avait manqué — et la dernière est ennuyante, ce qui était le but."
cast: "/casts/nas-pull-the-plug.cast"
poster: "npt:0:08"
caption: "Les trois coupures, condensées : les sondes qui mentent encore, la boucle de crash de Loki, le garde-fou de permissions au milieu de la réparation, et la course propre à la fin."
disclaimer: "⚠ Ceci n'est pas une capture en direct : c'est une reconstitution condensée, montée après coup à partir de la transcription réelle de la session. Les demandes et les messages d'arrêt sont ceux de la vraie session; le minutage est compressé et les longues boucles de surveillance sont coupées. Noms d'hôte sanitisés."
article: "debrancher-le-nas-pour-la-science"
---

Des workloads k3s restés `Running` avec leur stockage NFS mort en dessous —
des zombies que rien ne signalait. La session pose des sondes de vivacité
partout, puis les vérifie de la seule manière honnête : en tirant la fiche du
NAS. Trois fois.

Ce qui rend l'enregistrement intéressant, c'est la progression : la première
coupure montre trois sondes qui mentent encore (un `/ready` servi depuis la
mémoire, des `ls` répondus par le cache d'attributs NFS). La deuxième réveille
un bogue que l'ancienne configuration masquait — la boucle de crash WAL de
Loki, régénérée à chaque redémarrage par le *silly-rename* NFS. Et au milieu
de la réparation, le classificateur de permissions bloque le `mv` sur le
volume de données, pendant la panne : le garde-fou fait exactement sa job, au
moment exact où on aimerait qu'il se taise.

La troisième coupure ne trouve rien. C'était le but.
