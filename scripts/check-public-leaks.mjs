// La garde des enregistrements de terminal : rien du vrai labo ne passe à
// l'écran d'un cast, ni dans sa fiche.
//
//   node scripts/check-public-leaks.mjs [fichier …]
//
// Sans argument : public/casts/*.cast et src/content/casts{,-en}/*.md.
//
// Un cast ne se lit pas comme un fichier texte. Le mot est rarement d'un bloc
// dans le flux : zsh l'écrit lettre par lettre entre deux redessins de la
// suggestion automatique, une barre tmux le recouvre, un \r le réécrit. On le
// rejoue donc dans un vrai émulateur (@xterm/headless) et on lit l'écran après
// chaque événement, ligne par ligne, comme un visiteur le verrait. Le flux
// brut, débarrassé de ses séquences d'échappement, passe aussi : un mot écrit
// puis effacé dans le même événement n'existe que là. Seulement devant les
// règles nettes, pas devant la liste blanche : le flux colle les redessins de
// la barre tmux bout à bout, et ses heures mises à la file ressemblent à de
// l'IPv6 (vu sur les deux prises de la mauvaise patte).
//
// Deux moitiés, comme les gardes des dépôts *-iac :
//
//  - publique : la liste blanche de scripts/topology/allowlist.py (adresses de
//    documentation, domaines de la famille example) et quelques formes sans
//    lecture innocente (clés, jetons, MAC), plus bas ;
//  - privée : la liste noire du vrai inventaire. L'écrire ici serait la fuite,
//    alors elle vient de la variable PUBLIC_DENYLIST (secret du dépôt en CI)
//    ou du fichier PUBLIC_DENYLIST_FILE, par défaut
//    ~/git/ludorl82/net-cfgs/public-denylist.txt. Une ligne par règle :
//        étiquette [drapeaux] | expression régulière   (iu par défaut)
//    plus une ligne « !cle <hex> », la clé des acquittements privés.
//    Sans elle, la garde tourne à moitié et le dit ; avec GARDE_EXIGEE=1
//    (la CI), elle refuse.
//
// Le journal de la CI est public : en CI, une touche ne montre jamais le texte,
// seulement le fichier, l'endroit (t= secondes dans le cast, ou la ligne) et
// l'étiquette. En local, le texte est affiché.
//
// Faux positifs : plusieurs vrais noms d'hôte sont aussi des mots français.
// Une ligne relue et jugée correcte s'acquitte dans scripts/public-leaks-ack.txt
// avec l'empreinte que la garde imprime. Côté privé, l'empreinte est un HMAC
// par la clé de la liste noire : sans la clé, on ne peut pas tester une ligne
// publique contre le fichier pour apprendre qu'elle a touché un vrai nom.
import { createHash, createHmac } from "node:crypto";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";
import xterm from "@xterm/headless";
import { PUBLIC_RULES, allowlistHits, loadDenylist } from "./lib/public-gate.mjs";

const { Terminal } = xterm;
const ROOT = new URL("..", import.meta.url).pathname;
const IN_CI = !!process.env.CI || process.env.GARDE_SILENCE === "1";

const ESC = /\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\)|[PX^_][^\x1b]*\x1b\\|[@-Z\\-_])/g;

/* Toutes les lignes qu'un cast a affichées, avec l'instant de leur première
   apparition. */
async function castLines(path) {
  const [head, ...rest] = readFileSync(path, "utf8").split("\n").filter(Boolean);
  const hdr = JSON.parse(head);
  const seen = new Map();
  const note = (text, where, raw = false) => {
    const t = text.replace(/\s+$/, "");
    if (t.trim() && !seen.has(t)) seen.set(t, { where, raw });
  };
  note(hdr.title ?? "", "en-tête");
  for (const v of Object.values(hdr.env ?? {})) note(String(v), "en-tête");

  const term = new Terminal({
    cols: hdr.width,
    rows: hdr.height,
    scrollback: 0,
    allowProposedApi: true,
  });
  const buf = () => term.buffer.active;
  let raw = "";
  for (const l of rest) {
    const [time, kind, data] = JSON.parse(l);
    const where = `t=${Number(time).toFixed(1)} s`;
    if (kind !== "o") {
      note(String(data), where);
      continue;
    }
    raw += data;
    await new Promise((r) => term.write(data, r));
    // Les lignes enroulées sont relues comme une seule : un nom coupé par la
    // marge reste un nom.
    let logical = "";
    for (let y = 0; y < term.rows; y++) {
      const line = buf().getLine(buf().viewportY + y);
      if (!line) continue;
      if (!line.isWrapped && logical) {
        note(logical, where);
        logical = "";
      }
      logical += line.translateToString(true);
    }
    if (logical) note(logical, where);
  }
  term.dispose();

  // Le flux brut : séquences d'échappement retirées, retours arrière
  // appliqués, une ligne par \n ou \r.
  let flat = "";
  for (const ch of raw.replace(ESC, "")) {
    if (ch === "\b") flat = flat.slice(0, -1);
    else flat += ch;
  }
  for (const l of flat.split(/[\r\n]+/)) note(l, "flux brut", true);

  return [...seen].map(([text, { where, raw }]) => ({ text, where, raw }));
}

