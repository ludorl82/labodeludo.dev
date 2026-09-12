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

### After adding or editing an article: `npm run embed`

Bob answers from `public/bob-vectors.json`, a committed semantic index of the
corpus. The build does NOT regenerate it — that would make a public deploy fail
whenever the homelab is down — so it goes stale silently if this is skipped, and
the symptom is Bob failing to answer about the new article while still linking
to it.

`npm run embed` is incremental: unchanged chunks keep their vectors, so adding
one article re-embeds that article only. It needs `bob` reachable on the LAN
(it calls the `bge-m3` model on its Ollama); pass `--host` to point elsewhere.

## Documentation

Full documentation: https://docs.astro.build

Consult these guides before working on related tasks:

- [Adding pages, dynamic routes, or middleware](https://docs.astro.build/en/guides/routing/)
- [Working with Astro components](https://docs.astro.build/en/basics/astro-components/)
- [Using React, Vue, Svelte, or other framework components](https://docs.astro.build/en/guides/framework-components/)
- [Adding or managing content](https://docs.astro.build/en/guides/content-collections/)
- [Adding styles or using Tailwind](https://docs.astro.build/en/guides/styling/)
- [Supporting multiple languages](https://docs.astro.build/en/guides/internationalization/)
