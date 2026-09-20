#!/usr/bin/env bash
# Monte le plateau d'une PRISE RÉELLE asciinema et lance le recorder.
#
#   scripts/cast-stage.sh <nom-du-cast> <fichier-de-sortie.cast> [cols] [rows] [dépôt à cloner]
#
# Ce que ça fait, dans cet ordre (l'ordre est la moitié de la leçon) :
#   1. session tmux `cast` sur le socket nommé -L console, taille FIXÉE
#      (window-size manual + resize) — sinon tmux la calque sur le dernier
#      client attaché et le recorder lit la mauvaise géométrie ;
#   2. deux panneaux : commandes en haut, un suivi (get pods -w…) en bas ;
#   3. la fenêtre porte le nom du cast, automatic-rename off ;
#   4. la barre tmux et le prompt affichent « ludo » (le nom court du site),
#      réglés ICI, avant la prise — jamais substitués après, une substitution
#      qui change la longueur d'un mot casse le calcul du curseur de zsh ;
#   5. le recorder dans un pty de taille fixe ATTACHÉ à la session
#      (cast-rec-attach.py), pour que la barre tmux soit dans l'image.
# Ludo s'attache ensuite avec `tmux switch-client -t cast` (ou prefix s) et
# joue. `exit` dans les deux panneaux ferme la session et arrête le recorder.
set -eu
name="${1:?nom du cast}"; out="${2:?fichier .cast}"; cols="${3:-96}"; rows="${4:-26}"; repo="${5:-}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Dépôt de travail : un clone JETABLE directement sous ~/<nom>, sur master,
# pour que l'invite reste courte (« ludo@labo:~/cloudflare-iac$ ») et que rien ne touche l'arbre de travail réel
# (~/git/ludorl82/…). Refuse d'écraser un dossier existant ; à effacer après.
cwd="$HOME"   # sans dépôt : l'invite est « ludo@labo:~$ » tout court
if [ -n "$repo" ]; then
  cwd="$HOME/$(basename "$repo" .git)"
  [ -e "$cwd" ] && { echo "existe déjà, je n'écrase pas : $cwd" >&2; exit 1; }
  git clone -q "$repo" "$cwd" && git -C "$cwd" checkout -q master
fi
T=(tmux -L console)
pane_rows=$((rows - 1))   # la barre prend une ligne du pty du recorder
"${T[@]}" kill-session -t cast 2>/dev/null || true
# CAST_ENV="VAR=valeur VAR2=valeur" : variables poussées dans la session tmux,
# donc dans les deux shells, sans être tapées à l'écran (ex. LAB_HOST_MAP pour
# un clone qui n'a plus ses dépôts frères).
envargs=(); for kv in ${CAST_ENV:-}; do envargs+=(-e "$kv"); done
"${T[@]}" new -d -s cast "${envargs[@]}" -x "$cols" -y "$pane_rows" -c "$cwd"
"${T[@]}" set -t cast window-size manual
"${T[@]}" resize-window -t cast -x "$cols" -y "$pane_rows"
# Disposition, de haut en bas : les COMMANDES, un panneau de suivi optionnel
# (CAST_WATCH=1 : un `get pods -w` qui montre l'effet en direct), et le
# panneau de NARRATION, réservé au texte — ni invite ni commande, voir
# cast-narrate.sh. Ludo, 2026-09-20 : « on peut garder le panneau du bas pour
# la narration ».
if [ "${CAST_WATCH:-0}" = 1 ]; then
  # `-l` donne la taille du NOUVEAU panneau, et le second split porte sur le
  # panneau qui vient de naître : 13 d'abord (8 + 4 + la séparatrice), puis 4.
  "${T[@]}" split-window -v -l 13 -t cast -c "$cwd"
  "${T[@]}" split-window -v -l 4 -t cast -c "$cwd"
else
  "${T[@]}" split-window -v -l 5 -t cast -c "$cwd"
fi
win="$("${T[@]}" display -p -t cast '#{window_index}')"
"${T[@]}" rename-window -t "cast:$win" "$name"
"${T[@]}" set -t "cast:$win" automatic-rename off
sl="$("${T[@]}" show -gv status-left)"
"${T[@]}" set -t cast status-left "$(printf '%s' "$sl" | sed 's/#(whoami)/ludo/')"
for p in $("${T[@]}" list-panes -t "cast:$win" -F "#{pane_index}"); do
  "${T[@]}" send-keys -t "cast:$win.$p" " source $here/cast-prompt-ludo.zsh; clear" Enter
done
"${T[@]}" select-pane -t "cast:$win.1"
sleep 2
for p in $("${T[@]}" list-panes -t "cast:$win" -F "#{pane_index}"); do
  line="$("${T[@]}" capture-pane -p -t "cast:$win.$p" | grep -v '^\s*$' | head -1)"
  case "$line" in *"ludo@labo:"*) ;; *) echo "panneau $p : invite inattendue : $line" >&2; exit 1;; esac
done
nohup python3 "$here/cast-rec-attach.py" "$cols" "$rows" "$out" >/tmp/cast-rec-attach.log 2>&1 &
echo $! > /tmp/cast-rec.pid
sleep 3
if grep -q "$(whoami)" "$out"; then echo "le recorder voit encore $(whoami) : abandon" >&2; kill "$(cat /tmp/cast-rec.pid)"; exit 1; fi
echo "plateau prêt : session cast ($cols x $rows, fenêtre $name, dossier $cwd), recorder pid $(cat /tmp/cast-rec.pid) → $out"
echo "Ludo : tmux switch-client -t cast  ·  fin : exit dans les deux panneaux"
