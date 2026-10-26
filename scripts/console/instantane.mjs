// L'instantané public de la console : chaque fenêtre de la session tmux
// « claude », avec l'historique de sa conversation, assaini, pour la
// section console de /casts. Tourne sur la console, chaque soir.
//
//   node scripts/console/instantane.mjs --out instantane.json [--sans-relecture]
//
// POURQUOI LA TRANSCRIPTION ET PAS L'ÉCRAN. Claude Code tourne en plein écran :
// tmux ne garde aucun historique de ces fenêtres (history_size = 0), et
// capture-pane ne rend que l'écran du moment. L'historique est dans le .jsonl
// de la session, que le titre de la fenêtre retrouve (enregistrement
// « custom-title »).
//
// CE QUI EST LU : les demandes de Ludo, les réponses, et chaque appel
// d'outil réduit à une ligne (« Bash : Vérifier l'état du cluster »), jamais
// sa sortie. C'est dans les sorties que vivent les adresses, les secrets et
// les vrais noms ; on ne les assainit pas, on ne les prend pas.
//
// CE QUI EST PUBLIÉ : un récapitulatif par jour, écrit par le modèle local à
// partir de la conversation DÉJÀ assainie, jamais la conversation elle-même.
// Personne ne lisait 400 passages ; un paragraphe par jour, si.
//
// L'ASSAINISSEMENT, dans l'ordre, fenêtre par fenêtre :
//  1. exclusions privées : une fenêtre exclue n'apparaît pas du tout ;
//  2. remplacements privés, vrai → fictif (net-cfgs/console-instantane.txt) ;
//  3. caviardage générique : adresses, MAC, courriels, domaines inconnus
//     deviennent leur jumeau de documentation (allowlist.redact) ;
//  4. les gardes de check-public-leaks.mjs, liste blanche et liste noire ;
//  5. la relecture par le modèle local, qui retient ce qu'aucune liste ne sait
//     nommer d'avance : employeur, famille, santé, argent, secrets, adresses,
//     et les failles encore ouvertes qu'un inconnu pourrait exploiter.
// Une garde qui touche RETIRE le passage, puis ce qui reste est vérifié de
// nouveau ; jamais rien n'est réécrit. Le récapitulatif repasse ensuite les
// mêmes gardes : touché, il est retiré, et sa journée le dit. Une
// fenêtre n'est retenue en entier que si le sujet lui-même est privé (plus du
// quart à retirer) ou si la relecture ne se satisfait pas. Elle ne bloque
// jamais les autres. Une erreur, elle, n'écrit rien du tout : modèle
// injoignable, liste noire absente, transcription illisible — pas
// d'instantané plutôt qu'un instantané moins gardé.
//
// Le rapport détaillé (quelle garde, quelle entrée) va sur stderr, qui reste
// sur la console : il ne doit jamais suivre l'instantané.
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, readdirSync, renameSync, statSync, unlinkSync, utimesSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join } from "node:path";
import { PUBLIC_RULES, allowlistHits, loadDenylist, redactTexts } from "../lib/public-gate.mjs";

const arg = (name, dflt) => {
  const i = process.argv.indexOf(`--${name}`);
  return i < 0 ? dflt : process.argv[i + 1];
};
const flag = (name) => process.argv.includes(`--${name}`);

const OUT = arg("out");
const CONFIG = arg("config", join(homedir(), "git/ludorl82/net-cfgs/console-instantane.txt"));
const PROJECTS = arg("projects", join(homedir(), ".claude/projects"));
const SOCKET = arg("socket", "console");
const SESSION = arg("session", "claude");
const OLLAMA = arg("ollama", "http://bob:11434");
const MODEL = arg("model", "qwen38-27b");
const CACHE = arg("cache", join(homedir(), ".cache/console-instantane"));
const SANS_RELECTURE = flag("sans-relecture");

