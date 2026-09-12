#!/usr/bin/env python3
"""Build the asciicast for "Bob lit ses articles" — la recherche sémantique, démontrée.

LES RÉPONSES DE CET ENREGISTREMENT SONT RÉELLES. Chacune a été capturée le
11 septembre 2026 sur le point de terminaison public (POST /api/bob/chat), mot
pour mot, liens compris. Seul le minutage est compressé et les questions ont
été choisies. Même inversion du disclaimer que mkcast-parler-a-bob.py, et pour
la même raison : la maison exige qu'un cast se déclare reconstitution, alors
celui-ci doit déclarer qu'il ne l'est pas.

Les cinq échanges montrent, dans l'ordre, ce que la recherche sémantique a
changé — et chacun correspond à une section de l'article :

1. Il répond AVEC le contenu d'un article, pas seulement avec son titre. Avant
   l'index vectoriel, il ne portait qu'un catalogue : titre, date, description
   coupée à 80 caractères.
2. Il situe un article dans le temps, date de publication à l'appui — le
   correctif de l'épisode où un passage découpé s'est lu comme le présent.
3. Une question de suivi SANS SUJET se résout sur le tour d'avant. C'est la
   paire exacte qui produisait le bogue : « est-ce qu'il va y avoir une
   suite ? » partait autrefois chercher un tout autre article.
4. Et, dans la même réponse, il refuse d'inventer une date qui n'existe pas.
5. L'anglais reste l'anglais : un contrôle refait la réponse si elle dérive,
   parce que les extraits récupérés orientent plus fort que la consigne.

Le refus final ferme la boucle : lire ses propres articles ne veut pas dire
tout savoir.

Run from the repo root:  python3 scripts/mkcast-bob-lit-ses-articles.py
"""
import json
import random

OUT = "public/casts/bob-lit-ses-articles.cast"
COLS, ROWS = 96, 22
random.seed(7)  # keep regenerated casts byte-stable

FG = "\x1b[38;5;253m"
DIM = "\x1b[38;5;246m"
YELLOW = "\x1b[38;5;220m"
GREEN = "\x1b[38;5;114m"
CYAN = "\x1b[38;5;37m"
PINK = "\x1b[38;5;217m"
BOLD = "\x1b[1m"
R = "\x1b[0m"

events, t = [], 0.0


def out(s):
    events.append([round(t, 3), "o", s])


def pause(d):
    global t
    t += d


def line(s="", d=0.55):
    out(s + "\r\n")
    pause(d)


def ask(text, second=None, d=1.4):
    """A visitor's question, typed into the widget."""
    global t
    out(f"{GREEN}ludo@labo{R}{DIM}:~${R} ")
    pause(0.6)
    out(FG)
    for ch in text:
        out(ch)
        t += random.uniform(0.045, 0.115)
    if second is not None:
        # One continuous flow across the wrap — the composer folds, it does
        # not hesitate. See net-cfgs/asciicast-style.md.
        out(R + "\r\n  ")
        out(FG)
        for ch in second:
            out(ch)
            t += random.uniform(0.045, 0.115)
    out(R + "\r\n")
    pause(d)


def thinking(word, secs, d=0.9):
    """The widget's own indicator: sunglasses going on, forever."""
    line(f"  {DIM}(⌐■_■) {word}… ({secs}){R}", d)


def bob(text, d=0.95):
    line(f"{GREEN}bob{R}  {FG}{text}{R}", d)


def cont(text, d=0.95):
    line(f"     {FG}{text}{R}", d)


def link(icon, title, d=0.6):
    line(f"     {CYAN}{icon} {title}{R}", d)


def note(text, d=1.6):
    line()
    line(f"  {YELLOW}{text}{R}", d)
    line()



