#!/usr/bin/env bash
# Mesure ce que le modèle relit quand une ligne change dans son prompt.
#
#   scripts/voice/mesure-prefixe.sh haut       # l'heure en TÊTE du prompt système
#   scripts/voice/mesure-prefixe.sh bas        # l'heure en QUEUE du prompt système
#   scripts/voice/mesure-prefixe.sh question   # l'heure dans la QUESTION
#   scripts/voice/mesure-prefixe.sh journal    # ce que llama-server dit avoir relu
#   (top et end, en anglais, valent haut et bas)
#
# Trois questions de suite, le même prompt chaque fois, sauf l'heure à la
# seconde. Ollama (llama.cpp) ne réutilise que le plus long PRÉFIXE commun avec
# la requête précédente, et sur un modèle hybride (Qwen3.5 et suivants), il ne
# peut reprendre qu'à un point de contrôle pris AVANT la première différence :
# au début du message de l'utilisateur, ou 4 et 4 + n_ubatch jetons avant la
# fin du prompt (1 028, avec le n_ubatch de 1 024 que règle Ollama).
#
# Le temps affiché vient de l'API (prompt_eval_duration). Le NOMBRE de jetons
# relus, lui, n'y est pas : Ollama 0.34 renvoie toujours la taille complète du
# prompt dans prompt_eval_count. Le mode « journal » le lit à la source, dans le
# journal de llama-server : à lancer dans un autre terminal, sur l'hôte
# d'Ollama, ou d'ailleurs avec OLLAMA_HOTE=<hôte> (par ssh).
#
# MESURE_LANGUE=en affiche les messages en anglais (le prompt reste le même).
#
# Le prompt est fait des parties publiques de celui de la voix : la persona de
# Bob et les règles vocales. Le vrai ajoute la liste des appareils de la maison.
#
# Les options reprennent celles de la prod (même num_ctx, keep_alive -1) : une
# autre valeur ferait recharger le modèle, ou réarmerait son minuteur de
# déchargement, pour tout le monde.
set -euo pipefail

OU=${1:-haut}
case $OU in top) OU=haut ;; end) OU=bas ;; esac
OLLAMA=${OLLAMA:-http://localhost:11434}
MODELE=${MODELE:-qwen38-27b:latest}
ICI=$(cd "$(dirname "$0")" && pwd)
EN=$([ "${MESURE_LANGUE:-fr}" = en ] && echo 1 || true)

if [ "$OU" = journal ]; then
  suivre=(journalctl -u ollama -f -n 0 -o cat)
  [ -n "${OLLAMA_HOTE:-}" ] && suivre=(ssh -n "$OLLAMA_HOTE" "${suivre[@]}")
  relus=$([ -n "$EN" ] && echo 'tokens re-read' || echo 'jetons relus')
  "${suivre[@]}" |
    grep --line-buffered 'prompt eval time' |
    sed -u -E "s/.*prompt eval time = *[0-9.]+ ms \/ *([0-9]+) tokens.*/llama-server : \1 $relus/"
  exit
fi

PROMPT=$(cat "$ICI/../../src/data/bob-persona.md" "$ICI/voice-rules.txt")
QUESTION="Quel jour on est ?"

question() {
  local heure systeme demande
  heure="Il est $(date +%H:%M:%S)."
  systeme=$PROMPT demande=$QUESTION
  case $OU in
    haut)     systeme="$heure"$'\n\n'"$PROMPT" ;;
    bas)      systeme="$PROMPT"$'\n\n'"$heure" ;;
    question) demande="$heure $QUESTION" ;;
    *)        echo "usage : $0 haut|bas|question|journal (top|end en anglais)" >&2; exit 2 ;;
  esac
  jq -n --arg m "$MODELE" --arg s "$systeme" --arg q "$demande" '{
      model: $m, stream: false, think: false, keep_alive: -1,
      options: { num_ctx: 16384, num_predict: 1 },
      messages: [ { role: "system", content: $s },
                  { role: "user",   content: $q } ] }' |
    curl -sf "$OLLAMA/api/chat" -d @-
}

if [ -n "$EN" ]; then
  case $OU in
    haut)     echo "the time at the top of the system prompt" ;;
    bas)      echo "the time at the end of the system prompt" ;;
    question) echo "the time in the question" ;;
  esac
  ligne='"  question \($i): prompt read in " + $s + " s"'
else
  case $OU in
    haut)     echo "l'heure en tête du prompt système" ;;
    bas)      echo "l'heure à la fin du prompt système" ;;
    question) echo "l'heure dans la question" ;;
  esac
  ligne='"  question \($i) : prompt lu en " + ($s | sub("\\."; ",")) + " s"'
fi
for i in 1 2 3; do
  question | jq -r --arg i "$i" \
    "((.prompt_eval_duration / 1e7 | round) / 100 | tostring) as \$s | $ligne"
  sleep 2
done