const MAX_ENTRIES = 400; // par fenêtre, les plus récentes, en journées entières
const MAX_CHARS = 6000; // par entrée
const CHUNK_CHARS = 6000; // par appel au modèle : au-delà, le 27B rate des passages (banc du 2026-10-12)
const DAY_CHARS = 36000; // par récapitulatif : tient dans num_ctx 16384 avec la réponse
const TZ = "America/Toronto";
const DAY = new Intl.DateTimeFormat("en-CA", { timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit" });
const jour = (iso) => DAY.format(new Date(iso));

/* Domaines publics que la console cite sans rien révéler du labo : de la
   documentation et des fournisseurs. Tout autre domaine devient site.example. */
const PUBLIC_SUFFIX = [
  "anthropic.com", "claude.ai", "claude.com", "astro.build", "nixos.org", "nixos.wiki",
  "github.io", "githubusercontent.com", "npmjs.com", "python.org", "kubernetes.io",
  "k3s.io", "cloudflare.com", "amazon.com", "home-assistant.io", "esphome.io",
  "ollama.com", "huggingface.co", "qwen.ai", "alibabacloud.com", "letsencrypt.org",
  "mozilla.org", "wikipedia.org", "stackoverflow.com", "youtube.com", "linkedin.com",
  "google.com", "microsoft.com", "apple.com", "ubuntu.com", "debian.org",
  "archlinux.org", "docker.com", "docker.io", "grafana.com", "asciinema.org",
  "nvidia.com", "supermicro.com", "ui.com", "netgate.com", "pfsense.org",
  "tailscale.com", "humanums.com", "libvirt.org", "kernel.org", "freedesktop.org",
];

const log = (...a) => console.error("instantane:", ...a);

/* --- configuration privée --------------------------------------------- */

function loadConfig() {
  if (!existsSync(CONFIG)) throw new Error(`configuration privée absente : ${CONFIG}`);
  const exclude = [];
  const replace = [];
  for (const [i, raw] of readFileSync(CONFIG, "utf8").split("\n").entries()) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const bar = line.indexOf("|");
    const verb = line.slice(0, bar).trim();
    const rest = line.slice(bar + 1).trim();
    if (verb === "exclure") exclude.push(new RegExp(rest, "iu"));
    else if (verb === "remplacer") {
      const [re, to] = rest.split(/\s+=>\s+/);
      replace.push([new RegExp(re, "giu"), to ?? ""]);
    } else throw new Error(`${CONFIG}:${i + 1} : « exclure | … » ou « remplacer | … => … »`);
  }
  return { exclude, replace };
}

/* --- tmux et transcriptions ------------------------------------------- */

function windows() {
  const out = execFileSync(
    "tmux",
    ["-L", SOCKET, "list-windows", "-t", SESSION, "-F", "#{window_index}\t#{window_name}\t#{window_active}\t#{window_activity}"],
    { encoding: "utf8" },
  );
  return out
    .trim()
    .split("\n")
    .map((l) => {
      const [index, name, active, activity] = l.split("\t");
      return { index: Number(index), name, active: active === "1", activity: new Date(Number(activity) * 1000) };
    });
}

/* Titre → transcription la plus récente qui le porte comme DERNIER titre. Un
   titre se renomme ; c'est le dernier qui nomme la fenêtre. */
function transcriptsByTitle() {
  const map = new Map();
  for (const dir of readdirSync(PROJECTS)) {
    const full = join(PROJECTS, dir);
    if (!statSync(full).isDirectory()) continue;
    for (const f of readdirSync(full)) {
      if (!f.endsWith(".jsonl")) continue;
      const path = join(full, f);
      const text = readFileSync(path, "utf8");
      let title = null;
      for (const m of text.matchAll(/"type":"custom-title","customTitle":"((?:[^"\\]|\\.)*)"/g)) title = JSON.parse(`"${m[1]}"`);
      if (!title) continue;
      const mtime = statSync(path).mtimeMs;
      const prev = map.get(title);
      if (!prev || prev.mtime < mtime) map.set(title, { path, mtime });
    }
  }
  return map;
}

