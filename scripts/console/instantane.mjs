// L'instantané public de la console : chaque fenêtre de la session tmux
// « claude », avec l'historique de sa conversation, assaini, pour la page
// /console. Tourne sur la console, chaque soir.
//
//   node scripts/console/instantane.mjs --out instantane.json [--sans-relecture]
//
// POURQUOI LA TRANSCRIPTION ET PAS L'ÉCRAN. Claude Code tourne en plein écran :
// tmux ne garde aucun historique de ces fenêtres (history_size = 0), et
// capture-pane ne rend que l'écran du moment. L'historique est dans le .jsonl
// de la session, que le titre de la fenêtre retrouve (enregistrement
// « custom-title »).
//
// CE QUI EST MONTRÉ : les demandes de Ludo, les réponses, et chaque appel
// d'outil réduit à une ligne (« Bash : Vérifier l'état du cluster »), jamais
// sa sortie. C'est dans les sorties que vivent les adresses, les secrets et
// les vrais noms ; on ne les assainit pas, on ne les prend pas.
//
// L'ASSAINISSEMENT, dans l'ordre, fenêtre par fenêtre :
//  1. exclusions privées : une fenêtre exclue n'apparaît pas du tout ;
//  2. remplacements privés, vrai → fictif (net-cfgs/console-instantane.txt) ;
//  3. caviardage générique : adresses, MAC, courriels, domaines inconnus
//     deviennent leur jumeau de documentation (allowlist.redact) ;
//  4. les gardes de check-public-leaks.mjs, liste blanche et liste noire ;
//  5. la relecture par le modèle local, qui retient ce qu'aucune liste ne sait
//     nommer d'avance : employeur, famille, santé, argent, secrets, adresses.
// Une garde qui touche RETIENT la fenêtre ce soir-là (elle apparaît, vide,
// avec une raison générique) ; elle ne la réécrit jamais et ne bloque pas les
// autres. Une erreur, elle, n'écrit rien du tout : modèle injoignable, liste
// noire absente, transcription illisible — pas d'instantané plutôt qu'un
// instantané moins gardé.
//
// Le rapport détaillé (quelle garde, quelle entrée) va sur stderr, qui reste
// sur la console : il ne doit jamais suivre l'instantané.
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, readdirSync, renameSync, statSync, writeFileSync } from "node:fs";
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

const MAX_ENTRIES = 400; // par fenêtre, les plus récentes
const MAX_CHARS = 6000; // par entrée
const CHUNK_CHARS = 16000; // par appel au modèle

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
  return out.slice(-MAX_ENTRIES);
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

/** Première touche des gardes de liste, ou null. */
function listGate(texts, deny) {
  const pub = allowlistHits(texts, PUBLIC_SUFFIX);
  for (let i = 0; i < texts.length; i++) {
    if (pub.has(i)) return { i, label: pub.get(i) };
    for (const [label, re] of PUBLIC_RULES) if (re.test(texts[i])) return { i, label };
    for (const [label, re] of deny.rules) if (re.test(texts[i])) return { i, label };
  }
  return null;
}

const CATEGORIES = ["employeur", "famille", "sante", "argent", "secret", "adresse"];
const PROMPT_VERSION = "1";
const SYSTEM = `Tu es une garde de confidentialité. On te donne un extrait d'une session de travail entre Ludo et un assistant de programmation. L'extrait sera PUBLIÉ sur son site web.

Ce qui est PUBLIC et ne doit PAS être signalé : le travail technique sur son labo maison (serveurs, réseau, Kubernetes, NixOS, domotique, modèles d'IA), ses projets à venir, ses articles de blogue, ses chiens Bob et Stella, et les noms d'hôte, adresses et domaines, qui ont déjà été remplacés par des valeurs fictives.

Signale seulement ce qui appartient à l'une de ces catégories :
- employeur : le nom de l'employeur de Ludo, ou son travail pour lui ;
- famille : un proche nommé, la vie de famille, la conjointe, les enfants ;
- sante : la santé de Ludo ou d'un proche ;
- argent : finances personnelles (comptes, revenus, dettes, montants personnels) ;
- secret : un mot de passe, jeton, clé ou code écrit en clair ;
- adresse : une adresse postale, un numéro de téléphone, un courriel personnel.

Dans le doute sur une de ces catégories, signale-la. Réponds en JSON.`;

