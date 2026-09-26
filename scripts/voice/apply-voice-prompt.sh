#!/usr/bin/env bash
# Render Bob's voice prompt and compare it to, or install it into, Home Assistant.
#
#   apply-voice-prompt.sh --check   exit 1 if HA's prompt differs from the render
#   apply-voice-prompt.sh --apply   stop HA, write the prompt, start HA, verify
#
# HA keeps the Ollama conversation prompt in /config/.storage/core.config_entries
# and rewrites that file on shutdown, so an edit while it runs is overwritten:
# the only safe order is stop, edit, start. The trap restarts HA even if this
# script dies mid-way — a stop with no start left the house without automation
# for five minutes once (2026-09-12). automatron has jq and no python.
#
# The stored prompt ends with exactly one newline, and so does the render:
# --rawfile keeps it, and nothing trims it, so --apply reproduces the stored
# value byte for byte. A first version stripped it and every apply would have
# rewritten the entry for a newline nobody could see.
set -euo pipefail
cd "$(dirname "$0")/../.."
HOST="${HA_HOST:-automatron}"
STORE=/config/.storage/core.config_entries
# Only Bob's Ollama entry, the one on bob. Since 2026-09-26 there is a second
# Ollama entry: the office Voice PE's bridge to the console's `qwen` tmux
# session (nixos-iac, qwen-voice-bridge.py). Its prompt is empty on purpose —
# the bridge forwards only the last sentence — so reading every entry turned
# the check red, and --apply would have written Bob's prompt into it.
BOB='select(.domain=="ollama" and (.data.url | startswith("http://bob.tptpt.in:")))'
JQ_READ='.data.entries[] | '"$BOB"' | .subentries[] | select(.subentry_type=="conversation") | .data.prompt'
render=$(mktemp); trap 'rm -f "$render"' EXIT
node scripts/voice/render-voice-prompt.mjs > "$render"

case "${1:-}" in
  --check)
    live=$(ssh "$HOST" "jq -r '$JQ_READ' $STORE")
    if diff -u <(printf '%s\n' "$live") "$render" >/dev/null; then
      echo "voice prompt: live matches src/data/bob-persona.md + voice-rules.txt"
    else
      echo "voice prompt: DRIFT between Home Assistant and the rendered prompt" >&2
      diff -u <(printf '%s\n' "$live") "$render" >&2 || true
      exit 1
    fi ;;
  --apply)
    scp -q "$render" "$HOST:/config/.bob-voice-prompt.txt"
    ssh "$HOST" 'set -e
      trap "ha core start --no-progress >/dev/null 2>&1 || true" EXIT
      ha core stop --no-progress >/dev/null
      cp '"$STORE"' '"$STORE"'.bak-$(date +%Y%m%d%H%M)
      jq --rawfile p /config/.bob-voice-prompt.txt '"'"'.data.entries |= map(if .domain=="ollama" and (.data.url | startswith("http://bob.tptpt.in:")) then (.subentries |= map(if .subentry_type=="conversation" then (.data.prompt=$p) else . end)) else . end)'"'"' '"$STORE"' > '"$STORE"'.new
      mv '"$STORE"'.new '"$STORE"'
      rm -f /config/.bob-voice-prompt.txt'
    echo "voice prompt written; Home Assistant restarting"
    for i in $(seq 1 30); do
      if ssh "$HOST" "jq -r '$JQ_READ' $STORE" >/dev/null 2>&1 && ssh "$HOST" 'ha core info --no-progress 2>/dev/null | grep -q "state: started"'; then break; fi
      sleep 10
    done
    exec "$0" --check ;;
  *) echo "usage: $0 --check | --apply" >&2; exit 2 ;;
esac
