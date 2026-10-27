import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

/* La mention d'IA est obligatoire : sans champ `ia`, le build échoue, donc un
   article ne peut pas être publié en l'oubliant. La page l'affiche en tête
   (AiNotice.astro).
     aucune   — écrit sans IA (les articles de 2019 à 2022)
     reecrite — écrit par Ludo à partir d'un premier jet de l'IA, qu'il a
                reformulé en majeure partie ; `iaOutils` nomme l'outil
     assistee — rédigé par l'IA, relu et validé entièrement par Ludo ; `iaOutils` nomme l'outil
     redigee  — rédigé par Bob, de bout en bout
   Un article tagué `bob` est forcément `redigee`.
   `certificatHumain` porte l'identifiant d'un certificat Humanums
   (humanums.com/verify/<id>) : le texte a été tapé par Ludo dans leur éditeur,
   qui signe une empreinte du texte exact. L'original français offre le texte
   certifié à copier; la traduction renvoie au certificat.
   `court` est le code du lien court lbdl.dev/<court>, une 301 vers
   l'article (le Worker `lbdl` de cloudflare-iac lit liens-courts.json).
   LinkedIn remplace par lnkd.in tout
   lien de 26 caractères ou plus, tel que tapé : `lbdl.dev/` (9) laisse 16
   caractères au code, assez pour la plupart des slugs tels quels. Chaque
   langue a le sien (ex. `vmotion` et `vmotion-en`) ; l'unicité est
   vérifiée après le build (scripts/check-short-links.mjs). */
const postSchema = z
  .object({
    title: z.string(),
    pubDate: z.coerce.date(),
    description: z.string().optional().default(""),
    tags: z.array(z.string()).default([]),
    heroImage: z.string().optional(),
    ia: z.enum(["aucune", "reecrite", "assistee", "redigee"], {
      error:
        "champ `ia` manquant : aucune | reecrite | assistee | redigee (voir src/content.config.ts)",
    }),
    iaOutils: z.string().optional(),
    certificatHumain: z
      .string()
      .regex(/^HM-[A-Z0-9]{4}-[A-Z0-9]{4}$/, "certificatHumain : HM-XXXX-XXXX")
      .optional(),
    court: z
      .string()
      .regex(/^[a-z0-9-]{1,16}$/, "court : 16 caractères au plus, a-z 0-9 -")
      .optional(),
  })
  .refine((d) => !d.tags.includes("bob") || d.ia === "redigee", {
    message: "un article tagué `bob` doit avoir ia: \"redigee\"",
    path: ["ia"],
  })
  .refine((d) => (d.ia !== "assistee" && d.ia !== "reecrite") || !!d.iaOutils, {
    message: "ia: \"assistee\" ou \"reecrite\" exige iaOutils (ex. \"Claude Code\")",
    path: ["iaOutils"],
  })
  .refine((d) => !d.certificatHumain || d.ia !== "redigee", {
    message: "un certificat d'écriture humaine ne va pas sur un article rédigé par Bob",
    path: ["certificatHumain"],
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
  /* Ce qu'on regarde, et donc ce qu'on peut croire. Le filtre de /casts
     s'appuie dessus ; le libellé vient de src/lib/casts.ts.
       reconstitution — une session Claude Code (ou Qwen Code) remontée après
                        coup à partir de sa transcription réelle
       prise-reelle   — la console capturée pour vrai par asciinema
       chat           — des réponses du chat du site, capturées mot pour mot
       simulation     — un comportement réel rejoué pour l'enregistrement */
  type: z.enum(["reconstitution", "prise-reelle", "chat", "simulation"], {
    error: "champ `type` manquant : reconstitution | prise-reelle | chat | simulation",
  }),
  /** Slug(s) of the article(s) this recording came from. Normalised to an array;
      an unknown slug fails the build (src/lib/casts.ts). */
  article: z
    .union([z.string(), z.array(z.string())])
    .optional()
    .transform((v) => (v === undefined ? [] : Array.isArray(v) ? v : [v])),
  /* « aucune » pour les enregistrements du chat du site : le cadre par défaut
     reproduit une session Claude Code, et le chat n'en est pas une. */
  session: z.enum(["claude-code", "aucune"]).optional(),
  /* « none » quand la vraie barre tmux est dans l'enregistrement (prise
     réelle attachée à la session) : l'habillage en ferait une deuxième. */
  frame: z.enum(["alacritty", "none"]).optional(),
  /* Code du lien court lbdl.dev/<court>, une 301 vers la page du cast. Même
     espace et même limite que les articles (16 caractères) : un cast prend
     un code à lui, d'habitude celui de l'article suivi de « -cast »
     (`nvme-cast`, `nvme-cast-en`). Un doublon avec un article est refusé
     après le build (scripts/check-short-links.mjs). */
  court: z
    .string()
    .regex(/^[a-z0-9-]{1,16}$/, "court : 16 caractères au plus, a-z 0-9 -")
    .optional(),
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
