#!/usr/bin/env bash
# Is the Bob that runs the Bob that is written? Two comparisons, one verdict.
#
#   1. Home Assistant's voice prompt against the render of bob-persona.md +
#      voice-rules.txt (apply-voice-prompt.sh --check, needs `ssh automatron`).
#   2. The persona fingerprint production publishes in /bob-grounding.json
#      against the one computed from this checkout (persona-fingerprint.mjs).
#
# The first catches a prompt edited by hand in HA, or a merge nobody applied.
# The second catches a merge to main that never reached prod, or a prod built
# from something else. Both are "green job, wrong Bob" failures: nothing else
# would notice, the site and the house would just sound a little off.
#
# Meant to run from a checkout of MAIN: the Chat section on main is what prod
# was built from, and a dev-only edit is not drift, it is a pending change.
# Exit 1 on any drift, 2 when a comparison could not be made — a caller that
# maps 2 to "unknown" rather than "red" avoids paging on a flaky ssh.
set -uo pipefail
cd "$(dirname "$0")/../.."
PROD="${BOB_GROUNDING_URL:-https://labodeludo.dev/bob-grounding.json}"
rc=0

if out=$(scripts/voice/apply-voice-prompt.sh --check 2>&1); then
  echo "voice: ok"
else
  echo "$out" | sed 's/^/voice: /'
  rc=1
fi

want=$(node scripts/voice/persona-fingerprint.mjs) || { echo "chat: cannot compute fingerprint"; exit 2; }
live=$(curl -fsS --max-time 20 "$PROD" | jq -r '.personaFingerprint // empty')
if [ -z "$live" ]; then
  echo "chat: prod grounding unreadable or has no personaFingerprint"
  [ "$rc" = 0 ] && rc=2
elif [ "$live" = "$want" ]; then
  echo "chat: ok ($live)"
else
  echo "chat: DRIFT prod publishes $live, main computes $want"
  rc=1
fi
exit $rc
