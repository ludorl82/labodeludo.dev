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
    # the hand-drawn diagrams label their nodes in French with the same
    # intent as example.net (relais.exemple.net, portail.exemple.net) —
    # fictional by construction, and no lab name has ever looked like this
    "exemple.net", "exemple.com",
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


def scan(value: str, where: str, extra_suffix: tuple = ()) -> None:
    """Raise Leak if the string contains anything outside the allowlist."""
    allowed = ALLOWED_SUFFIX + tuple(extra_suffix)
    for m in ANY_V4.finditer(value):
        if not ALLOWED_V4.match(m.group(0)):
            raise Leak(f"non-documentation IPv4 {m.group(0)!r} at {where}")
    for m in ANY_V6.finditer(value):
        s = m.group(0)
        groups = [g for g in s.split(":") if g]
        # host:port and timestamps (11:26:13) also match the loose pattern —
        # only treat it as an address when it has ::, four-plus groups, or a
        # hex letter in some group (every real prefix here has one)
        hexish = any(re.search(r"[a-f]", g, re.I) for g in groups)
        if "::" in s or len(groups) >= 4 or (len(groups) >= 3 and hexish):
            if not s.lower().startswith("2001:db8"):
                raise Leak(f"non-documentation IPv6 {s!r} at {where}")
    # a bare @ is everywhere in code (JSX, decorators) — only the full
    # email shape with a non-example domain is a leak
    for m in re.finditer(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})",
                         value):
        if not m.group(1).lower().endswith(allowed):
            raise Leak(f"email-shaped {m.group(0)!r} at {where}")
    for m in HOSTLIKE.finditer(value):
        s = m.group(0).lower()
        if ANY_V4.match(s) or s.endswith(allowed):
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


def _is_v6_address(s: str) -> bool:
    groups = [g for g in s.split(":") if g]
    hexish = any(re.search(r"[a-f]", g, re.I) for g in groups)
    return "::" in s or len(groups) >= 4 or (len(groups) >= 3 and hexish)


def redact(value: str, extra_suffix: tuple = ()) -> str:
    """Replace everything scan() would refuse with its documentation twin.

    For prose that must be published unattended (the nightly console
    snapshot): instead of refusing a whole window over one address, the
    address becomes 192.0.2.x, the domain becomes site.example. The last
    octet / group is kept so two different hosts stay two different hosts
    on the page. `extra_suffix` lets the caller allow well-known public
    domains (docs, vendors) that the infrastructure allowlist never needed.
    scan() must still pass afterwards; redact() narrows, it does not vouch.
    """
    allowed = ALLOWED_SUFFIX + tuple(extra_suffix)

    def v4(m):
        s = m.group(0)
        if ALLOWED_V4.match(s):
            return s
        return "192.0.2." + s.rsplit(".", 1)[1]

    def v6(m):
        s = m.group(0)
        if not _is_v6_address(s) or s.lower().startswith("2001:db8"):
            return s
        last = [g for g in s.split(":") if g][-1:] or ["1"]
        return "2001:db8::" + last[0]

    def email(m):
        if m.group(1).lower().endswith(allowed):
            return m.group(0)
        return "courriel@example.com"

    def host(m):
        s = m.group(0).lower()
        if ANY_V4.match(s) or s.endswith(allowed):
            return m.group(0)
        if s.split(".")[-1] in PUBLIC_TLDS:
            return "site.example"
        return m.group(0)

    value = ANY_V4.sub(v4, value)
    value = ANY_V6.sub(v6, value)
    value = re.sub(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})",
                   email, value)
    return HOSTLIKE.sub(host, value)
