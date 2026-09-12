## Project context

This is the source for labodeludo.dev, migrated from WordPress in July 2026. See README.md for architecture, content structure, and the deploy pipeline.

Key operational rules:
- `main` is protected and deploys straight to the S3 prod bucket with `--delete` — never push half-finished content there. Push to `dev` (or a feature branch) first; it deploys to the staging container automatically.
- Any change to `scripts/redirect-old-urls.sh` or the old-URL mapping should be tested against the actual `git log`/deploy history, not assumed — WordPress's permalink category prefix didn't always match the post's first assigned category.
- Article frontmatter `tags` array does double duty (category chip color + author badge) — see `src/lib/category.ts` / `src/lib/author.ts` before changing how tags are parsed.

## Development

When starting the dev server, use background mode:

```
astro dev --background
```

Manage the background server with `astro dev stop`, `astro dev status`, and `astro dev logs`.

### The semantic index rebuilds itself during `npm run build`

Bob answers from `public/bob-vectors.json`, a semantic index of the corpus. The
build regenerates it (`--soft`) and the result is also committed, which is two
things for two reasons:

- **In the build**, so it cannot go stale silently. It used to be a manual step
  and the symptom of forgetting it misleads: Bob keeps LINKING a new article
  while unable to say a word about its content, so he looks like he knows it.
- **Committed**, so an unreachable Ollama is a loud warning and the previous
  index ships unchanged, instead of a failed deploy.

It is incremental — one new article re-embeds that article only — and it does
not rewrite the file when nothing changed, so a build never produces a spurious
2.4 MB diff.

Run `npm run embed` (no `--soft`) by hand when you want it to FAIL on a broken
embedding service, and commit the result so the fallback copy stays current.

The model runs in the cluster (`embeddings` namespace, on the GPU reserved for
Kubernetes), so the build reaches it by Service name — it runs on the in-cluster
runner. From a laptop, forward the port first:

```
kubectl port-forward -n embeddings svc/embeddings 11435:11434
npm run embed -- --host http://127.0.0.1:11435
```

## Documentation

Full documentation: https://docs.astro.build

Consult these guides before working on related tasks:

- [Adding pages, dynamic routes, or middleware](https://docs.astro.build/en/guides/routing/)
- [Working with Astro components](https://docs.astro.build/en/basics/astro-components/)
- [Using React, Vue, Svelte, or other framework components](https://docs.astro.build/en/guides/framework-components/)
- [Adding or managing content](https://docs.astro.build/en/guides/content-collections/)
- [Adding styles or using Tailwind](https://docs.astro.build/en/guides/styling/)
- [Supporting multiple languages](https://docs.astro.build/en/guides/internationalization/)