function cleanUserText(s) {
  return s
    .replace(/<system-reminder[\s\S]*?<\/system-reminder>/g, "")
    .replace(/<pasted_content[\s\S]*?<\/pasted_content>/g, "[contenu collé]")
    .replace(/<command-name>([\s\S]*?)<\/command-name>[\s\S]*/g, "$1")
    .replace(/<local-command-[\s\S]*?<\/local-command-[a-z]+>/g, "")
    .trim();
}

function toolLine(b) {
  const i = b.input ?? {};
  const short = b.name.startsWith("mcp__") ? b.name.split("__").slice(1).join(" · ") : b.name;
  switch (b.name) {
    case "Bash":
      return `Bash : ${i.description ?? "commande"}`;
    case "Read":
    case "Write":
    case "Edit":
    case "NotebookEdit":
      return `${b.name} : ${basename(i.file_path ?? i.notebook_path ?? "")}`;
    case "Agent":
    case "Task":
      return `Agent : ${i.description ?? ""}`;
    case "WebSearch":
      return `Recherche web : ${i.query ?? ""}`;
    case "Skill":
      return `Skill : ${i.skill ?? ""}`;
    case "AskUserQuestion":
      return null; // rendu avec ses réponses, voir plus bas
    default:
      return short;
  }
}

/* La branche active de la conversation : de la dernière entrée vers le haut
   par parentUuid, en enjambant les compactages par logicalParentUuid. Les
   retours en arrière laissent des branches mortes dans le fichier ; on ne les
   montre pas. */
function entriesOf(path) {
  const recs = [];
  for (const l of readFileSync(path, "utf8").split("\n")) {
    if (!l) continue;
    try {
      recs.push(JSON.parse(l));
    } catch {
      /* ligne coupée par une écriture en cours */
    }
  }
  const byUuid = new Map(recs.filter((r) => r.uuid).map((r) => [r.uuid, r]));
  let leaf = null;
  for (const r of recs) if ((r.type === "user" || r.type === "assistant") && !r.isSidechain) leaf = r;
  const chain = [];
  const seen = new Set();
  for (let cur = leaf; cur && !seen.has(cur.uuid); ) {
    seen.add(cur.uuid);
    chain.push(cur);
    cur = byUuid.get(cur.parentUuid) ?? byUuid.get(cur.logicalParentUuid);
  }
  chain.reverse();

  const asked = new Map(); // tool_use id → questions
  const out = [];
  const push = (r, t, at) => {
    if (t && t.trim()) out.push({ r, t: t.length > MAX_CHARS ? `${t.slice(0, MAX_CHARS)} […]` : t, at });
  };
  for (const rec of chain) {
    const at = rec.timestamp;
    if (rec.type === "attachment" && rec.attachment?.type === "queued_command") {
      const p = String(rec.attachment.prompt ?? "");
      if (!p.startsWith("<")) push("u", cleanUserText(p), at);
      continue;
    }
    if (rec.type === "system" && rec.subtype === "compact_boundary") {
      push("n", "— conversation compactée —", at);
      continue;
    }
    if (rec.type !== "user" && rec.type !== "assistant") continue;
    if (rec.isMeta || rec.isCompactSummary || rec.isSidechain) continue;
    const content = rec.message?.content;
    if (rec.type === "user") {
      if (typeof content === "string") {
        if (!content.startsWith("<task-notification") && !content.startsWith("<agent-message")) push("u", cleanUserText(content), at);
        continue;
      }
      for (const b of content ?? []) {
        if (b.type === "text") push("u", cleanUserText(b.text), at);
        else if (b.type === "image") push("u", "[image]", at);
        else if (b.type === "tool_result" && asked.has(b.tool_use_id)) {
          const answers = rec.toolUseResult?.answers ?? {};
          const lines = asked.get(b.tool_use_id).map((q) => `${q} → ${answers[q] ?? "(sans réponse)"}`);
          push("u", lines.join("\n"), at);
        }
      }
      continue;
    }
    for (const b of content ?? []) {
      if (b.type === "text") push("a", b.text, at);
      else if (b.type === "tool_use") {
        if (b.name === "AskUserQuestion") {
          const qs = (b.input?.questions ?? []).map((q) => q.question);
          asked.set(b.id, qs);
          push("t", `Question : ${qs.join(" / ")}`, at);
        } else push("t", toolLine(b), at);
      }
    }
  }
  // `n` : le rang dans toute la conversation, stable d'un soir à l'autre
  // (la relecture le cite, et son cache en dépend).
  const all = out.map((e, n) => ({ ...e, n }));
  if (all.length <= MAX_ENTRIES) return all;
  // La coupe tombe au milieu d'une journée : ce début de journée ne se
  // résumerait pas en entier, et son récapitulatif changerait chaque soir.
  // Il part avec le reste.
  const kept = all.slice(-MAX_ENTRIES);
  const cut = jour(kept[0].at);
  return kept.filter((e) => jour(e.at) !== cut);
}

