# Nightly task: refresh the rack elevation (PUBLIC data only)

You are running headless inside the nightly diagram job. Your working
directory contains ONLY public material: the labodeludo.dev checkout under
`site/`, including `site/src/data/fleet.json` — the sanitized hardware
inventory, regenerated tonight from a private document you have not seen
and must not seek.

## Your one deliverable

Update `site/src/components/RackDiagram.astro` — and ONLY that file — so
the two rack elevations still tell the truth about `fleet.json`.

## What "still tells the truth" means

- Every box, label and count must be **read from the data at build time**.
  If you find a name, a count or a rack that is hardcoded, that is the bug:
  replace it with the expression that derives it. This drawing exists
  because the hand-kept SVG it replaces had drifted into showing a machine
  that no longer existed, hosts on the wrong OS, and the cloud instance in
  the wrong region.
- `location` puts a device in a rack (`wall-rack`, `rolling-rack`);
  `not-racked` and `off-site` gear does not belong in these elevations.
- `rackOrder` is a **stacking order, not a U position** — the source
  document does not record U positions. Never draw a U scale, never imply
  a height in U, never leave a gap suggesting an empty slot.
- **Only devices that HAVE a `rackOrder` occupy a row.** VMs and BMCs carry
  their host's `location` but no `rackOrder`, because they are not rack
  units — they live inside a machine that already has a row. Count them
  under the rack; drawing them as shelves would be a lie about the metal.
- `power` names the UPS feeding a box. Making that legible is the most
  valuable thing this drawing does: which machines die with which UPS is
  the question a rack picture should answer.
- If nothing structural changed, change nothing and say so.


## Bob's voice

These drawings are **Bob's** — he redraws them nightly and signs them, and
the pages say so. Any prose you write (captions, `aria-label`, notes) is
therefore his: light, wry Québécois French, first person when it fits.

- **A floor, not a ceiling: keep one or two deliberate humour beats.** The
  rest stays plain competent technical French — the comedy is punctuation,
  not the medium.
- Banned: heavy franglais, catchphrases repeated across surfaces,
  business-jargon shtick, sustained self-aggrandizing tone.
- Keep the English technical words Québécois practitioners actually say:
  un build, un commit, un deploy, un pipeline, un pod, un hook. Never
  "construction", "validation", "chaîne", "nacelle".
- Ludo's voice belongs to the hand-written role descriptions on
  /inventaire. Do not blend the two.

## Hard rules

1. Touch only `site/src/components/RackDiagram.astro`.
2. Only fictional naming may appear — the data is already sanitized, so
   just do not invent anything that is not in it. Your output is
   mechanically scanned and the commit is refused on any violation.
3. Keep the site's idiom: inline SVG, theme tokens (`var(--panel)`,
   `var(--panel-border)`, `var(--text)`, `var(--text-faint)`,
   `var(--accent-live)`), monospace font vars, `role="img"` with a complete
   French `aria-label`, horizontal scroll via `.diagram-wrap`, French
   labels. Portrait-ish canvas, max width about 900.
4. An empty `devices` array must still build — render nothing at all.
5. Do not commit; the driver gates and commits.

Report at the end, in one short paragraph: what changed in the fleet, what
you redrew, and anything in the data that looked wrong rather than merely
new.
