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
  loader: glob({ pattern: "**/*.md", base: "./src/content/blog-en" }),
  schema: z.object({
    title: z.string(),
    pubDate: z.coerce.date(),
    description: z.string().optional().default(""),
    tags: z.array(z.string()).default([]),
    heroImage: z.string().optional(),
  }),
});

const pages = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/pages" }),
  schema: z.object({
    title: z.string(),
  }),
});

export const collections = { blog, blogEn, pages };