/* --- gardes ------------------------------------------------------------ */

const SESSION_LINK = /https?:\/\/claude\.ai\/code\/session_\w+/g;
/* Une clé publique n'est pas un secret, mais c'est un identifiant : elle relie
   une machine du labo à ce qu'on en dit ailleurs. */
const SSH_KEY = /\b(ssh-(?:ed25519|rsa|ecdsa[\w-]*)) AAAA[\w+/=]+/g;

function sanitize(texts, config) {
  let t = texts.map((s) => {
    let v = s.replace(SESSION_LINK, "[lien de session]").replace(SSH_KEY, "$1 AAAA…");
    for (const [re, to] of config.replace) v = v.replace(re, to);
    return v;
  });
  t = redactTexts(t, PUBLIC_SUFFIX);
  return t;
}

/** Toutes les touches des gardes de liste : Map index → première étiquette. */
function listHits(texts, deny) {
  const pub = allowlistHits(texts, PUBLIC_SUFFIX);
  const hits = new Map();
  for (let i = 0; i < texts.length; i++) {
    if (pub.has(i)) {
      hits.set(i, pub.get(i));
      continue;
    }
    for (const [label, re] of [...PUBLIC_RULES, ...deny.rules]) {
      if (re.test(texts[i])) {
        hits.set(i, label);
        break;
      }
    }
  }
  return hits;
}

const CATEGORIES = ["employeur", "famille", "sante", "argent", "secret", "adresse", "faille"];
const PROMPT_VERSION = "3";
const SYSTEM = `Tu es une garde de confidentialité. On te donne un extrait d'une session de travail entre Ludo et un assistant de programmation, découpé en passages numérotés [n]. L'extrait sera PUBLIÉ sur son site web.

Ce qui est PUBLIC et ne doit PAS être signalé : le travail technique sur son labo maison (serveurs, réseau, Kubernetes, NixOS, domotique, modèles d'IA), ses projets à venir, ses articles de blogue, ses chiens Bob et Stella, et les noms d'hôte, adresses et domaines, qui ont déjà été remplacés par des valeurs fictives.

Signale chaque passage qui contient quelque chose de l'une de ces catégories :
- employeur : le nom de l'employeur de Ludo, ou son travail pour lui ;
- famille : un proche nommé, la vie de famille, la conjointe, les enfants ;
- sante : la santé de Ludo ou d'un proche ;
- argent : finances personnelles (comptes, revenus, dettes, montants personnels) ;
- secret : un mot de passe, jeton, clé ou code écrit en clair ;
- adresse : une adresse postale, un numéro de téléphone, un courriel personnel ;
- faille : une faiblesse de sécurité ENCORE en place qu'un inconnu pourrait exploiter (un compte sans mot de passe, un service ouvert sans chiffrement ou avec un mot de passe faible, un port exposé, une protection désactivée). Une faille corrigée dans le même passage, ou une mesure de sécurité décrite, n'en est pas une.

Donne le numéro [n] de CHAQUE passage concerné, pas seulement le premier : les passages signalés seront retirés, le reste sera publié. Dans le doute, signale. Réponds en JSON.`;

