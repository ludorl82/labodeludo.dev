---
name: cast
description: "Enregistrer POUR VRAI un asciicast pour labodeludo.dev (pas une reconstitution) : monter le plateau tmux, laisser Ludo jouer, assainir et vérifier à l'écran, intégrer au site, ouvrir la PR. À charger dès qu'on parle d'enregistrer, refaire ou publier un cast. Pour le LOOK (palette, grammaire de la TUI, disclaimer, canal asciinema.org), c'est net-cfgs/asciicast-style.md qui fait foi."
---

# Un cast enregistré pour vrai

Chaîne gelée le 2026-09-20 après dix prises pour « Un pod stateless change de
noeud, pour vrai ». Elle vaut pour les casts de PROCÉDURE, rejouables à
volonté. Les casts d'incidents restent des reconstitutions (`mkcast-*.py`),
avec leur disclaimer, parce qu'on ne rejoue pas un BIOS invisible.

Les faits qui ne bougent pas — palette, grammaire de la TUI, honnêteté,
publication sur asciinema.org — vivent dans `net-cfgs/asciicast-style.md`.
Ce skill ne les répète pas ; il dit dans quel ordre faire les gestes et
pourquoi chaque ordre a été appris.

## 0. Avant de monter quoi que ce soit

- **Décision de Ludo (2026-09-20) : les interactions avec Claude Code GARDENT
  leur reconstitution.** La vraie prise sert à montrer la console — barre
  tmux, prompt, suggestions, deux panneaux, vrai chronomètre. Donc du shell
  pur : un mécanisme qu'on rejoue, jamais une session qu'on rejouerait.
- **Choisir un scénario dont la commande mesure elle-même.** `time (kubectl
  rollout restart … && kubectl rollout status …)` donne le chiffre ; `kubectl
  wait -l` attrape aussi le pod qui meurt et sort en erreur. Stratégie
  Recreate = la séquence d'une éviction.
- **Un asciicast ne voit que le terminal.** Un geste fait ailleurs (bouton
  Home Assistant, widget web) n'y sera jamais : c'est une vidéo, pas un cast.
- **Vérifier l'état de départ ET le remettre entre les prises** (pod sur le
  bon noeud, rien de cordonné). Chaque prise ratée laisse le cluster ailleurs.
- **Ne jamais coller un `clear` derrière une ligne à moitié tapée** : ça
  fabrique une entrée d'historique (« cordon bobclear ») que la suggestion
  automatique resservira à Ludo à la prise suivante. `C-c` d'abord, `clear`
  ensuite ; et purger `~/.histfile` si c'est arrivé.

## 1. Le plateau

```bash
scripts/cast-stage.sh <nom-du-cast> <prise.cast> [96] [26] [dépôt à cloner]
```

Avec un dépôt en cinquième argument, le script le clone JETABLE directement
sous `~/<nom>` sur master et y ouvre les deux panneaux : l'invite reste
courte (« ludo@labo:~/cloudflare-iac$ »), rien ne touche l'arbre réel sous
`~/git/ludorl82/`, et on efface le clone après la prise. Un clone n'a plus ses dépôts frères :
ce que le script attend d'eux se passe par `CAST_ENV="VAR=valeur"` (poussé
dans la session tmux, jamais tapé), par exemple `LAB_HOST_MAP` pour les
scripts d'assainissement — sinon leur message d'erreur imprime un chemin
complet avec le vrai nom d'utilisateur, et la prise est bonne à jeter. Le prompt du plateau est SANS thème : p10k est démonté pour la session et
l'invite redevient « ludo@labo:~/cloudflare-iac$ », au branding du site
(Ludo, 2026-09-20 : « retire les thèmes que j'utilise pour l'enregistrement »).

Le script fait, dans l'ordre : session `cast` sur `-L console` à taille
FIXÉE (`window-size manual` + `resize-window` AVANT le recorder, sinon tmux
la calque sur le dernier client attaché et le cast sort en 137×40) ; deux
panneaux (commandes en haut, suivi en bas) ; fenêtre nommée comme le cast ;
invite SANS thème (`cast-prompt-ludo.zsh` démonte p10k et pose
`ludo@labo:~$`, deux couleurs de la palette ; `#(whoami)` devient « ludo »
dans `status-left` de la session) ;
recorder `asciinema rec --idle-time-limit 2` dans un pty de taille fixe
ATTACHÉ à la session (`cast-rec-attach.py`), pour que la barre tmux soit dans
l'image. Sans dépôt en argument, les panneaux s'ouvrent dans `~` et l'invite est
`ludo@labo:~$` tout court. Il refuse de continuer si une invite ne dit pas
« ludo@labo: » ou si le recorder voit le vrai nom d'utilisateur.

asciinema vient de `python3 -m pip install --user --break-system-packages
asciinema` sur la console (le pip nu est refusé, « externally-managed »).

## 2. La prise : Ludo au clavier, moi en régie — ou moi au clavier

