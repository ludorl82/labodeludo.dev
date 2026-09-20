#!/usr/bin/env bash
# Narration d'une prise, dans un panneau qui lui est réservé.
#
#   scripts/cast-narrate.sh open  <cible tmux>   → le panneau n'affiche plus que
#       la narration : ni invite, ni commande. (Un tube nommé + `cat` en boucle,
#       lancé puis effacé de l'écran.)
#   scripts/cast-narrate.sh say   <texte>        → une ligne, en gris pâle (246,
#       le « dim » de la palette maison), qui apparaît d'un coup : on lit une
#       phrase, on ne la regarde pas s'écrire.
#   scripts/cast-narrate.sh close               → ferme le tube.
set -eu
F=/tmp/cast-narration
case "${1:?open|say|close}" in
  open)
    rm -f "$F"; mkfifo "$F"
    # `clear` fait partie de la commande : il efface l'invite et la commande
    # elles-mêmes. Surtout pas de C-l après, il tomberait dans l'entrée du
    # `cat` et s'afficherait en « ^L ».
    tmux -L console send-keys -t "${2:?cible}" "clear; while :; do cat $F; done" Enter
    sleep 1.5 ;;
  say)
    printf '\033[38;5;246m  %s\033[0m\n' "${2:?texte}" > "$F" ;;
  close)
    tmux -L console send-keys -t "${2:?cible}" C-c 2>/dev/null || true
    rm -f "$F" ;;
esac