function textLines(path) {
  return readFileSync(path, "utf8")
    .split("\n")
    .map((text, i) => ({ text, where: `ligne ${i + 1}` }));
}

function defaultFiles() {
  const list = (dir, ext) =>
    existsSync(join(ROOT, dir))
      ? readdirSync(join(ROOT, dir))
          .filter((f) => f.endsWith(ext))
          .sort()
          .map((f) => join(ROOT, dir, f))
      : [];
  return [
    ...list("public/casts", ".cast"),
    ...list("src/content/casts", ".md"),
    ...list("src/content/casts-en", ".md"),
  ];
}

const ackFile = join(ROOT, "scripts/public-leaks-ack.txt");
const acks = new Set(
  existsSync(ackFile)
    ? readFileSync(ackFile, "utf8")
        .split("\n")
        .map((l) => l.replace(/#.*/, "").trim())
        .filter(Boolean)
    : [],
);

const deny = loadDenylist();
if (!deny) {
  if (process.env.GARDE_EXIGEE === "1") {
    console.error("check-public-leaks : liste noire privée absente, et GARDE_EXIGEE=1 — refus.");
    process.exit(2);
  }
  console.warn(
    "check-public-leaks : liste noire privée absente — seule la moitié publique tourne.",
  );
}

const files = process.argv.slice(2).length
  ? process.argv.slice(2).map((f) => join(process.cwd(), f))
  : defaultFiles();

let unacked = 0;
const used = new Set();
for (const file of files) {
  const rel = relative(ROOT, file);
  const lines = file.endsWith(".cast") ? await castLines(file) : textLines(file);
  const pub = allowlistHits(lines.map((l) => (l.raw ? "" : l.text)));

  lines.forEach(({ text, where }, i) => {
    const hits = [];
    if (pub.has(i)) hits.push(["pub", pub.get(i)]);
    for (const [label, re] of PUBLIC_RULES) if (re.test(text)) hits.push(["pub", label]);
    for (const [label, re] of deny?.rules ?? []) if (re.test(text)) hits.push(["priv", label]);
    if (!hits.length) return;

    const material = `${rel}\0${text}`;
    const id = {
      pub: `pub:${createHash("sha256").update(material).digest("hex").slice(0, 32)}`,
      priv: deny ? `priv:${createHmac("sha256", deny.key).update(material).digest("hex").slice(0, 32)}` : null,
    };
    for (const [side, label] of hits) {
      const ack = id[side];
      if (ack && acks.has(ack)) {
        used.add(ack);
        continue;
      }
      unacked++;
      console.error(`FUITE [${label}] ${rel} (${where})  ${ack}`);
      if (!IN_CI) console.error(`    ${text.trim().slice(0, 200)}`);
    }
  });
}

/* Un acquittement qui ne sert plus est une porte ouverte pour rien. On le
   signale seulement quand on a vu tout le corpus et les deux moitiés. */
if (deny && !process.argv.slice(2).length) {
  for (const a of acks) if (!used.has(a)) console.warn(`acquittement inutilisé : ${a}`);
}

if (unacked) {
  console.error(
    `\ncheck-public-leaks : ${unacked} touche(s) non acquittée(s). Corriger le cast ou sa fiche ;` +
      `\nsi la ligne est correcte après relecture, ajouter son empreinte à scripts/public-leaks-ack.txt.`,
  );
  process.exit(1);
}
console.log(
  `check-public-leaks : ${files.length} fichier(s) propres` +
    (deny ? "" : " (moitié publique seulement)"),
);
