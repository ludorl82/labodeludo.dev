# labodeludo.dev

Source for [labodeludo.dev](https://labodeludo.dev) — Ludo's homelab/DevOps blog. Built with [Astro](https://astro.build), content in Markdown, deployed to S3.

Migrated from WordPress in July 2026. WordPress is fully decommissioned; this repo + S3 is the whole site now.

## Project structure

```
/
├── src/
│   ├── content/
│   │   ├── blog/          # articles (Markdown + frontmatter: title, pubDate, description, tags, heroImage)
│   │   └── pages/          # standalone pages (e.g. Mission), rendered by src/pages/[...slug].astro
│   ├── content.config.ts   # content collection schemas
│   ├── layouts/BaseLayout.astro
│   ├── components/         # CategoryChip, AuthorBadge, AuthorBox, TopologyStrip, Lightbox
│   ├── lib/                # category.ts, author.ts — tag → category/author mapping
│   └── pages/
│       ├── index.astro           # homepage: article list
│       ├── blog/[...slug].astro  # article page
│       └── [...slug].astro       # static pages (Mission, ...)
├── public/images/blog/     # article images, mirrors WordPress's wp-content/uploads relative paths
├── docker-compose.yml      # staging container (nginx serving dist/)
├── scripts/redirect-old-urls.sh  # recreates 301s from old WordPress URLs, runs every prod deploy
└── .github/workflows/deploy.yml
```

Tags in article frontmatter carry double duty: the WordPress category (`DevOps`/`Cloud`/`Maison`/`Labo`) drives the colored chip and topology-strip dot, and `bob`/`ludo` drives the author badge — see `src/lib/category.ts` and `src/lib/author.ts`.

## Deploy pipeline

A self-hosted GitHub Actions runner lives on `docker.tptpt.in` (systemd service, labels `docker`) — see `.github/workflows/deploy.yml`.

- **Push to `main`** (protected, PR required): builds and runs `aws s3 sync dist/ s3://labodeludo.dev/ --delete`, then re-runs `scripts/redirect-old-urls.sh` (the sync's `--delete` would otherwise wipe the old-URL redirect objects every time, since they live outside `dist/`). Uses a scoped IAM user (`labodeludo-deploy`, policy limited to this one bucket) via GitHub secrets.
- **Push to any other branch** (`dev`, feature branches): builds and runs `docker compose up -d --force-recreate` on the runner — serves the build locally on `docker.tptpt.in:80` via nginx (container `labodeludo-staging`). `--force-recreate` is required: `astro build` gives `dist/` a new inode every run, so a running container's bind mount otherwise goes stale and serves an empty directory.

**Don't push to `main` with unfinished content** — the prod sync fully replaces the bucket's contents every time, there's no versioning safety net.

## Local preview

Traefik on `aws` (`~/web-docker/traefik/dynamic/astro.yml`) routes `Host(labodeludo.dev)` → `172.16.10.130:80` (the staging container). To preview whatever's currently deployed on `dev`, point your local hosts file at `labodeludo.dev → 10.10.10.7` (aws's private WireGuard IP, already routed from home VLANs).

## Commands

| Command | Action |
| :------ | :----- |
| `npm install` | Install dependencies |
| `npm run dev` | Local dev server at `localhost:4321` |
| `npm run build` | Build to `./dist/` |
| `npm run preview` | Preview the build locally |