function cacheGet(key) {
  const p = join(CACHE, `${key}.json`);
  if (!existsSync(p)) return null;
  const now = new Date();
  utimesSync(p, now, now); // servi ce soir : l'élagage le garde
  return JSON.parse(readFileSync(p, "utf8"));
}

/* Une tranche que plus aucune fenêtre ne produit ne sera plus jamais
   demandée : un verdict qui n'a pas servi depuis 30 jours part. */
function cachePrune() {
  if (!existsSync(CACHE)) return;
  const limit = Date.now() - 30 * 86400_000;
  for (const f of readdirSync(CACHE)) {
    const p = join(CACHE, f);
    if (statSync(p).mtimeMs < limit) unlinkSync(p);
  }
}
function cachePut(key, v) {
  mkdirSync(CACHE, { recursive: true });
  writeFileSync(join(CACHE, `${key}.json`), JSON.stringify(v));
}

/** Un appel au modèle local, réponse JSON selon `format`. */
async function ask(what, system, user, format) {
  const res = await fetch(`${OLLAMA}/api/chat`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      model: MODEL,
      stream: false,
      think: false,
      messages: [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
      format,
      options: { temperature: 0, num_ctx: 65536 }, // la valeur de tous les appelants de bob (2026-10-25)
    }),
    signal: AbortSignal.timeout(600_000),
  });
  if (!res.ok) throw new Error(`${what} : HTTP ${res.status}`);
  return JSON.parse((await res.json()).message.content);
}

/** Les numéros de passage que le modèle signale dans une tranche. */
async function review(chunk) {
  const key = createHash("sha256").update(`${PROMPT_VERSION}\0${MODEL}\0${chunk.text}`).digest("hex");
  const hit = cacheGet(key);
  if (hit) return hit;
  const verdict = await ask("relecture", SYSTEM, `Extrait :\n\n${chunk.text}`, {
    type: "object",
    properties: {
      passages: {
        type: "array",
        items: {
          type: "object",
          properties: { n: { type: "integer" }, categorie: { type: "string", enum: CATEGORIES } },
          required: ["n", "categorie"],
        },
      },
    },
    required: ["passages"],
  });
  const passages = (verdict.passages ?? []).filter((p) => CATEGORIES.includes(p.categorie));
  // Un numéro qui n'est pas dans la tranche ne désigne rien : le modèle a
  // signalé quelque chose sans dire où. On ne sait pas quoi retirer, alors la
  // tranche entière l'est.
  const known = new Set(chunk.ns);
  const v = passages.some((p) => !known.has(p.n))
    ? { passages: chunk.ns.map((n) => ({ n, categorie: passages[0].categorie })) }
    : { passages };
  cachePut(key, v);
  return v;
}

/* Des tranches qui restent les mêmes d'un soir à l'autre, sinon le cache ne
   sert à rien : la fenêtre garde ses 400 dernières entrées, son début glisse
   chaque soir, et une coupe tous les N caractères depuis le début décalerait
   toutes les tranches. La coupe se décide donc sur le contenu (après une
   entrée dont l'empreinte finit par 0, passé la moitié de la taille), comme
   un découpage rsync : seules les tranches qui ont vraiment changé repassent
   devant le modèle. Chaque passage porte son rang dans la conversation. */
function chunks(entries) {
  const label = { u: "Ludo", a: "Assistant", t: "[outil]", n: "" };
  const out = [];
  let cur = { text: "", ns: [] };
  for (const e of entries) {
    const line = `[${e.n}] ${label[e.r]} ${e.t}\n\n`;
    if (cur.text && cur.text.length + line.length > CHUNK_CHARS) {
      out.push(cur);
      cur = { text: "", ns: [] };
    }
    cur.text += line;
    cur.ns.push(e.n);
    const h = createHash("sha256").update(line).digest()[0];
    if (cur.text.length > CHUNK_CHARS / 2 && h % 4 === 0) {
      out.push(cur);
      cur = { text: "", ns: [] };
    }
  }
  if (cur.text) out.push(cur);
  return out;
}

