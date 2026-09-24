import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

/* La mention d'IA est obligatoire : sans champ `ia`, le build échoue, donc un
   article ne peut pas être publié en l'oubliant. La page l'affiche en tête
   (AiNotice.astro).
     aucune   — écrit sans IA (les articles de 2019 à 2022)
     assistee — rédigé par Ludo avec l'aide de l'IA ; `iaOutils` nomme l'outil
     redigee  — rédigé par Bob, de bout en bout
   Un article tagué `bob` est forcément `redigee`. */
const postSchema = z
  .object({
    title: z.string(),
    pubDate: z.coerce.date(),
    description: z.string().optional().default(""),
    tags: z.array(z.string()).default([]),
    heroImage: z.string().optional(),
    ia: z.enum(["aucune", "assistee", "redigee"], {
      error:
        "champ `ia` manquant : aucune | assistee | redigee (voir src/content.config.ts)",
    }),
    iaOutils: z.string().optional(),
  })
  .refine((d) => !d.tags.includes("bob") || d.ia === "redigee", {
    message: "un article tagué `bob` doit avoir ia: \"redigee\"",
    path: ["ia"],
  })
  .refine((d) => d.ia !== "assistee" || !!d.iaOutils, {
    message: "ia: \"assistee\" exige iaOutils (ex. \"Claude Code\")",
    path: ["iaOutils"],
  });

const blog = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/blog" }),
  schema: postSchema,
});

const blogEn = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/blog-en" }),
  schema: postSchema,
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
  /* « aucune » pour les enregistrements du chat du site : le cadre par défaut
     reproduit une session Claude Code, et le chat n'en est pas une. */
  session: z.enum(["claude-code", "aucune"]).optional(),
  /* « none » quand la vraie barre tmux est dans l'enregistrement (prise
     réelle attachée à la session) : l'habillage en ferait une deuxième. */
  frame: z.enum(["alacritty", "none"]).optional(),
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