Deux modes. Ludo tape (le pod stateless), ou je tape à sa place avec
`scripts/cast-type.sh <cible tmux> <ligne>` (la vérification qui refuse de
publier) : un caractère à la fois à 45–115 ms, puis Entrée, la cadence des
reconstitutions. Alors le disclaimer le dit : « frappes envoyées par script,
pas tapées par Ludo ; commandes et sorties réelles ». Quand je tape, la
prise entière tient dans UNE commande Bash avec des `sleep` entre les
étapes ; faire une répétition d'abord, elle révèle ce que l'invite montre
(branche du clone, chemin) et ce que les sorties impriment. Rejouer sur une
COPIE du dépôt (le cinquième argument de `cast-stage.sh`), jamais dans l'arbre
de travail, et ne jamais `ls` un dossier dont les noms de fichiers sont
sensibles (les zones DNS portent les vrais domaines).


Ludo bascule avec `tmux switch-client -t cast` (ou `prefix s`). Lui donner le
déroulement en clair : quoi lancer en bas, les commandes en haut dans l'ordre
(l'historique est là, les flèches marchent), puis `C-c`/`exit` en bas et
`exit` en haut — la session se ferme, le recorder s'arrête tout seul.

Entre deux prises : arrêter le recorder par son pid (`/tmp/cast-rec.pid`),
JAMAIS `pkill -f rec-attach` — le motif matche le shell qui le lance et tue
la session de Claude (rc 144). Puis remettre l'état de départ, puis relancer
`cast-stage.sh`. Garder chaque prise (`take<N>.cast`) : la bonne est souvent
une prise antérieure.

## 3. Assainir, et vérifier à l'ÉCRAN

```bash
CAST_SUBS='[["<id-du-conteneur>","console-labo"]]' \
  python3 scripts/sanitize-cast.py <prise.cast> public/casts/<slug>.cast
```

Ce que le script fait : coupe avant le premier `clear` puis avant la première
vraie frappe ; fond les suites où seule la barre tmux change (son horloge bat
chaque seconde et défait `--idle-time-limit`) en 2 s ; préfixe le préambule
maison (« Prise réelle — pas une reconstitution … ») ; applique `CAST_SUBS` ;
puis **rejoue le cast dans pyte et refuse (rc 1) si un motif interdit est à
l'écran à un moment quelconque**. Le grep sur le fichier ne prouve rien : zsh
émet les lettres une à une entre séquences d'échappement.

Règles de substitution, apprises à la dure :
- **même longueur seulement** (`dae8265a7fd2` → `console-labo`, 12 pour 12).
  Une longueur qui change dans une ligne éditée décale le curseur de zsh
  (« kubkubectl ») et laisse des restes de suggestion (« gamgamgpu ») ;
- **bob et stella restent publics** (décision de Ludo 2026-09-20 : ce sont les
  chiens, bob l'est déjà) — donc pas de substitution dans le texte tapé ;
- ce qui doit changer se règle AVANT la prise (prompt, barre), pas après.

Relire dans un vrai terminal, pas seulement dans pyte :
`tmux -L console new -d -s play -x 96 -y 26` + `asciinema play -s 8`, puis
`capture-pane -p -S -200` (pyte et tmux ont toujours montré la même chose,
mais la relecture coûte 25 s).

## 4. Intégrer au site

- `public/casts/<slug>.cast` ; page `src/content/casts/<slug>.md` avec
  `session: "aucune"`, **`frame: "none"`** (la vraie barre tmux est dans
  l'enregistrement : l'habillage du composant en ferait une deuxième), un
  `poster` à l'instant du résultat (`npt:m:ss`), et un disclaimer INVERSÉ
  (« ✔ capture réelle … seules les pauses de plus de deux secondes sont
  raccourcies ») — le schéma exige le champ, la maison exige la vérité.
- Dans l'article, FR et EN : `<AsciiCast src=… frame="none" …/>`. Si le cast
  remplace une reconstitution, la reconstitution garde sa page et l'article
  y renvoie pour ce qu'une vraie prise ne peut plus montrer (l'« avant »).
- Le lecteur reçoit la police Nerd Font du site (`terminalFontFamily`) et les
  seize couleurs de base d'Alacritty (thème `labo`) : sans ça, icône de
  dossier en rectangle vide et prompt en gris.
- `npm run build`, PR vers `dev` (le staging ne se construit QUE depuis
  `dev`), Ludo relit sur dev.labodeludo.dev, puis PR `dev → main`.
- L'upload sur asciinema.org reste le geste de Ludo (compte, visibilité).

## 5. Avant de livrer, vérifier

- [ ] `sanitize-cast.py` rc 0, « écran : PROPRE », vrai nom d'utilisateur et
      identifiant du conteneur absents du flux.
- [ ] Le récit complet est à l'écran (chaque commande ET sa sortie) — une
      prise où le cordon manque a l'air bonne et ne l'est pas.
- [ ] Géométrie de l'en-tête = celle demandée ; durée sans trou de plus de 2 s.
- [ ] Cluster remis dans l'état de départ, session `cast` fermée.
- [ ] Disclaimer inversé, `frame: "none"`, poster au bon instant, FR et EN.