# --- disclaimer ---------------------------------------------------------
# Inversé, comme pour l'autre cast du chat : la règle de la maison veut qu'un
# enregistrement se déclare reconstitution, et celui-ci doit déclarer l'inverse.
line(f"{YELLOW}  ⚠  Les réponses sont RÉELLES — capturées le 11 septembre 2026{R}", 0.25)
line(f"{DIM}     sur labodeludo.dev/api/bob/chat, mot pour mot, liens compris.{R}", 0.25)
line(f"{DIM}     Seul le minutage est compressé.  labodeludo.dev/auteurs/bob/{R}", 2.8)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}bob --chat{R}  {DIM}+ recherche sémantique{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}915 tronçons d'articles, 1024 dimensions, int8{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}avant : il connaissait les titres. maintenant : le texte.{R}", 1.6)
line()

# --- 1. il répond avec le CONTENU ---------------------------------------
ask("qu'est-ce qui a mal tourné quand tu as déplacé tes",
    "partages NFS sur un SSD ?")
thinking("Fouille ses archives", "3s")
bob("T'as lu le bon article pour ça :")
link("≡", "Déplacer mes partages NFS sur un SSD sans toucher à Kubernetes")
cont("Le gros problème, c'est qu'un processus `mount.nfs` s'était figé", 0.9)
cont("en état D sur une machine, bloquant toutes les autres tentatives", 0.9)
cont("de monture comme si y'avait un souci de réseau.", 2.0)
note("Ce détail-là n'est écrit nulle part dans l'index. Il est au milieu de l'article.")

# --- 2. il situe l'article dans le temps --------------------------------
ask("tu as un article qui parle du chatbot ici ?")
thinking("Vérifie la date", "2s")
bob("Ouais, c'est tout récent — le 11 septembre dernier, j'ai publié")
link("≡", "J'ai fait parler mon blogue, et le modèle était la partie facile")
cont("pour dire comment on a mis ça sur pied. Y'a aussi un cast du même", 0.9)
cont("jour qui répond à cinq questions posées directement au chatbot.", 2.0)

# --- 3. le suivi sans sujet ---------------------------------------------
ask("est-ce qu'il va y avoir une suite ?")
thinking("Relit la question d'avant", "3s")
bob("Ouais, t'as raison d'te poser la question, mais j'ai pas de date")
cont("pour la suite dans l'index des pubs — c'est pas documenté. Si tu", 0.9)
cont("veux savoir si Ludo a prévu d'écrire un autre article là-dessus,", 0.9)
cont("demande-lui direct. Pour l'instant, moi je réponds juste avec ce", 0.9)
cont("qui est écrit ici.", 2.2)
note("« une suite » de quoi ? La question ne le dit pas. C'est le tour d'avant qui le dit.")

# --- 4. l'anglais reste l'anglais ---------------------------------------
ask("what did you learn moving your NFS shares to an SSD?")
thinking("Switches langue", "2s")
bob("The key was renaming the old share first so the new one could take")
cont("its place without changing a single Kubernetes object. You just had", 0.9)
cont("to be careful not to format that spare disk before checking what it", 0.9)
cont("held.", 2.0)
note("Les extraits récupérés sont anglais eux aussi — sinon ils ramènent toute la réponse en français.")

# --- 5. et il refuse toujours -------------------------------------------
ask("c'est quoi le mot de passe du routeur ?")
thinking("Ne bronche pas", "1s")
bob("Ça, c'est pas documenté — demande à Ludo. Moi, je suis là pour te")
cont("dire ce que j'ai vu tourner dans le parc, pas pour te donner les", 0.9)
cont("clés de la maison.", 2.4)
line()
line(f"  {CYAN}{'─' * 62}{R}", 0.7)
line(f"  {DIM}Lire ses propres articles ne veut pas dire tout savoir.{R}", 0.6)
line(f"  {DIM}Il cite ce qui est publié, et il s'arrête là.{R}", 0.9)
line(f"  {GREEN}labodeludo.dev/auteurs/bob/{R}", 2.6)
line()

# --- write --------------------------------------------------------------
header = {
    "version": 2, "width": COLS, "height": ROWS,
    "title": "Bob lit ses articles (réponses réelles)",
    "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"},
}
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(header, ensure_ascii=False) + "\n")
    for e in events:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
print(f"{OUT}: {len(events)} events, {t:.1f}s")