const RETIRE = "— passage retiré par la garde —";
/* Au-delà, ce n'est plus un passage qui est privé, c'est le sujet : la
   fenêtre est retenue au lieu d'être publiée en gruyère. */
const MAX_RETRAIT = 0.25;
const TOURS = 3;

/** Remplace les entrées retirées par une seule marque par suite. */
function retirer(entries, drop) {
  const out = [];
  for (const e of entries) {
    if (!drop.has(e.n)) out.push(e);
    else if (out.at(-1)?.t !== RETIRE) out.push({ r: "n", t: RETIRE, at: e.at, n: e.n });
  }
  return out;
}

/* --- récapitulatifs ---------------------------------------------------- */

const RESUME_VERSION = "1";
const SYSTEM_RESUME = `Tu résumes une journée de travail entre Ludo et Claude, un assistant de programmation, dans son labo maison. Le résumé sera publié sur son site, sous la date du jour, pour des visiteurs qui veulent savoir sur quoi il travaille.

Écris en français, au passé composé, en 2 à 4 phrases, un seul paragraphe, sans liste ni Markdown. Dis ce que Ludo cherchait à faire, ce qui a été fait ou décidé, et où ça en est à la fin de la journée. Appelle-les « Ludo » et « Claude ». N'ajoute rien qui ne soit pas dans l'extrait : aucun chiffre, aucun nom, aucune cause qu'il ne donne pas. Réponds en JSON.`;

/** Le texte d'une journée pour le modèle : sans les outils s'il est trop
    long, puis des entrées raccourcies, puis la fin seulement. */
function dayText(entries) {
  const label = { u: "Ludo :", a: "Claude :", t: "[outil]" };
  const render = (es, max) => es.map((e) => `${label[e.r]} ${e.t.length > max ? `${e.t.slice(0, max)} […]` : e.t}`).join("\n\n");
  let text = render(entries, 1500);
  if (text.length > DAY_CHARS) text = render(entries.filter((e) => e.r !== "t"), 600);
  return text.length > DAY_CHARS ? text.slice(-DAY_CHARS) : text;
}

async function resume(text) {
  const key = createHash("sha256").update(`resume\0${RESUME_VERSION}\0${MODEL}\0${text}`).digest("hex");
  const hit = cacheGet(key);
  if (hit) return hit.resume;
  const v = await ask("récapitulatif", SYSTEM_RESUME, `Journée :\n\n${text}`, {
    type: "object",
    properties: { resume: { type: "string" } },
    required: ["resume"],
  });
  cachePut(key, { resume: v.resume });
  return v.resume;
}

/** Un récapitulatif par journée, chacun repassé devant les gardes : touché,
    il est retiré, pas réécrit. */
async function recapitulatifs(w, safe, config, deny) {
  const days = new Map();
  for (const e of safe) {
    if (e.r === "n") continue;
    const d = jour(e.at);
    if (!days.has(d)) days.set(d, []);
    days.get(d).push(e);
  }
  const out = [];
  for (const [date, es] of days) {
    // Une journée où Claude n'a rien répondu (un /compact, des outils seuls)
    // n'a rien à raconter : le modèle en ferait une « opération de maintenance ».
    if (!es.some((e) => e.r === "a")) continue;
    const [text] = sanitize([await resume(dayText(es))], config);
    const hit = listHits([text], deny).get(0);
    const flagged = hit ? null : (await review({ text: `[0] ${text}\n\n`, ns: [0] })).passages[0]?.categorie;
    if (hit || flagged) {
      log(`${w.index}:${w.name} — récapitulatif du ${date} retiré, ${hit ? `garde « ${hit} »` : `relecture « ${flagged} »`}`);
      out.push({ date, retire: true });
    } else out.push({ date, resume: text });
  }
  return out;
}

/* --- assemblage -------------------------------------------------------- */

const config = loadConfig();
const deny = loadDenylist();
if (!deny) throw new Error("liste noire privée absente : pas d'instantané moins gardé");
if (!OUT) throw new Error("--out <fichier> manquant");

