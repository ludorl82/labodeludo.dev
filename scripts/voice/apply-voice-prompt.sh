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
# session (nixos-iac, qwen-voice-bridge.py), with an empty prompt on purpose —
# the bridge forwards only the last sentence. Unscoped, --apply would write
# Bob's prompt into it, and --check would compare against both entries (it
# only passed because an empty prompt adds a trailing newline that $( )
# strips; a non-empty one there would read as drift).
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
      # `ha core info` has no state line on this Supervisor (found 2026-09-28):
      # the old grep for "state: started" never matched, so this loop always
      # ran its full 5 minutes. HA's web server answering is the signal.
      if [ "$(curl -sk -m 5 -o /dev/null -w '%{http_code}' "https://${HA_HTTP:-automatron-local.tptpt.in}/manifest.json")" = 200 ]; then break; fi
      sleep 10
    done
    "$0" --check || exit 1
    # The prompt lives in core.config_entries, which ha-iac (private, next to
    # this repo) mirrors and checks every morning: without a catch-up there,
    # every prompt change reads as drift. pull-config opens the PR; a missing
    # checkout or a failure does not undo the apply, it only says so.
    if [ -f "${HA_IAC_DIR:-../ha-iac}/scripts/pull-config.sh" ]; then
      ( cd "${HA_IAC_DIR:-../ha-iac}" && sh scripts/pull-config.sh ) \
        || echo "ha-iac: pull-config failed — run it by hand" >&2
    else
      echo "ha-iac: no checkout at ${HA_IAC_DIR:-../ha-iac} — run its scripts/pull-config.sh by hand" >&2
    fi ;;
  *) echo "usage: $0 --check | --apply" >&2; exit 2 ;;
esac
