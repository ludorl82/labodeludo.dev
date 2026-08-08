# The seeds behind /architecture

Two files feed the nightly author, and they answer different questions:

- **`architecture.json`** — what the IaC repos *declare*, joined from the
  four public snapshots (contract below). Deterministic, gate-published.
- **`src/data/fleet.json`** — what physically *exists*, including the boxes
  no repo declares (the switch, the AP, the printer, cameras, personal
  machines). It is derived from a hand-maintained PRIVATE document by the
  nightly job's private session, sanitized through the same host map the
  `*-iac` sanitizers use, and it crosses into this repo only after two
  mechanical gates: the positive allowlist (`scan-public.py`) and a
  denylist of real names that lives in the private driver and is never
  published. Shape:

```json
{
  "fleetVersion": 1,
  "generated": "2026-08-08T09:00:00+00:00",
  "devices": [
    { "name": "gpu-01", "class": "server", "network": "vlan10",
      "role": "agent k3s, GPU", "iacDeclared": true }
  ]
}
```

`class` is free-form but conventional (`server`, `sbc`, `vm`, `nas`,
`router`, `switch`, `access-point`, `printer`, `camera`, `ups`, `bmc`,
`laptop`, `phone`, `cloud-vm`). **No addresses of any kind** — a diagram
does not need them, and their absence removes the largest class of leak by
construction. `iacDeclared` says whether the device also appears in
`architecture.json`, so the author does not draw it twice.

An empty `devices` array is valid and means "the seed has not run yet" —
the site must build either way.

---

# topology.json — the contract between the IaC snapshots and this site

The `/architecture` live view is generated from the four **public sanitized
snapshots** ([nixos-iac-public], [k3s-iac-public], [aws-iac-public],
[cloudflare-iac-public]). Each snapshot carries a `topology.json` at its root,
emitted by that repo's sanitizer **from the already-sanitized tree** — so the
data is fictional by construction and passes the same fail-closed verification
gate as the rest of the snapshot. This site never reads the private repos;
that is the design, not a detail.

[nixos-iac-public]: https://github.com/ludorl82/nixos-iac-public
[k3s-iac-public]: https://github.com/ludorl82/k3s-iac-public
[aws-iac-public]: https://github.com/ludorl82/aws-iac-public
[cloudflare-iac-public]: https://github.com/ludorl82/cloudflare-iac-public

## Shape

```json
{
  "topologyVersion": 1,
  "repo": "k3s-iac-public",
  "layer": "cluster",
  "nodes": [
    {
      "id": "workload:kuma/kuma",
      "kind": "workload",
      "label": "kuma",
      "layer": "cluster",
      "source": "kuma/deployment.yaml",
      "meta": {}
    }
  ],
  "edges": [
    { "from": "workload:kuma/kuma", "to": "host:cloud-01", "kind": "pinned-to" }
  ]
}
```

- `topologyVersion` — bumped on breaking shape changes; the join step refuses
  versions it does not know.
- `layer` — one per repo: `hardware` (nixos), `cluster` (k3s), `cloud` (aws),
  `edge` (cloudflare).
- `source` — path of the file inside that public snapshot that defines the
  node; the site renders every box as a link to it.

## Id namespaces

Ids are `namespace:rest`, lowercase, matching `[a-z0-9.:/@_-]+`.

| namespace | emitted by | meaning |
|---|---|---|
| `host:` | nixos | a machine (`host:gpu-01`) |
| `cluster:` | k3s | the k3s cluster grouping node (`cluster:k3s`) |
| `app:` | k3s | an Argo CD Application (`app:kuma`) |
| `workload:` | k3s | Deployment/StatefulSet/DaemonSet/CronJob (`workload:<app>/<name>`) |
| `route:` | k3s | an IngressRoute (`route:<app>/<name>`, `meta.hosts` = hostnames) |
| `instance:` | aws | an EC2 instance |
| `lambda:` | aws | a Lambda function |
| `bucket:` | aws | an S3 bucket |
| `tunnel:` | cloudflare | a Cloudflare Tunnel (`tunnel:k3s`) |
| `dns:` | cloudflare | a public hostname routed through the tunnel (`dns:kuma.pub.example.com`) |
| `access:` | cloudflare | a Cloudflare Access application |
| `external:` | any | hors-IaC hardware, derived ONLY from what the IaC references (a non-cluster tunnel origin → `external:router`, NFS/plex → `external:nas`, a ups-master module → `external:ups-<host>`). Never hand-listed; gear nothing references stays invisible by design. Ids in this namespace MAY collide across snapshots — the join merges them (meta union + `meta.seenBy`) instead of failing. |

## Edge kinds

| kind | meaning |
|---|---|
| `part-of` | workload/route → app; app → cluster |
| `pinned-to` | workload → host (nodeSelector) |
| `member-of` | host → cluster:k3s (the host runs a k3s server/agent) |
| `routes-to` | dns → tunnel; tunnel → cluster; route → workload |
| `is` | identity across layers (`instance:...` → `host:cloud-01`) |
| `protects` | access app → dns hostname |
| `uses` | app/host → external hardware it leans on (NFS, plex backend), or app → an S3 bucket its manifests name (`meta.s3Refs` on the app node, captured by the k3s emitter; the join promotes a ref to an edge only when the aws layer declares that bucket) |
| `powered-by` | host → its UPS |

## Rules (enforced by the emitters, re-checked by the join)

1. An emitter that extracts **zero nodes** exits non-zero — an empty layer is
   a broken parser, never a valid result.
2. Every edge endpoint either exists in the same file's `nodes`, or is a
   **cross-layer reference** into one of the namespaces another layer owns
   (`host:`, `cluster:`, `tunnel:`, `dns:`). The join step resolves those and
   fails on danglers.
3. The join ([`join-topology.py`](join-topology.py)) additionally greps the
   merged output against a forbidden-pattern list (real-looking RFC 1918
   addresses, non-example domains) — belt and suspenders on top of each
   snapshot's own gate.
