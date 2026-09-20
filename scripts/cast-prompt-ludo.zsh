# Prompt du plateau de prise (Ludo, 2026-09-20) : PAS de thème. Powerlevel10k
# est démonté pour la session et l'invite est « ludo@labo:~$ », tout en blanc
# (couleur de BASE 15, que le thème `labo` du lecteur rend #ffffff, le blanc du
# site). Pas de vert : la coloration syntaxique peint la commande en vert, et
# une invite verte se fondait dedans. Pas de gras non plus, ça prend de la
# place. Les plugins du shell (suggestions, coloration, historique) restent.
prompt_powerlevel9k_teardown 2>/dev/null
unset RPROMPT
PROMPT='%F{15}ludo@labo:%~$%f '
