#!/usr/bin/env python3
"""Tests for check-answerable.py — the decision logic, with a fake Bob.

The gate's own `--selftest` covers the refusal DETECTOR against replies whose
verdict is known. This covers the layer above it: what happens to a question
once the detector has spoken, which is where the consequential choices live —
the retry past the rate limiter, and the rule that an unverifiable question is
kept rather than dropped.

Nothing here touches the network. The asker is injected, so a rate limiter, a
dead endpoint and an empty reply are all reproducible instead of waited for.

  python3 scripts/topology/tests/test-check-answerable.py
"""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
GATE = HERE.parent / "check-answerable.py"

spec = importlib.util.spec_from_file_location("gate", GATE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

# The retry sleeps; the test should not.
gate.RETRY_BACKOFF_S = 0
gate.SPACING_S = 0

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  \033[32mok\033[0m   {label}")
    else:
        failed += 1
        print(f"  \033[31mFAIL\033[0m {label}: got {got!r}, wanted {want!r}")


def scripted(*replies):
    """An asker that returns each (reply, links, limited, err) tuple in turn."""
    seq = list(replies)
    calls = []

    def asker(q):
        calls.append(q)
        return seq.pop(0) if seq else seq_default
    seq_default = ("", [], False, "ran out of scripted replies")
    asker.calls = calls
    return asker


print("\033[1m== a plain answer is published\033[0m")
v, _ = gate.verdict("q", scripted(("Y'a un article là-dessus, /blog/x/.", ["/blog/x/"], False, "")))
check("answered", v, "ANSWERED")

print("\n\033[1m== a refusal is a dead end, whatever words it uses\033[0m")
v, _ = gate.verdict("q", scripted(("Ça, c'est pas documenté — demande à Ludo.", [], False, "")))
check("the prescribed sentence", v, "REFUSED")
# Captured from production 2026-09-15: the same refusal, phrased freely. The
# detector must not depend on the model reciting the prompt word for word.
v, _ = gate.verdict("q", scripted(
    ("Non, Proxmox c'est pas dans le parc — y'a rien là-dessus dans l'index "
     "ni sur les pages. C'est pas documenté ici, tu demandes à Ludo.", [], False, "")))
check("the same refusal, freely phrased", v, "REFUSED")

print("\n\033[1m== the rate limiter is not a refusal\033[0m")
a = scripted(("Doucement. Une question à la fois.", [], True, ""),
             ("Ouais, c'est /blog/x/.", ["/blog/x/"], False, ""))
v, _ = gate.verdict("q", a)
check("retried past the limiter", v, "ANSWERED")
check("asked twice", len(a.calls), 2)

a = scripted(("Doucement.", [], True, ""), ("Doucement.", [], True, ""))
v, why = gate.verdict("q", a)
check("limited twice is inconclusive, not refused", v, "INCONCLUSIVE")
check("says why", "rate-limited" in why, True)

print("\n\033[1m== a broken endpoint is inconclusive, never a refusal\033[0m")
v, _ = gate.verdict("q", scripted(("", [], False, "curl 28: timeout"),
                                  ("", [], False, "curl 28: timeout")))
check("transport failure", v, "INCONCLUSIVE")
v, _ = gate.verdict("q", scripted(("", [], False, ""), ("   ", [], False, "")))
check("empty reply", v, "INCONCLUSIVE")

print("\n\033[1m== filtering keeps what it could not check\033[0m")
# The whole point: a gate that deletes questions because the network hiccupped
# would be a worse failure than the dead end it exists to remove.
with tempfile.TemporaryDirectory() as d:
    p = pathlib.Path(d) / "openers.json"
    p.write_text(json.dumps({"generated": "x", "openers": ["bon", "mort", "inconnu"]}))
    replies = {
        "bon": ("Oui, /blog/x/.", ["/blog/x/"], False, ""),
        "mort": ("Ça, c'est pas documenté — demande à Ludo.", [], False, ""),
        "inconnu": ("", [], False, "curl 28: timeout"),
    }
    gate.ask = lambda q: replies[q]
    sys.argv = ["check-answerable.py", str(p), "--filter", "--min", "1"]
    code = gate.main()
    out = json.loads(p.read_text())
    check("exit 0 when filtering", code, 0)
    check("the dead end is gone", "mort" in out["openers"], False)
    check("the good one stays", "bon" in out["openers"], True)
    check("the unverifiable one is KEPT", "inconnu" in out["openers"], True)

print("\n\033[1m== --min is a floor, and it is enforced\033[0m")
with tempfile.TemporaryDirectory() as d:
    p = pathlib.Path(d) / "openers.json"
    p.write_text(json.dumps({"generated": "x", "openers": ["mort"]}))
    gate.ask = lambda q: ("Ça, c'est pas documenté — demande à Ludo.", [], False, "")
    sys.argv = ["check-answerable.py", str(p), "--filter", "--min", "1"]
    check("fails when nothing survives", gate.main(), 1)

print("\n\033[1m== the gate refuses to run on a broken detector\033[0m")
# A gate nobody re-validates is how a saturated test survives for months.
saved = gate.SELFTEST
gate.SELFTEST = [("Ça, c'est pas documenté — demande à Ludo.", [], False)]  # wrong truth
with tempfile.TemporaryDirectory() as d:
    p = pathlib.Path(d) / "openers.json"
    p.write_text(json.dumps({"generated": "x", "openers": ["q"]}))
    sys.argv = ["check-answerable.py", str(p)]
    check("exits 2 rather than judging", gate.main(), 2)
gate.SELFTEST = saved

print("\n\033[1m== the shipped file passes its own selftest\033[0m")
r = subprocess.run([sys.executable, str(GATE), "--selftest"], capture_output=True, text=True)
check("selftest green", r.returncode, 0)

print(f"\n\033[1m{passed} passed, {failed} failed\033[0m")
sys.exit(1 if failed else 0)
