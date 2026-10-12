// Les deux moitiés de la garde publique, partagées par check-public-leaks.mjs
// (les casts, au déploiement) et console/instantane.mjs (la console, chaque
// soir). Voir l'en-tête de check-public-leaks.mjs pour le pourquoi.
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const ROOT = new URL("../..", import.meta.url).pathname;

/* Formes publiques sans lecture innocente. La liste blanche couvre déjà les
   adresses IP, les courriels et les noms de domaine. */
export const PUBLIC_RULES = [
  ["clé privée", /BEGIN [A-Z ]*PRIVATE KEY/],
  ["clé AWS", /\bAKIA[0-9A-Z]{16}\b/],
  ["jeton", /\b(sk-ant-[\w-]{10,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_\w{20,}|xox[abprs]-[\w-]{10,})/],
  ["JWT", /eyJ[\w-]{10,}\.eyJ[\w-]{10,}/],
  ["jeton de sonde", /api\/push\/(?!EXAMPLE)[A-Za-z0-9]{8,}/],
  ["lien de session", /claude\.ai\/code\/session_\w+/],
  ["adresse MAC", /\b(?!02:00:00:00:)([0-9a-f]{2}:){5}[0-9a-f]{2}\b/i],
  ["numéro de série", /\b(ata|nvme)-(?!EXAMPLE)[A-Za-z0-9]+_\w+/],
];

export function loadDenylist() {
  let text = process.env.PUBLIC_DENYLIST;
  let from = "PUBLIC_DENYLIST";
  if (!text) {
    const file =
      process.env.PUBLIC_DENYLIST_FILE ??
      join(homedir(), "git/ludorl82/net-cfgs/public-denylist.txt");
    if (!existsSync(file)) return null;
    text = readFileSync(file, "utf8");
    from = file;
  }
  let key = null;
  const rules = [];
  for (const [i, raw] of text.split("\n").entries()) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    if (line.startsWith("!cle ")) {
      key = line.slice(5).trim();
      continue;
    }
    // « étiquette | regex », drapeaux iu. « étiquette [u] | regex » change les
    // drapeaux : u seul quand la casse distingue un nom propre d'un mot
    // courant. Pas de troisième champ : une regex contient déjà des |.
    const bar = line.indexOf("|");
    if (bar < 0) throw new Error(`${from}:${i + 1} : « étiquette [drapeaux] | regex » attendu`);
    const m = line.slice(0, bar).trim().match(/^(.*?)(?:\s*\[([a-z]+)\])?$/);
    rules.push([m[1], new RegExp(line.slice(bar + 1).trim(), m[2] ?? "iu")]);
  }
  if (!key) throw new Error(`${from} : ligne « !cle <hex> » manquante`);
  return { key, rules, from };
}

function scanLines(mode, input) {
  const r = spawnSync("python3", [join(ROOT, "scripts/topology/scan-lines.py"), ...(mode ? [mode] : [])], {
    input: JSON.stringify(input),
    encoding: "utf8",
    maxBuffer: 256 * 1024 * 1024,
  });
  if (r.status !== 0) throw new Error(`scan-lines.py : ${r.stderr}`);
  return JSON.parse(r.stdout);
}

/** La liste blanche de scripts/topology/allowlist.py sur une liste de textes :
    Map index → type de touche (jamais la valeur). `suffix` : domaines publics
    admis en plus (la console cite de la documentation, pas l'infrastructure). */
export function allowlistHits(texts, suffix = []) {
  return new Map(suffix.length ? scanLines("--suffix", { texts, suffix }) : scanLines("", texts));
}

/** allowlist.redact() : chaque adresse, courriel ou domaine refusé devient son
    jumeau de documentation. Rétrécit seulement ; allowlistHits() doit encore
    passer après. */
export function redactTexts(texts, suffix = []) {
  return scanLines("--redact", { texts, suffix });
}
