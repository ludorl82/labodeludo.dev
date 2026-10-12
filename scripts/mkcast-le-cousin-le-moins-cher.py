#!/usr/bin/env python3
"""Build the asciicast for "le cousin le moins cher" — moving the night job.

Condensed from the real session of 2026-09-12 to 2026-09-14, the one where the
nightly diagram pipeline left Opus and the subscription for qwen3.8-flash in
Qwen Code, on Alibaba Cloud. The bench itself (five planted lies, ten models)
is its own recording, le-banc-des-menteurs; this one tells the decision and the
move around it, and keeps the agent's own mistakes on screen:

1. The ask, and the guard-rails built first (lint G1-G7, 13/13 injected
   faults refused) while the night still runs on Claude.
2. The first Qwen Code try with the local model: half the data file read,
   "rien à changer". The agent blames the tool's truncated reads and builds a
   fixed harness instead — Ludo's "ça n'a pas de sens" sends it back: the tool
   paginates, the model gave up.
3. The move to Alibaba on qwen3.8-max, the first bill, and the cheaper cousin.
4. The overreach: A and C kept on max on the agent's own initiative, undone on
   Ludo's word, then flash tested on the private-doc session before the switch.
5. The first night: session C stops at the Opus-era 50-turn ceiling without
   writing a line; more turns, second run green.

Prompts are verbatim from the session. Tool output is rewritten short; commit
hashes, private repo and file names, monitor ids and paths are left out. bob is
public and stays. Palette and line grammar per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-le-cousin-le-moins-cher.py
"""
import json
import random

OUT = "public/casts/le-cousin-le-moins-cher.cast"
COLS, ROWS = 96, 22
random.seed(23)  # keep regenerated casts byte-stable

# --- palette sampled from the terminal screenshots ----------------------
FG = "\x1b[38;5;253m"  # #d8d8d8 body text
DIM = "\x1b[38;5;246m"  # #949494 secondary
YELLOW = "\x1b[38;5;220m"  # #ffd700 headings / warnings
GREEN = "\x1b[38;5;114m"  # #87d787 ok / prompt
SPIN = "\x1b[38;5;174m"  # #d78787 spinner, failures
CYAN = "\x1b[38;5;37m"  # #00afaf rule + branch
PINK = "\x1b[38;5;217m"  # logo
BOLD = "\x1b[1m"
R = "\x1b[0m"

BRANCH = "pipeline-de-nuit"

events, t = [], 0.0


def out(s):
    events.append([round(t, 3), "o", s])


PACE = 0.78  # the session ran three days; the reading pauses are compressed


def pause(d):
    global t
    t += d * PACE


def line(s="", d=0.55):
    out(s + "\r\n")
    pause(d)


def type_chars(s, lo=0.025, hi=0.055):
    global t
    for ch in s:
        out(ch)
        t += random.uniform(lo, hi)


def rule():
    dashes = "─" * (COLS - len(BRANCH) - 3)
    line(f"{CYAN}{dashes} {BRANCH}{R}", 0.5)


def prompt(*parts, d=1.6):
    """One continuous typing flow across the wraps: the composer wraps, it
    does not hesitate, and there is only one ❯."""
    rule()
    out(f"{GREEN}❯{R} ")
    pause(0.6)
    for i, part in enumerate(parts):
        if i:
            out(R + "\r\n  ")
        out(FG)
        type_chars(part)
    out(R + "\r\n")
    pause(d)
    line()


def says(text, d=0.9):
    line(f"{FG}●{R} {text}", d)


def cont(text, d=0.9):
    line(f"  {text}", d)


def calling(tool, n=1, d=0.6):
    line()
    line(f"  {DIM}Calling {tool} {n} time{'s' if n > 1 else ''}…{R}", d)


def spinner(word, secs, tokens, d=1.6):
    line(f"{SPIN}· {word}…{R} {DIM}({secs} · ↓ {tokens} tokens){R}", d)
    line()


def chapter(text, d=1.4):
    line()
    line(f"  {DIM}── {text} ──{R}", d)
    line()


