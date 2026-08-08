"""Positive allowlist over public-facing generated content.

Shared by join-topology.py (scans the merged architecture.json) and
scan-public.py (scans arbitrary files an automated author produced before
they may be committed). It deliberately knows only what FICTIONAL data
looks like — documentation addressing and example-family domains — never
what real data looks like; a denylist here would itself be the leak.
"""
import re

ALLOWED_V4 = re.compile(
    r"\b(192\.0\.2|198\.51\.100|203\.0\.113|198\.18\.0)\.\d{1,3}\b")
ANY_V4 = re.compile(r"\b\d{1,3}(\.\d{1,3}){3}\b")
ANY_V6 = re.compile(r"\b[0-9a-fA-F:]*::?[0-9a-fA-F:]+\b")
HOSTLIKE = re.compile(r"\b[a-z0-9-]+(\.[a-z0-9-]+)+\b", re.I)
ALLOWED_SUFFIX = (
    ".example", "example.com", "labodeludo.dev", "labodeludo.com",
    "pages.dev", "cfargotunnel.com", "amazonaws.com", "svc.cluster.local",
    "acm-validations.aws", "github.com",
)
# A dotted token is only treated as a HOSTNAME when its final label is a
# public TLD — code identifiers (arch.nodes), filenames (foo.yaml) and
# instance types (t3a.medium) all end in something that is not one. This
# list is generic internet knowledge (not derived from any private data)
# and intentionally over-broad; it must at minimum cover every TLD the lab
# actually uses so a real name can never pass.
# Word-like TLDs (.to, .sh, .run, .live, .network...) are deliberately
# ABSENT: they collide with code identifiers (e.to, deploy.sh) and the lab
# uses none of them. Every TLD the lab actually uses (com net in ca io dev)
# must stay, or a real name could pass.
PUBLIC_TLDS = frozenset((
    "com net org io in dev ca app me co uk fr de eu us nl ch at be es "
    "pl se no fi dk ie nz au jp kr cn ru br mx ar biz info xyz cc tv ai"
).split())


class Leak(Exception):
    pass


def scan(value: str, where: str) -> None:
    """Raise Leak if the string contains anything outside the allowlist."""
    for m in ANY_V4.finditer(value):
        if not ALLOWED_V4.match(m.group(0)):
            raise Leak(f"non-documentation IPv4 {m.group(0)!r} at {where}")
    for m in ANY_V6.finditer(value):
        s = m.group(0)
        groups = [g for g in s.split(":") if g]
        # host:port also matches the loose pattern — only treat it as an
        # address when it has :: or at least three hex groups
        if "::" in s or len(groups) >= 3:
            if not s.lower().startswith("2001:db8"):
                raise Leak(f"non-documentation IPv6 {s!r} at {where}")
    # a bare @ is everywhere in code (JSX, decorators) — only the full
    # email shape with a non-example domain is a leak
    for m in re.finditer(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})",
                         value):
        if not m.group(1).lower().endswith(ALLOWED_SUFFIX):
            raise Leak(f"email-shaped {m.group(0)!r} at {where}")
    for m in HOSTLIKE.finditer(value):
        s = m.group(0).lower()
        if ANY_V4.match(s) or s.endswith(ALLOWED_SUFFIX):
            continue
        if s.split(".")[-1] in PUBLIC_TLDS:
            raise Leak(f"hostname-like string {s!r} outside the allowlist "
                       f"at {where}")


def walk(obj, where: str) -> None:
    """scan() every string in a nested JSON-ish structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, f"{where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, f"{where}[{i}]")
    elif isinstance(obj, str):
        scan(obj, where)
