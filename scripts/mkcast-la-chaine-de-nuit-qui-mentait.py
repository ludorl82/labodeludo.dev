#!/usr/bin/env python3
"""Build the asciicast for « La chaîne de nuit qui mentait ».

Condensed from the real session of 2026-09-16 (continued past midnight UTC),
the day documented in net-cfgs/history.md as « La chaîne de nuit : la bonne
version, le bon compte de cartes, moins de temps, et des journaux ». The two
companion articles are « ce-que-coute-une-nuit-de-pipeline » (Ludo, the cost
tables) and « la-job-etait-verte » (Bob, the plumbing).

The day had a dozen threads. This recording keeps one: three green statuses
that each said « tout va bien » for a reason unrelated to the work.

1. A suggested question that leads to a refusal. The guard existed; it never
   ran, because the scheduler executed a hand-made copy in ~/scripts dated
   Sunday the 13th. The agent stops on a refused write and waits for Ludo.
2. (short) the graphics card nobody counted: labo.gpus, and the first real
   run of the machine-side check flagging two false alerts of its own making.
3. « Pourquoi 60 minutes quand rien n'a changé ? » The agent proposes to
   measure first; Ludo says the times are already known. Delta (seen-A).
4. The API content filter refuses session C in 12 s, `qwen` exits 0, and the
   driver reports « already matched » — worse, the fresh delta banks it.
   Then the agent retracts its own « gros levier » claim with the numbers.
5. Every scheduled job dies with code 70, « never started »: Debian's bash
   reads ~/.bashrc under sshd, and line 3 of that file is `exec zsh`.

Prompts are verbatim from the transcript (typos kept). Tool output is
rewritten short. Names follow the articles: « la console », « le
planificateur », gaming-01; no hosts, domains, addresses, PR numbers or
commit hashes from the real lab. Palette and line grammar per
net-cfgs/asciicast-style.md; prompt helper is the fixed (no-pause) one.

Run from the repo root:  python3 scripts/mkcast-la-chaine-de-nuit-qui-mentait.py
"""
import json
import random

OUT = "public/casts/la-chaine-de-nuit-qui-mentait.cast"
COLS, ROWS = 96, 22
random.seed(16)  # keep regenerated casts byte-stable

# --- palette sampled from the terminal screenshots ----------------------
FG = "\x1b[38;5;253m"  # #d8d8d8 body text
DIM = "\x1b[38;5;246m"  # #949494 secondary
YELLOW = "\x1b[38;5;220m"  # #ffd700 headings / warnings
GREEN = "\x1b[38;5;114m"  # #87d787 ok / prompt
SPIN = "\x1b[38;5;174m"  # #d78787 spinner, failures
RED = "\x1b[38;5;174m"
CYAN = "\x1b[38;5;37m"  # #00afaf rule + branch
PINK = "\x1b[38;5;217m"  # logo
BOLD = "\x1b[1m"
R = "\x1b[0m"

BRANCH = "chaine-de-nuit"

events, t = [], 0.0


def out(s):
    events.append([round(t, 3), "o", s])


def pause(d):
    global t
    t += d


def line(s="", d=0.55):
    out(s + "\r\n")
    pause(d)


def rule():
    dashes = "─" * (COLS - len(BRANCH) - 3)
    line(f"{CYAN}{dashes} {BRANCH}{R}", 0.5)


def prompt(*parts):
    """One continuous typing flow across wraps: no end-of-line pause and no
    second prompt char — the composer wraps, it does not hesitate."""
    global t
    rule()
    out(f"{GREEN}❯{R} ")
    pause(0.7)
    for i, text in enumerate(parts):
        if i:
            out(R + "\r\n  ")
        out(FG)
        for ch in text:
            out(ch)
            t += random.uniform(0.045, 0.115)
    out(R + "\r\n")
    pause(1.4)
    line()


def says(text, d=0.9):
    line(f"{FG}●{R} {text}", d)


def cont(text, d=0.9):
    line(f"  {text}", d)