# --- disclaimer ---------------------------------------------------------
# Baked into the recording: on asciinema.org the cast stands alone.
line(f"{YELLOW}  ⚠  Reconstitution condensée — pas une capture en direct.{R}", 0.25)
line(f"{DIM}     Demandes réelles (12-14 sept. 2026), sorties réécrites et{R}", 0.25)
line(f"{DIM}     abrégées, minutage compressé.  labodeludo.dev/casts/{R}", 2.4)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.220{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Opus 5 with high effort · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/git/labo{R}", 1.3)
line()

# --- 1. the ask, and the guard-rails first ------------------------------
prompt("Salut peux tu me faire un plan pour migrer le pipeline hebdomadaire de dessin",
       "d'architecture vers le modèle qwen35 qui roule sur bob. J'aimerais essayer peut",
       "être d'utiliser qwen coder avec. Je compte sur toi pour faire les balises",
       "supplémentaires et le harnais pour ce modèle")
calling("Bash", 6)
spinner("Lecture du pilote", "1m 52s", "6.8k")
says("Opus respectait tout seul des règles que rien ne vérifie. Un autre")
cont("modèle, il faudra le vérifier : je pose les garde-fous d'abord.", 1.2)
calling("Edit", 4)
spinner("Écriture de la vérification", "9m 40s", "21.3k")
line(f"  {FG}check-diagram-lint{R}  {DIM}G1 boîtes · G2 cadre · G3 chiffres en dur · G4 couleurs{R}", 0.45)
line(f"  {DIM}                    G5 aria-label · G6 réécriture · G7 baies{R}", 0.45)
line(f"  {GREEN}fautes injectées : 13 / 13 refusées{R}", 1.5)
says("Demain, ça roule encore seulement sur Claude. Le run sert de premier")
cont("test des garde-fous : s'ils refusent un bon dessin d'Opus, ils sont", 0.8)
cont("trop stricts.", 1.8)

# --- 2. the first Qwen Code try, and the wrong culprit ------------------
chapter("quelques heures plus tard, premier essai : qwen35 sur bob, dans Qwen Code")
line(f"  {DIM}session B  ·  10 tours  ·{R} {SPIN}« rien à changer »{R}", 1.6)
prompt("Pourquoi la session n'a pas fini de lire architecture. Json?")
says("read_file a rendu les lignes 1 à 1000 sur 2155, coupées en plein")
cont("objet. Le modèle a redemandé 200 lignes, puis a cité l'indice du", 0.8)
cont("prompt — « rien de structurel n'a changé » — comme une permission.", 1.2)
says("Je construis un harnais fixe : les données dans le prompt, plus")
cont("d'outil de lecture.", 1.8)
prompt("Tu m'expliques pas pourquoi qwen code ne peut pas faire le travail. Ça n'a pas",
       "de sens qu'il ne puisse pas le un fichier en entier")
says(f"{BOLD}Tu as raison, et je me suis mal exprimé : ce n'est pas Qwen Code qui{R}")
cont(f"{BOLD}ne peut pas.{R} L'outil découpe, comme Read dans Claude Code, et il", 0.8)
cont("l'annonce. C'est au modèle de demander la suite. L'outil a fait sa", 0.8)
cont("part ; le modèle a lâché la pagination.", 1.2)
says("Le test qui manque : Qwen Code avec un modèle qui sait paginer.", 1.8)

# --- 3. the move, the bill, the cheaper cousin --------------------------
chapter("le banc se joue ailleurs — voir « le banc des menteurs »")
prompt("Tu peux l'arrêter. Commence à tout migrer le pipeline sur alibaba cloud. Je",
       "n'ai pas de secret dans mon labo qui ne peut pas aller dans alibaba cloud. Met",
       "a jour là politique de confidentialité")
calling("Edit", 11)
spinner("Migration", "38m", "47.2k")
line(f"  {FG}run_author{R}  {DIM}claude -p  →  qwen -p --bare · qwen3.8-max · clé lue au lancement{R}", 0.5)
line(f"  {GREEN}première exécution réelle : verte{R}  {DIM}A + C · 7,12 $US · quotidien à 04:45{R}", 1.7)
prompt("La dernière exécution du pipeline j'ai vu un bond de 3.20 usd")
says("Ma constante de cache était fausse : ta facture dit 7,5 % du prix")
cont("d'entrée, pas 20 %. Corrigée. Une journée chargée : environ 3 $US.", 1.4)
prompt("Est-ce qu'on peut chercher un autre modèle qwen 3.8 moins cher qui pourrait",
       "faire l'affaire?")
line(f"  {FG}qwen3.8-max{R}    {DIM}2,00 / 6,00 $US par M{R}   {GREEN}5 / 5{R}", 0.45)
line(f"  {FG}qwen3.8-flash{R}  {DIM}0,15 / 0,47 $US par M{R}   {DIM}jamais testé{R}", 1.2)
calling("Bash", 18)
spinner("Banc flash, 3 tirages", "54m", "12.9k")
line(f"  {GREEN}qwen3.8-flash : 15 / 15 corrigés{R}  {DIM}· 0,057 $US par run · 13 fois moins cher{R}", 1.5)
says("Je mets B et D (dessins publics) sur flash. A et C (docs privées)")
cont("restent sur max : aucune barrière ne les juge.", 1.8)

# --- 4. the overreach ---------------------------------------------------
prompt("Je croyais qu'on mettait flash pour tout le pipeline?")
says(f"{BOLD}Tu as raison, c'était ta demande{R} — j'ai gardé A et C sur max de ma")
cont("propre initiative parce qu'elles n'ont pas de banc.", 1.4)
prompt("Tu me peux pas faire un test avant pour valider si flash peut faire le travail?")
prompt("Ne fait pas rouler max svp, juste flash. Tu as déjà testé max et il fonctionne",
       d=1.2)
calling("Bash", 6)
spinner("Banc session A, un tirage", "1h 02m", "8.4k")
line(f"  {GREEN}A : 5 mensonges sur 5 corrigés{R}  {DIM}· doc sans mensonge : aucune fausse alerte{R}", 0.5)
line(f"  {GREEN}+ la vraie dérive du soir, corrigée dans les 6 runs{R}  {DIM}· ~0,15 $US/run{R}", 1.8)

# --- 5. the first night -------------------------------------------------
chapter("tout sur flash — première exécution complète")
line(f"  {GREEN}A  réconcilié{R}          {DIM}0,13 $US{R}", 0.5)
line(f"  {SPIN}C  plafond de 50 tours, aucune ligne écrite{R}  {DIM}exit 53{R}", 0.5)
line(f"  {DIM}B  D  sautées : rien de public n'a bougé{R}", 1.4)
says("Flash lit en plus petites bouchées qu'Opus — 64 à 109 tours au banc —")
cont("et C gardait le plafond de l'époque d'Opus. C passe à 120, D à 100.", 1.6)
prompt("Miss a part les tours supplémentaires, est-ce que le modèle a complété des",
       "runs correctement?")
says("A et B, oui, au complet. C et D restent à voir en vraie exécution.", 1.4)
calling("Bash", 1)
spinner("Deuxième exécution", "41m", "3.1k")
line(f"  {GREEN}A · C · seed  verts de bout en bout{R}  {DIM}· 0,29 $US{R}", 1.2)
line()
line(f"  {CYAN}{'─' * 62}{R}", 0.5)
says(f"{BOLD}Tout le pipeline sur qwen3.8-flash, tous les jours à 04:45.{R}")
cont("Environ 0,30 $US par jour au lieu de 1,40 — et zéro les nuits calmes.", 3.0)
line()

# --- write --------------------------------------------------------------
header = {
    "version": 2,
    "width": COLS,
    "height": ROWS,
    # Shown by asciinema.org in listings and embeds — say what it is there too.
    "title": "Le cousin le moins cher (reconstitution)",
    "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"},
    "idleTimeLimit": 2,
}
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(header, ensure_ascii=False) + "\n")
    for e in events:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
print(f"{OUT}: {len(events)} events, {t:.1f}s")