function cacheGet(key) {
  const p = join(CACHE, `${key}.json`);
  return existsSync(p) ? JSON.parse(readFileSync(p, "utf8")) : null;
}
function cachePut(key, v) {
  mkdirSync(CACHE, { recursive: true });
  writeFileSync(join(CACHE, `${key}.json`), JSON.stringify(v));
}

async function review(chunk) {
  const key = createHash("sha256").update(`${PROMPT_VERSION}\0${MODEL}\0${chunk}`).digest("hex");
  const hit = cacheGet(key);
  if (hit) return hit;
  const res = await fetch(`${OLLAMA}/api/chat`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      model: MODEL,
      stream: false,
      think: false,
      messages: [
        { role: "system", content: SYSTEM },
        { role: "user", content: `Extrait :\n\n${chunk}` },
      ],
      format: {
        type: "object",
        properties: { categories: { type: "array", items: { type: "string", enum: CATEGORIES } } },
        required: ["categories"],
      },
      options: { temperature: 0, num_ctx: 16384 },
    }),
    signal: AbortSignal.timeout(600_000),
  });
  if (!res.ok) throw new Error(`relecture : HTTP ${res.status}`);
  const body = await res.json();
  const verdict = JSON.parse(body.message.content);
  const cats = (verdict.categories ?? []).filter((c) => CATEGORIES.includes(c));
  const v = { categories: [...new Set(cats)] };
  cachePut(key, v);
  return v;
}

/* Des tranches qui restent les mêmes d'un soir à l'autre, sinon le cache ne
   sert à rien : la fenêtre garde ses 400 dernières entrées, son début glisse
   chaque soir, et une coupe tous les N caractères depuis le début décalerait
   toutes les tranches. La coupe se décide donc sur le contenu (après une
   entrée dont l'empreinte finit par 0, passé la moitié de la taille), comme
   un découpage rsync : seules les tranches qui ont vraiment changé repassent
   devant le modèle. */
function chunks(entries) {
  const label = { u: "Ludo", a: "Assistant", t: "[outil]", n: "" };
  const out = [];
  let cur = "";
  for (const e of entries) {
    const line = `${label[e.r]} ${e.t}\n\n`;
    if (cur && cur.length + line.length > CHUNK_CHARS) {
      out.push(cur);
      cur = "";
    }
    cur += line;
    const h = createHash("sha256").update(line).digest()[0];
    if (cur.length > CHUNK_CHARS / 2 && h % 4 === 0) {
      out.push(cur);
      cur = "";
    }
  }
  if (cur) out.push(cur);
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
  const [name, ...clean] = texts;
  const safe = entries.map((e, i) => ({ ...e, t: clean[i] }));
  const base = { index: w.index, active: w.active, activity: w.activity.toISOString() };

  const hit = listGate(texts, deny);
  if (hit) {
    log(`${w.index}:${w.name} — retenue, garde « ${hit.label} » (${hit.i === 0 ? "nom" : `entrée ${hit.i - 1}`})`);
    result.push({ ...base, name: hit.i === 0 ? `fenêtre ${w.index}` : name, status: "retenue", reason: "garde" });
    continue;
  }
  if (!src) {
    log(`${w.index}:${w.name} — aucune transcription trouvée`);
    result.push({ ...base, name, status: "publiee", entries: [] });
    continue;
  }

  let cats = [];
  if (!SANS_RELECTURE) {
    for (const c of chunks(safe)) cats.push(...(await review(c)).categories);
    cats = [...new Set(cats)];
  }
  if (cats.length) {
    log(`${w.index}:${w.name} — retenue, relecture : ${cats.join(", ")}`);
    result.push({ ...base, name, status: "retenue", reason: "relecture" });
    continue;
  }
  log(`${w.index}:${w.name} — publiée, ${safe.length} entrées (${basename(src.path)})`);
  result.push({ ...base, name, status: "publiee", entries: safe });
}

const doc = {
  version: 1,
  generated: new Date().toISOString(),
  session: SESSION,
  relu: !SANS_RELECTURE,
  windows: result,
};
mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(`${OUT}.tmp`, JSON.stringify(doc));
renameSync(`${OUT}.tmp`, OUT);
log(`écrit ${OUT} : ${result.filter((w) => w.status === "publiee").length} publiée(s), ${result.filter((w) => w.status === "retenue").length} retenue(s)`);
