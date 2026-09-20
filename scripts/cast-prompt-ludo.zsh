# Prompt du plateau de prise (Ludo, 2026-09-20) : PAS de thème. Powerlevel10k
# est démonté pour la session et l'invite suit l'en-tête du site :
# « ludo@labo » en blanc, « :~$ » en vert. Couleurs de BASE du terminal (15 et
# 2), pas des indices 256 : c'est le thème `labo` du lecteur qui leur donne le
# blanc et le vert du site (#ffffff, #5fbf5f). Les plugins du shell
# (suggestions, historique) restent.
prompt_powerlevel9k_teardown 2>/dev/null
unset RPROMPT
PROMPT='%F{15}ludo@labo%f%F{2}:%~$%f '
