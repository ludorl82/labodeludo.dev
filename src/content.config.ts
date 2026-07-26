import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const blog = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/blog" }),
  schema: z.object({
    title: z.string(),
    pubDate: z.coerce.date(),
    description: z.string().optional().default(""),
    tags: z.array(z.string()).default([]),
    heroImage: z.string().optional(),
  }),
});

const blogEn = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/blog-en" }),
  schema: z.object({
    title: z.string(),
    pubDate: z.coerce.date(),
    description: z.string().optional().default(""),
    tags: z.array(z.string()).default([]),
    heroImage: z.string().optional(),
  }),
});

/* Terminal recordings. The .cast file is the artifact; this collection holds
   the framing around it — including the disclaimer, which is mandatory because
   every cast is a condensed reconstruction rather than a live capture. */
const castSchema = z.object({
  title: z.string(),
  pubDate: z.coerce.date(),
  description: z.string().optional().default(""),
  cast: z.string(),
  poster: z.string().optional(),
  disclaimer: z.string(),
  caption: z.string(),
  /** Slug of the article this recording came from, if any. */
  article: z.string().optional(),
});

const casts = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/casts" }),
  schema: castSchema,
});

const castsEn = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/casts-en" }),
  schema: castSchema,
});

const pages = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/pages" }),
  schema: z.object({
    title: z.string(),
  }),
});

export const collections = { blog, blogEn, casts, castsEn, pages };
