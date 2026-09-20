# Prompt du plateau de prise (Ludo, 2026-09-20) : PAS de thème. Powerlevel10k
# est démonté pour la session et l'invite redevient la forme classique
# « ludo@labo:~/git/cloudflare-iac$ », au branding du site, deux couleurs de la
# palette maison (vert 114, bleu 153). Les plugins du shell (suggestions,
# historique) restent.
prompt_powerlevel9k_teardown 2>/dev/null
unset RPROMPT
PROMPT='%F{114}ludo@labo%f:%F{153}%~%f$ '
