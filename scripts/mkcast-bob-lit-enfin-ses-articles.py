#!/usr/bin/env python3
"""Build the asciicast for "Bob lit enfin ses articles" — the build session.

Condensed from the real session of 2026-09-11 (evening), the one the article
"J'ai lu mes propres articles…" is drawn from. The cast "bob-lit-ses-articles"
already shows the chat's ANSWERS; this one shows the construction: how the
semantic index (bge-m3, int8, no vector database) went from idea to production,
and the four ways it broke on the way.

The arc, in five beats:

1. The diagnosis: the chat only ever saw a catalogue (title, date, description
   cut at 80 characters), and the corpus is far too big for a prompt.
2. "construis le": bge-m3 moves into the existing Ollama, 915 chunks, 2.45 MB.
   The Worker goes live first and degrades cleanly (`retrieved` empty).
3. "merged": retrieval still empty — a 404 frozen at the edge by
   `cacheEverything`, a retry with `cacheTtl: 0` that bypasses nothing, then a
   HTTP 500 on a second system message, right after announcing it was ready.
4. The chat announcing its own disappearance: a cut-up chunk without its
   subject and without a date. Fix: dates on excerpts plus an arbitration rule.
5. A follow-up question with no subject: only the last message was embedded.
   A classifier is ruled out by the data; both formulations are embedded and
   each chunk keeps its best score. And the catch that matters most: the date
   fix had never reached production — a duplicated function, which
   `node --check` does not catch in a module.

Prompts are verbatim. The two pasted conversations are cut short (marked […]),
as the on-screen notice says. The cloud model is not named, hosts are not
named beyond the public "bob" and the fictional gpu-01; repositories are not
named. Palette and line grammar per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-bob-lit-enfin-ses-articles.py
"""

import random
import re

import claude_tui as T
from claude_tui import BOLD, CYAN, DIM, FG, GREEN, R, RED, YELLOW, calling, line, spinner

T.setup(
    out="public/casts/bob-lit-enfin-ses-articles.cast",
    title="Bob lit enfin ses articles (reconstitution)",
    session="recherche-semantique",
    windows=["backlog", "recherche-semantique"],
    current="recherche-semantique",
    start="11-Sep-26 19:48:22",
    cwd="~/git/site",
    model="Opus 5 · Claude Max",
    version="v2.1.180",
    seed=19,
)

T.disclaimer("Demandes réelles (conversations collées abrégées […]),",
             "minutage compressé, noms sanitisés.")
T.banner()

CODE = "\x1b[38;5;153m"  # inline code, as the TUI tints it (no backticks)


def md(text):
    """Render `code` spans the way the TUI does: tinted, backticks dropped."""
    return re.sub(r"`([^`]+)`", lambda m: f"{CODE}{m.group(1)}{R}", text)


def says(text, d=0.9):
    T.says(md(text), d)


def cont(text, d=0.9):
    T.cont(md(text), d)


def prompt(text, pasted=None):
    """La demande tapée d'un trait ; une conversation collée arrive d'un bloc,
    comme un collage dans la zone de saisie, et monte avec la demande."""
    if not pasted:
        T.prompt(text)
        return
    T._end_turn()
    b = T._s["bottom"]
    T.pause(0.6)
    typed = ""
    for ch in text:
        typed += ch
        T.out_(f"\x1b7\x1b[{b + 2};1H\x1b[2K❯ {typed[-(T.COLS - 3):]}\x1b8")
        T.t += random.uniform(0.045, 0.11)
    tag = f" [Pasted text #1 +{len(pasted)} lines]"
    T.pause(0.5)
    T.out_(f"\x1b7\x1b[{b + 2};1H\x1b[2K❯ {(typed + tag)[-(T.COLS - 3):]}\x1b8")
    T.pause(0.7)
    T.out_(f"\x1b7\x1b[{b + 2};1H\x1b[2K❯ \x1b8")
    import textwrap
    for i, l in enumerate(textwrap.wrap(text, T.COLS - 4)):
        T._hist(f"{DIM}{T.PROMPT_BG}{'❯' if i == 0 else ' '} {FG}{l} \x1b[49m")
    for p in pasted:
        T._hist(f"{DIM}{T.PROMPT_BG}  {p} \x1b[49m")
    line("", 2.6)
    T._s["turn"] = {"label": "5s"}
    T._footer(working=True)
    T.pause(0.8)


def beat(text, d=3.2):
    """The agent catching its own mistake. Not a stop: it kept going."""
    line()
    line(f"  {YELLOW}{BOLD}{text}{R}", d)
    line()

# --- 1. the diagnosis ---------------------------------------------------
prompt("je suis intéressé par l'idée d'alimenter Bob sur le site web avec la recherche sémantique")

calling("Bash", 3)
spinner("Lecture de la mise à la terre", "14s", "2.2k")
says(f"Le diagnostic est net. Bob reçoit un {BOLD}index{R} : une ligne par article,")
cont("titre, date, description coupée à 80 caractères. Il sait quels articles", 0.8)
cont(f"existent, {BOLD}pas ce qu'il y a dedans{R}. Le corpus fait 937 Ko, environ", 0.8)
cont("354 000 jetons : impossible à mettre dans un prompt.", 1.3)
says("Proposition : indexation au build, recherche dans le Worker, aucune base")
cont(f"vectorielle. Modèle d'embeddings : {GREEN}bge-m3{R}, multilingue. Je le construis ?", 1.8)

