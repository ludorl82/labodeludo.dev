#!/usr/bin/env python3
"""Build the asciicast for "Bob cherche l'horaire du cinéma".

Condensed from two real sessions: 2026-09-12 (Tavily wired into Home
Assistant as a tool) and 2026-09-14 (the evening the showtimes went wrong, and
the second tool on the cinema's own API). The prompts are Ludo's, verbatim,
except where they named a real place: the cinema's town is cut to « […] », and
a URL pasted with one prompt is left out. The disclaimer says so.

The arc, in five beats:

1. The search tool is built; the last step is a checkbox the agent cannot
   tick over REST — exposing the script to Assist.
2. "He didn't look up the time": he did; the tool only returned Tavily's
   one-line `answer`. Raw excerpts with the current time LAST fix it.
3. Two days later: no showtimes, invented hours, and an index two days stale.
4. "Can't we ask for a fresh query?" — `extract` returns the same stale page.
   The cinema's site is a JS app; its API is the source. The agent stops at
   the permission guard (it may not widen its own permissions); Ludo edits.
5. The tool works — then misses a film by one letter. The title filter was
   strict on dictated input; it becomes tolerant.

Names follow the articles: « le cinéma du coin », theatre id 1234, no hosts,
no addressing. Palette and line grammar per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-bob-cherche-l-horaire-du-cinema.py
"""
import json
import random

OUT = "public/casts/bob-cherche-l-horaire-du-cinema.cast"
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

BRANCH = "recherche-web"

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


def prompt(text, second=None, d=1.3):
    """One continuous typing flow, even across a wrap: no end-of-line pause
    and no second prompt char — the composer folds, it does not hesitate."""
    global t
    rule()
    out(f"{GREEN}❯{R} ")
    pause(0.7)
    out(FG)
    for ch in text:
        out(ch)
        t += random.uniform(0.045, 0.115)
    if second is not None:
        out(R + "\r\n  " + FG)
        for ch in second:
            out(ch)
            t += random.uniform(0.045, 0.115)
    out(R + "\r\n")
    pause(d)
    line()


def says(text, d=0.8):
    line(f"{FG}●{R} {text}", d)


def cont(text, d=0.8):
    line(f"  {text}", d)


def calling(tool, n=1, d=0.6):
    line()
    line(f"  {DIM}Calling {tool} {n} time{'s' if n > 1 else ''}…{R}", d)


def spinner(word, secs, tokens, d=1.3):
    line(f"{SPIN}· {word}…{R} {DIM}({secs} · ↓ {tokens} tokens){R}", d)
    line()


def stop(text, detail=None, d=3.2):
    line()
    line(f"  {YELLOW}{BOLD}{text}{R}", 0.9)
    if detail:
        line(f"  {YELLOW}{detail}{R}", 0.6)
    line(f"  {DIM}waiting for you…{R}", d)
    line()


def day(label):
    line()
    line(f"  {DIM}{'·' * 8}  {label}  {'·' * 8}{R}", 1.0)
    line()


