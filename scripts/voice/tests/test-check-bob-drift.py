#!/usr/bin/env python3
"""Tests for check-bob-drift.sh — what a failed comparison is allowed to mean.

The script's header promises three outcomes: 0 green, 1 drift, 2 "could not
compare, treat as unknown". The chat half honoured that from the start. The
voice half did not: it collapsed every non-zero from apply-voice-prompt.sh
into 1, so anything that stopped the comparison from happening was reported
as "Bob has drifted".

That fired on 2026-09-22. A fleet-wide SSH key rotation locked the check out
of Home Assistant, apply-voice-prompt.sh died under `set -e` carrying ssh's
255, and Kuma 76 went red while the persona was untouched and the chat
fingerprint was green. The cost of the confusion is the whole point of the
monitor: a red that means "I could not look" trains you to ignore a red that
means "Bob is wrong".

Nothing here touches the network or Home Assistant. Both halves are injected —
the voice check is a stub with a chosen exit code, and prod's grounding is a
file:// URL — so an unreachable HA is reproducible instead of waited for.

  python3 scripts/voice/tests/test-check-bob-drift.py
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
REAL = HERE.parent / "check-bob-drift.sh"
FP = "abc12345"

failures = []


def run(voice_exit, voice_msg, published_fp):
    """Run check-bob-drift.sh against stubs; return (exit code, output)."""
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        voice = root / "scripts" / "voice"
        voice.mkdir(parents=True)
        shutil.copy(REAL, voice / "check-bob-drift.sh")

        stub = voice / "apply-voice-prompt.sh"
        stub.write_text(
            "#!/usr/bin/env bash\n"
            f"echo {json.dumps(voice_msg)} >&2\n"
            f"exit {voice_exit}\n"
        )
        stub.chmod(0o755)

        # The chat half is real code; only its two inputs are stubbed.
        (voice / "persona-fingerprint.mjs").write_text(
            f"process.stdout.write({json.dumps(FP)});\n"
        )
        grounding = root / "grounding.json"
        grounding.write_text(json.dumps({"personaFingerprint": published_fp}))

        p = subprocess.run(
            ["bash", str(voice / "check-bob-drift.sh")],
            capture_output=True, text=True,
            env={"PATH": "/usr/bin:/bin:/usr/local/bin",
                 "BOB_GROUNDING_URL": grounding.as_uri()},
        )
        return p.returncode, p.stdout + p.stderr


def check(name, got, want, output):
    if got == want:
        print(f"  ok   {name}: exit {got}")
    else:
        print(f"  FAIL {name}: exit {got}, expected {want}\n       {output.strip()}")
        failures.append(name)


print("check-bob-drift.sh")

rc, out = run(0, "voice prompt: live matches", FP)
check("everything agrees", rc, 0, out)

rc, out = run(1, "voice prompt: DRIFT between Home Assistant and the render", FP)
check("voice prompt really differs -> drift", rc, 1, out)

# The 2026-09-22 regression. ssh exits 255 when it cannot authenticate, and
# apply-voice-prompt.sh runs under `set -e`, so that is what comes back.
rc, out = run(255, "root@automatron.tptpt.in: Permission denied (publickey).", FP)
check("HA unreachable -> unknown, NOT drift", rc, 2, out)

rc, out = run(2, "usage: ... --check | --apply", FP)
check("voice check misused -> unknown", rc, 2, out)

# A real disagreement outranks an unverifiable half: 1 wins over 2.
rc, out = run(255, "Permission denied (publickey).", "deadbeef")
check("HA unreachable but chat drifted -> drift", rc, 1, out)

rc, out = run(0, "voice prompt: live matches", "deadbeef")
check("chat fingerprint differs -> drift", rc, 1, out)

print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all passed'}")
sys.exit(1 if failures else 0)
