# Nightly task: refresh the architectural diagram (PUBLIC data only)

You are running headless inside the nightly diagram job (Session B). Your
working directory contains ONLY public material: the four `*-iac-public`
snapshot clones under `snapshots/`, the labodeludo.dev checkout under
`site/`, and the freshly joined `architecture.json` (also copied to
`site/src/data/architecture.json`). You have not seen, and must not seek,
any private repository or real infrastructure detail.

## Two seeds, one drawing

- `architecture.json` — what the IaC repos **declare** (nodes, edges).
- `site/src/data/fleet.json` — what physically **exists**, including the
  boxes no repo declares: the switch, the AP, the printer, cameras,
  personal machines, the UPSes, the BMCs. Sanitized before it reached you;
  it carries no addresses on purpose. `iacDeclared: true` means the device
  is already in `architecture.json` — draw it once, not twice.

The drawing should show **the whole lab**, not only its declared half. A
device present in the fleet but absent from the IaC is not an error to
hide: draw it, muted/dashed like the existing hors-IaC boxes, because the
gap between what is declared and what exists is part of the story. If
`fleet.json` has an empty `devices` array the seed has not run yet — draw
from `architecture.json` alone and say nothing about it.

## Your one deliverable

Update `site/src/components/LiveArchDiagram.astro` — and ONLY that file —
so its drawn SHAPE still tells the truth about the architecture described
by `architecture.json` and the snapshots.

It is rendered inside `src/components/ArchGenerated.astro`, which is itself
the gated top half of the `/architecture` hub — so your diagram sits above
the exhaustive bands, the hand-drawn view and the role cards. Do not touch
any of those.

## What "still tells the truth" means

- Compare the diagram's structural claims against the data: sites, the
  single tunnel and its direction, where the control-plane lives, which
  paths exist (public name → tunnel → ingress → apps → machines; blog →
  S3), the WireGuard seam, host counts and names.
- If nothing structural changed, change nothing. Do not redraw for taste.
  Exit having made no edit and say so.
- If something changed (a host appeared/disappeared, a new layer-crossing
  path exists, the control-plane moved...), adjust the smallest set of
  boxes/paths/labels that makes the diagram true again.

## The hors-IaC nodes

`external:` nodes (layer `external`) are hardware NOT declared in any IaC
repo, surfaced only because the IaC references it (a tunnel origin, NFS
volumes, a UPS module). Draw them dashed and muted, never as first-class
boxes, and never invent one the data does not contain — their absence is
part of the story the page tells.

## Interactivity contract

The diagram participates in the page's click-highlight. Every box that
represents topology nodes MUST keep (or gain) either
`data-node="<id>"` (single node — wrapped in an SVG `<a>` with
`href={src(node)}` and a `<title>` tooltip) or
`data-nodes="<id> <id>..."` (aggregate — a `<g>`; a click lights exactly
its members). Ids come from architecture.json. Decorative marks
(visiteurs, arrows, the WireGuard line) carry neither. The driver refuses
a refresh that strips these attributes.

## Hard rules

1. **Counts and names must come from `architecture.json` at build time**
   (the component already imports it — keep that pattern). Never hardcode a
   number the data can provide.
2. **Only fictional naming may appear**: documentation IPs (192.0.2.x,
   198.51.100.x, 203.0.113.x, 2001:db8::) and example-family domains, the
   sanitized host names (gpu-01, pi-02, cloud-01...). Your output is
   mechanically scanned (`scan-public.py`) and the commit is refused on any
   violation — do not test that boundary.
3. Keep the site's diagram idiom: inline SVG, theme tokens (`var(--panel)`,
   `var(--panel-border)`, `var(--text)`, `var(--text-faint)`,
   `var(--accent-live)`), monospace font vars, orthogonal connectors,
   `role="img"` with a complete French `aria-label`, horizontal scroll via
   the existing `.diagram-wrap`. French labels.
3b. **Canvas reality**: the figure is full-bleed but capped at 1100px wide,
   and the site column is narrow — keep the flow VERTICAL (portrait-ish
   viewBox, roughly 760 wide; grow DOWNWARD when you need room, matching
   the page's band order edge → cluster → hardware). Never widen the
   viewBox past ~800.
4. The component must keep building. Try `SHOW_LIVE_ARCH=1 npm run build`
   in `site/` as your verification; if the sandbox denies it, say so and
   double-check your edit by reading it — the driver runs the same build
   (and the scan-public gate) before anything is committed, so a breakage
   is caught either way.
5. Do not touch any other file. Do not commit — the driver script reviews,
   gates and commits your change.

Report at the end, in one short paragraph: what structural drift you found
(or that there was none) and what you changed.