const byTitle = transcriptsByTitle();
const result = [];
for (const w of windows()) {
  if (config.exclude.some((re) => re.test(w.name))) {
    log(`${w.index}:${w.name} — exclue`);
    continue;
  }
  const src = byTitle.get(w.name);
  const entries = src ? entriesOf(src.path) : [];
  const texts = sanitize([w.name, ...entries.map((e) => e.t)], config);
  let [name, ...clean] = texts;
  let safe = entries.map((e, i) => ({ ...e, t: clean[i] }));
  const base = { index: w.index, active: w.active, activity: w.activity.toISOString() };
  const retenue = (why, reason) => {
    log(`${w.index}:${w.name} — retenue, ${why}`);
    result.push({ ...base, name, status: "retenue", reason });
  };

  // 1. Les gardes de liste, passage par passage. Un nom de fenêtre touché
  //    devient « fenêtre N » ; une entrée touchée est retirée.
  const hits = listHits([name, ...safe.map((e) => e.t)], deny);
  if (hits.has(0)) {
    log(`${w.index}:${w.name} — nom touché (« ${hits.get(0)} »), renommée`);
    name = `fenêtre ${w.index}`;
  }
  const dropped = new Set();
  for (const [i, label] of hits) {
    if (i === 0) continue;
    dropped.add(safe[i - 1].n);
    log(`${w.index}:${w.name} — entrée ${safe[i - 1].n} retirée, garde « ${label} »`);
  }
  safe = retirer(safe, dropped);

  if (!src) {
    log(`${w.index}:${w.name} — aucune transcription trouvée`);
    result.push({ ...base, name, status: "publiee", jours: [] });
    continue;
  }

  // 2. La relecture, jusqu'à ce qu'elle ne signale plus rien : ce qui reste
  //    après un retrait est relu à nouveau, parce qu'une réponse voisine peut
  //    encore porter ce que le passage retiré disait.
  let propre = SANS_RELECTURE;
  for (let tour = 0; !propre && tour < TOURS; tour++) {
    const flagged = new Map();
    for (const c of chunks(safe.filter((e) => e.t !== RETIRE)))
      for (const p of (await review(c)).passages) flagged.set(p.n, p.categorie);
    if (!flagged.size) propre = true;
    for (const [n, cat] of flagged) {
      dropped.add(n);
      log(`${w.index}:${w.name} — entrée ${n} retirée, relecture « ${cat} » (tour ${tour + 1})`);
    }
    safe = retirer(safe, dropped);
  }

  // 3. Une dernière passe des gardes de liste sur ce qui sera publié : elle
  //    ne doit plus rien trouver. Si elle trouve, c'est un bogue ici.
  if (listHits([name, ...safe.map((e) => e.t)], deny).size) {
    retenue("garde encore touchée après retrait", "garde");
    continue;
  }
  if (!propre) {
    retenue(`relecture toujours insatisfaite après ${TOURS} tours`, "relecture");
    continue;
  }
  if (dropped.size > MAX_RETRAIT * entries.length) {
    retenue(`${dropped.size} entrées sur ${entries.length} à retirer`, hits.size ? "garde" : "relecture");
    continue;
  }
  const jours = await recapitulatifs(w, safe, config, deny);
  log(`${w.index}:${w.name} — publiée, ${jours.length} jour(s), ${entries.length - dropped.size} entrées lues, ${dropped.size} retirée(s) (${basename(src.path)})`);
  result.push({ ...base, name, status: "publiee", retirees: dropped.size, jours });
}

const doc = {
  version: 2,
  generated: new Date().toISOString(),
  session: SESSION,
  relu: !SANS_RELECTURE,
  windows: result,
};
cachePrune();
mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(`${OUT}.tmp`, JSON.stringify(doc));
renameSync(`${OUT}.tmp`, OUT);
log(`écrit ${OUT} : ${result.filter((w) => w.status === "publiee").length} publiée(s), ${result.filter((w) => w.status === "retenue").length} retenue(s)`);