def calling(tool, n=1, d=0.7):
    line()
    line(f"  {DIM}Calling {tool} {n} time{'s' if n > 1 else ''}…{R}", d)


def spinner(word, secs, tokens, d=1.5):
    line(f"{SPIN}· {word}…{R} {DIM}({secs} · ↓ {tokens} tokens){R}", d)
    line()


def waiting():
    line()
    line(f"  {DIM}waiting for you…{R}", 3.2)


# --- disclaimer ---------------------------------------------------------
line(f"{YELLOW}  ⚠  Reconstitution condensée — pas une capture en direct.{R}", 0.25)
line(f"{DIM}     Demandes et messages réels (16 sept. 2026), minutage compressé,{R}", 0.25)
line(f"{DIM}     sorties réécrites, noms sanitisés.  labodeludo.dev/casts/{R}", 2.2)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.220{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Opus 5 with high effort · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/git/labo{R}", 0.9)
line()

# --- 1. green, and running Sunday's code --------------------------------
prompt("Pour le pipeline qui choisit les questions, cette nuit il a choisit une question",
       "qui répond par la negative, peux tu regarder?")

calling("Bash", 3)
spinner("Lecture du journal de la job", "14s", "1.6k")
line(f"  {DIM}job des questions   {R}{GREEN}succès{R}  {DIM}71 s · 8 questions publiées{R}", 0.4)
line(f"  {DIM}check-answerable    {R}{RED}aucune ligne{R}", 0.4)
line(f"  {DIM}~/scripts/daily-bob-sync.sh   daté du 13 sept. · 2 commits derrière master{R}", 1.3)
says(f"Ce n'est pas la garde qui a mal jugé — {BOLD}la garde n'a jamais tourné.{R}")
cont("Le planificateur exécute une copie faite à la main dans ~/scripts, que rien", 0.8)
cont("ne synchronise. La job était verte, et elle roulait le code de dimanche.", 1.4)
says("L'écriture dans ~/scripts m'est refusée (« Modify Shared Resources »).")
cont("J'ai besoin de ton feu vert pour y recopier les trois scripts de master.", 0.6)
waiting()

prompt("g approuvé les permissions")
says("Les trois scripts sont identiques à master. Pour que ça ne revienne pas :")
cont(f"{GREEN}run-from-master.sh{R} — fetch master, exécute, imprime le commit ;", 0.8)
cont("un fetch raté sort en erreur au lieu de rouler la copie d'hier.", 1.6)

# --- 2. the card nobody counted -----------------------------------------
prompt("Fais le champ labo.gpus maintenant. Je veux le voir corriger le problème. Tu",
       "pourras rouler le pipeline ensuite")
calling("Edit", 4)
spinner("Déclaration des cartes", "2m 10s", "6.2k")
line(f"  {DIM}drift-ctl gpus   {R}{RED}2 DISAGREES{R}  {DIM}— le contrôle envoyait `true`, et un invité{R}", 0.5)
line(f"  {DIM}                 voit des adresses PCI traduites : deux fausses alertes, de mon fait{R}", 0.5)
line(f"  {DIM}drift-ctl gpus   {R}{GREEN}10 AGREES{R}  {DIM}· 3 invités SKIPPED · gaming-01 : 2 × RTX 3050{R}", 1.6)

# --- 3. sixty minutes for nothing ---------------------------------------
prompt("Est-ce qu'il y aurait moyen d'utiliser le pipeline pour qu'il ne roule pas aussi",
       "longtemps lorsqu'il n'y a pas de changement. Je m'explique mal qu'on ait pas plus de",
       "60 minutes avec des données qui n'ont pas changé")
says("Environ cent requêtes à vingt secondes chacune, pour une seule session.")
says(f"{BOLD}1. Mesurer d'abord.{R} Ajouter la durée par session au journal.")
cont(f"{BOLD}2. Donner un delta à A et C{R}, comme B et D en ont un.", 0.6)
waiting()

prompt("On sait déjà le temps pris. Pas besoin de 1. Utilisons le delta comme tu suggères")
says(f"Chaque session garde son point de départ, {GREEN}seen-A{R} et {GREEN}seen-C{R}, et ne", 0.8)
cont("reçoit que la liste calculée des commits. Relecture complète aux sept jours.", 1.4)

# --- 4. a refusal read as agreement -------------------------------------
calling("Bash", 2)
spinner("Passage de mesure", "61m 16s", "3.8k")
line(f"  {DIM}C says: {R}{RED}[API Error: 400 InternalError.Algo.DataInspectionFailed]{R}", 0.5)
line(f"  {DIM}C: 12 s · 3 requêtes · 0,00 $ · qwen exit 0{R}", 0.5)
line(f"  {DIM}→ résumé : {R}{GREEN}« C: already matched the repos »{R}", 1.6)
line()
line(f"  {YELLOW}{BOLD}Session C n'a jamais tourné, et le pilote a dit qu'elle était d'accord.{R}", 1.2)
says("Le filtre de contenu de l'API a refusé l'entrée. Rien lu, rien écrit,")
cont(f"donc « d'accord ». Et {BOLD}depuis mon delta, la base avance{R} : la nuit suivante", 0.8)
cont("aurait sauté pour de bon une fenêtre que personne n'a lue.", 0.6)
cont(f"Correctif : fouiller la transcription, sortir en {RED}60{R}, ne rien enregistrer.", 1.6)

says("Et je dois corriger ce que je t'ai dit : j'ai vendu « pas de session quand")
cont(f"rien n'a changé » comme le gros levier. {BOLD}C'est faux.{R} Une garde sautait", 0.8)
cont(f"déjà A et C. {BOLD}Le vrai levier, c'est le delta.{R}", 1.2)
line(f"  {DIM}A complète, rien trouvé   35,4 min   149 requêtes   24,9 M jetons   0,42 ${R}", 0.5)
line(f"  {DIM}A en delta                 {R}{GREEN}7,5 min    24 requêtes    1,9 M jetons   0,05 ${R}", 1.8)

# --- 5. the third line of .bashrc ---------------------------------------
prompt("Fusionné, est-ce qu'on peut s'assurer de collecter les logues dans grafana et son",
       "système de logue")
calling("Bash", 6)
spinner("Vérification des jobs", "4m 40s", "5.1k")
line(f"  {DIM}journal de la console → Loki   {R}{GREEN}ok{R}", 0.4)
line(f"  {DIM}chaque job du planificateur    {R}{RED}code 70 · « never started » · < 6 s{R}", 1.6)
says(f"Pire qu'un problème de logues : {BOLD}toute la chaîne de 04:30 serait tombée.{R}")
cont("Ton ~/.bashrc fait `exec zsh` à la ligne 3, avant la garde interactive.", 0.8)
cont("Sous ssh, le bash de Debian lit ~/.bashrc même pour un `bash -c` : la job", 0.8)
cont("devenait un zsh, qui sortait à 0 sans rien exécuter.", 1.2)
says(f"Correctif : {GREEN}bash --norc --noprofile{R}, sans SSH_CLIENT. Ton .bashrc, je n'y")
cont("touche pas. Les tests passaient parce qu'ils roulaient dans le seul contexte où", 0.8)
cont("la panne est impossible ; ils posent maintenant un .bashrc hostile.", 1.6)

# --- the lesson ---------------------------------------------------------
line()
says(f"Trois verts, trois mensonges. {BOLD}Vert ne dit pas quelle version a roulé.{R}")
cont("Faire écrire au système ce qu'il a fait : le commit, le refus, le code.", 2.2)
line()

# --- write --------------------------------------------------------------
header = {
    "version": 2, "width": COLS, "height": ROWS,
    "title": "La chaîne de nuit qui mentait (reconstitution)",
    "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"},
}
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(header, ensure_ascii=False) + "\n")
    for e in events:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
print(f"{OUT}: {len(events)} events, {t:.1f}s")