# --- 2. the build -------------------------------------------------------
prompt("construis le")

says("bge-m3 peut vivre dans l'Ollama de bob : aucune nouvelle exposition")
cont("publique. Côté sécurité, la règle WAF s'élargit d'un seul chemin.", 1.0)
calling("Bash", 9)
spinner("Vectorisation du corpus", "1m 41s", "6.8k")
line(f"  {GREEN}915 tronçons{R} {DIM}· 1024 dim · normalisés, quantifiés int8 · 2,45 Mo{R}", 1.2)
says("Worker déployé avant l'artefact. Bob répond toujours, `retrieved` vide :")
cont("le mode dégradé prévu. Il ne manque que la fusion, qui est la tienne.", 1.8)

# --- 3. merged: two failures in a row -----------------------------------
prompt("merged")

line(f"  {DIM}artefact :{R} {GREEN}HTTP 200{R} {DIM}· 2 448 591 octets{R}", 0.8)
line(f"  {DIM}Worker   :{R} {RED}vectors 404{R}", 1.2)
says("C'est de ma main : `cacheEverything` avec un TTL d'une heure a mis en")
cont(f"cache {BOLD}le 404{R} reçu avant le déploiement du site. `curl` voit 200, le", 0.8)
cont("Worker relit un échec figé.", 1.0)
says("Et mon réessai ne contournait rien : `cacheTtl: 0` veut dire « ne stocke")
cont("pas cette réponse », pas « ignore ce qui est stocké ».", 1.4)
calling("Bash", 4)
line(f"  {RED}source: canned{R}  {DIM}à chaque question{R}", 1.2)
says(f"{BOLD}Là j'ai cassé quelque chose.{R} Le gabarit du modèle renvoie une 500")
cont("dès qu'il y a un second message système — et j'y avais mis les extraits.", 0.8)
cont("Ils passent en tête du tour de l'utilisateur.", 1.0)
line(f"  {GREEN}retrieved: true{R}  {DIM}prompt 9 737 jetons · 2 357 réévalués{R}", 1.8)

# --- 4. the chat announces its own disappearance ------------------------
prompt("comprends tu pourquoi il me répond cela?", [
    "toi",
    "Est-ce qu'il y aura un suivi du blogue qui parle?",
    "bob",
    "Non, le suivi est parti avec les six jours de test et l'article dit explicitement",
    "que l'auteur a tout débranché pour de bon. Le chatbot n'est plus là pour répondre […]",
])

says("Oui, et c'est un défaut de ma conception. L'extrait servi dit : « Six jours")
cont("plus tard, j'ai tout débranché. » Ce « tout », c'est le modèle infonuagique,", 0.8)
cont("mais le sujet est dans le tronçon précédent. Découpé, il n'a plus de", 0.8)
cont("référent — et Bob a annoncé le départ du chatbot. En étant le chatbot.", 1.4)
says("Deux correctifs, à la fin du prompt : la date de chaque extrait, et une")
cont("règle d'arbitrage — l'état courant, plus haut, gagne sur un article.", 1.8)

# --- 5. the follow-up, and the fix that never shipped -------------------
prompt("on dirait qu'il ne tient pas compte du contexte de la conversation", [
    "toi",
    "Tu as un article qui parle du chatbot ici?",
    "[…]",
    "Est-ce qu'il va y avoir une suite?",
    "bob",
    "Non, y'a pas de suite prévue dans la série « Débrancher le NAS » […]",
])

says("Encore ma conception : je ne vectorise que le dernier message, et « une")
cont("suite ? » ne porte aucun sujet.", 1.0)
says("Détecter les suivis au score ? Les données disent non : les plages se")
cont("chevauchent, une vraie question marque 0,406. Je vectorise donc les deux", 0.8)
cont("formulations et chaque tronçon garde son meilleur score.", 1.0)
line(f"  {DIM}suivi « une suite ? »  {R}{RED}0,422{R} {DIM}→{R} {GREEN}0,586, bon article premier{R}", 1.4)
calling("Bash", 1)
line(f"  {RED}apply échoué :{R} {DIM}Identifier 'excerptsMessage' has already been declared{R}", 1.2)

beat("Le correctif des dates n'est jamais parti en prod.")

says("Une de mes éditions a dupliqué une fonction ; Cloudflare a refusé le Worker.")
cont("Mes tests « après correction » tournaient sur l'ancien : de la variance,", 0.8)
cont(f"pas le correctif. Et {BOLD}`node --check` ne valide pas un module{R} — c'est", 0.8)
cont("`node --input-type=module` qui l'attrape.", 1.6)

# --- the lesson ---------------------------------------------------------
line()
line(f"  {CYAN}{'─' * 62}{R}", 0.6)
says(f"{BOLD}Ce qui est le plus près de la question oriente le plus fort.{R}")
cont("Les extraits décident ; tout le reste du prompt négocie.", 2.6)
line()

T.save()
