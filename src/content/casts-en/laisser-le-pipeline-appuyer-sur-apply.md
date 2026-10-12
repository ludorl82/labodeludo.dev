---
title: "The pipeline presses apply"
pubDate: 2026-07-31
description: "One tool picked per repo, a destroy gate tested against a real DNS record, then the same merge delivered on the NixOS side by comin, with nobody at the keyboard."
cast: "/casts/iac-apply.cast"
poster: "npt:0:14"
caption: "Picking one tool per repo, the destroy gate tested against a real record, then the same merge delivered on the NixOS side by comin, with nobody at the keyboard."
article: "laisser-le-pipeline-appuyer-sur-apply"
type: "reconstitution"
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, assembled afterwards from the real session transcript. The prompts and stop messages are from the actual session; timing is compressed and the long CI-watch loops are cut. Hostnames sanitized; the DNS record shown was a throwaway created for this test."
---

Four infrastructure repos already described in code, but every apply still went
through a human hand. The session closes the loop: GitHub Actions with OIDC for
the cloud, Argo CD for the cluster, comin for NixOS.

The gate was not taken at its word. A first PR creates a throwaway TXT record,
and it resolves on the public internet after the merge. A second PR deletes it,
and the job refuses. Twice that day, Claude Code's permission classifier also
handed control back: once on `tofu apply`, once on reading a secret.