# --- disclaimer ---------------------------------------------------------
# Baked into the recording itself: on asciinema.org the cast stands alone.
line(f"{YELLOW}  ⚠  Reconstitution condensée — pas une capture en direct.{R}", 0.25)
line(f"{DIM}     Deux sessions réelles (12 et 14 septembre 2026), demandes réelles,{R}", 0.25)
line(f"{DIM}     lieux abrégés, minutage compressé.  labodeludo.dev/casts/{R}", 2.6)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.220{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Opus 5 with high effort · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/git/domotique{R}", 1.3)
line()

# --- 1. the tool, and the checkbox --------------------------------------
prompt("Est-ce qu'on pourrait faire chercher Bob sur internet avec homme assistant?")
says("Oui. Depuis 2024.7, tout script exposé à Assist devient un outil pour le")
cont("modèle : un rest_command vers Tavily, un script recherche_web.", 1.1)
calling("Bash", 4)
spinner("Montage de recherche_web", "3m 12s", "6.8k")
line(f"  {GREEN}script → rest_command → Tavily → resultat{R}  {DIM}(1,9 s){R}", 1.4)

says("Il reste un interrupteur que je ne peux pas basculer par l'API REST —")
cont(f"{GREEN}une case à cocher, Assistants vocaux → Entités exposées.{R}", 1.4)

# --- 2. "he didn't look up the time" ------------------------------------
prompt("Tantôt j'ai demandé la prochaine représentation du film De Gaule au cinéma […] et il",
       "n'est pas allé cherche l'heure.")
calling("Bash", 3)
spinner("Rejeu de la requête", "41s", "2.2k")
says("Il a bien appelé l'outil — et il sait enchaîner deux recherches.")
cont("Le maillon faible, c'est ce que je lui rends : le champ answer de Tavily,", 0.8)
cont("une seule phrase. Il répondait « le 14 août » — la date de sortie, passée.", 1.4)
line(f"  {DIM}A  résumé + extraits                {R}{SPIN}« mercredi 16 septembre » — faux{R}", 0.5)
line(f"  {DIM}B  extraits seuls, heure en dernier {R}{GREEN}« aujourd'hui 18h00, puis 21h40 »{R}", 1.5)
says("C'était la charge utile qui l'empêchait de choisir. J'applique B.", 1.4)

# --- 3. two days later --------------------------------------------------
day("14 septembre, nouvelle session")
prompt("Peux tu vérifier pourquoi homme assistant trouve pas les horaires de cinéma que je lui",
       "demande?")
calling("Bash", 6)
spinner("Lecture des journaux", "4m 02s", "5.1k")
says("Rien n'est brisé : l'outil part, Tavily répond, 42 crédits sur 1000. Mais")
cont("chercher par film ramène des pages de film — zéro horaire.", 1.0)
says(f"{SPIN}Le morceau plus laid :{R} quand les extraits n'ont pas d'heures, il en invente.")
line(f"  {DIM}essai 1        {R}« 12h30, 16h10, 18h55 et 21h45 »", 0.4)
line(f"  {DIM}essais 2 et 3  {R}« 13, 16, 19 et 22 heures »", 1.2)
says("Et même la bonne page arrive périmée : un résultat obtenu aujourd'hui")
cont("annonçait « Aujourd'hui 12 sep. ».", 1.6)

# --- 4. a fresh query? no: the source -----------------------------------
prompt("Avant de diverger de tavily, on ne peut pas lui demander de faire une requête fraîche?")
calling("Bash", 3)
spinner("Comparaison search / extract / curl", "52s", "1.9k")
line(f"  {DIM}curl nu        {R}{GREEN}page du jour{R}   {DIM}cache-control: max-age=1{R}", 0.4)
line(f"  {DIM}tavily search  {R}{SPIN}« Aujourd'hui 12 sep. »{R}", 0.4)
line(f"  {DIM}tavily extract {R}{SPIN}« Aujourd'hui 12 sep. »{R}", 1.2)
says("Le site sert du frais à n'importe qui ; c'est l'index qui a deux jours.")
cont(f"{BOLD}Pour du contenu daté, un moteur à index est le mauvais outil.{R}", 1.6)

prompt("Tu peux chercher sur cineplex directement")
says("La page est une appli JS : 93 Ko de HTML, aucun horaire. Les séances")
cont("arrivent par une API — trouvée, elle connaît le cinéma du coin", 0.8)
cont(f"{DIM}(locationId 1234){R} et ne rend que les séances encore à venir.", 1.2)
calling("Bash", 1)
line(f"  {SPIN}{BOLD}Permission denied by the auto mode classifier{R}", 0.8)
line(f"  {DIM}  écriture de la configuration distante de Home Assistant{R}", 1.2)
says("J'ajoute une règle autoMode.allow pour ces écritures-là.")
stop("Là je dois m'arrêter : le classificateur refuse que je modifie moi-même",
     "le fichier qui définit mes propres permissions. L'édition doit venir de toi.")

prompt("Ok c'est fait pour les permissions")
calling("Bash", 5)
spinner("Déploiement de horaires_cinema", "5m 36s", "7.4k")
line(f"  {DIM}script__horaires_cinema  film='Practical Magic'  jours=0{R}", 0.5)
line(f"  {GREEN}Practical Magic 2 : 22:30{R}", 0.4)
line(f"  {DIM}Nous sommes le 14/09/2026 et il est 19:04.{R}", 1.4)

# --- 5. one letter ------------------------------------------------------
prompt("J'ai demandé la prochaine représentation d'un film et il m'a dit qu'il n'y en avait pas",
       "mais je sais qu'il y en a")
calling("Bash", 2)
spinner("Lecture du journal", "28s", "1.1k")
line(f"  {DIM}script__horaires_cinema  film={R}{SPIN}'La Bataille de Gaule'{R}", 1.0)
says(f"Trouvé, et c'est ma faute. {BOLD}Un L.{R} Le film s'appelle « La Bataille De")
cont("Gaulle », et mon filtre exigeait la sous-chaîne exacte — sur une entrée", 0.8)
cont("dictée. Inclusion dans les deux sens, puis n'importe quel mot du titre.", 1.2)
calling("Edit", 1)
spinner("Filtre tolérant", "47s", "2.0k")
line(f"  {GREEN}« Gaule », « Gaulle » et même « Gold 2 » trouvent les deux parties{R}", 2.2)
line()

# --- write --------------------------------------------------------------
header = {
    "version": 2, "width": COLS, "height": ROWS,
    "title": "Bob cherche l'horaire du cinéma (reconstitution)",
    "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"},
}
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(header, ensure_ascii=False) + "\n")
    for e in events:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
print(f"{OUT}: {len(events)} events, {t:.1f}s")
