#!/usr/bin/env python3
"""Build the asciicast for "le témoin" — the control device that ends a hunt.

Condensed from the real session of 2026-09-10, the one documented in
net-cfgs/history.md as "The wake word the office could not switch off". That
session had three stories in it; this recording tells one, and only one: an LED
ring that went red at the wrong intensity, two plausible hypotheses chased in
the wrong direction, and a single sentence from Ludo that killed both.

The arc: a double-press automation is built and works — the assistant answers
perfectly — but the ring turns red the moment the wake word fires. The first
hypothesis is a known signature from 2026-08-05 (a TTS engine going
unavailable); every engine is healthy and had run a second earlier. The second
is a live conflict with the firmware's listening animation, which is about to
be tested the slow way. Then Ludo says the other satellite runs the same
animation in the right colour — and it has never been painted. That is the
whole answer: ESPHome persists the last colour HA writes TO FLASH, and the
voice animations composite on top of it.

Two beats kept because they are the lesson rather than the plot:

- The device restart that "proved" the cause was elsewhere. It restored the
  persisted value faithfully, which looks exactly like a ruled-out hypothesis.
- Testing the colour only while IDLE. Idle is the one state in which nothing
  else is drawing, so it proves nothing — and it was the entire basis for
  calling the change safe.

Names sanitized: the two satellites are voix-01 and voix-02 rather than their
MAC-derived ids, entity ids follow the same shape, no domains and no
addressing. Rooms are kept — the story is that the twin is in another room.
Palette and line grammar per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-le-temoin.py
"""
import json
import random

OUT = "public/casts/le-temoin.cast"
COLS, ROWS = 96, 22
random.seed(11)  # keep regenerated casts byte-stable

# --- palette sampled from the terminal screenshots ----------------------
FG = "\x1b[38;5;253m"
DIM = "\x1b[38;5;246m"
YELLOW = "\x1b[38;5;220m"
GREEN = "\x1b[38;5;114m"
SPIN = "\x1b[38;5;174m"
CYAN = "\x1b[38;5;37m"
PINK = "\x1b[38;5;217m"
RED = "\x1b[38;5;174m"
BLUE = "\x1b[38;5;74m"
BOLD = "\x1b[1m"
R = "\x1b[0m"

BRANCH = "mot-de-reveil"

events, t = [], 0.0


def out(s):
    events.append([round(t, 3), "o", s])


def pause(d):
    global t
    t += d


def line(s="", d=0.55):
    out(s + "\r\n")
    pause(d)


def typed(s, prefix="", d=1.5):
    global t
    if prefix:
        out(prefix)
        pause(0.7)
    for ch in s:
        out(ch)
        t += random.uniform(0.045, 0.115)
    out("\r\n")
    pause(d)


def rule():
    dashes = "─" * (COLS - len(BRANCH) - 3)
    line(f"{CYAN}{dashes} {BRANCH}{R}", 0.5)


def prompt(text, second=None):
    rule()
    if second is None:
        typed(f"{FG}{text}{R}", prefix=f"{GREEN}❯{R} ", d=1.8)
    else:
        # One continuous typing flow across the wrap: no end-of-line pause, no
        # second prompt char — the composer wraps, it does not hesitate.
        global t
        out(f"{GREEN}❯{R} ")
        pause(0.7)
        out(FG)
        for ch in text:
            out(ch)
            t += random.uniform(0.045, 0.115)
        out(R + "\r\n  ")
        out(FG)
        for ch in second:
            out(ch)
            t += random.uniform(0.045, 0.115)
        out(R + "\r\n")
        pause(1.8)
    line()


def says(text, d=0.9):
    line(f"{FG}●{R} {text}", d)


def cont(text, d=0.9):
    line(f"  {text}", d)


def calling(tool, n=1, d=0.7):
    line()
    line(f"  {DIM}Calling {tool} {n} time{'s' if n > 1 else ''}…{R}", d)


def spinner(word, secs, tokens, d=2.0):
    line(f"{SPIN}· {word}…{R} {DIM}({secs} · ↓ {tokens} tokens){R}", d)
    line()


# --- disclaimer ---------------------------------------------------------
line(f"{YELLOW}  ⚠  Reconstitution condensée — pas une capture en direct.{R}", 0.25)
line(f"{DIM}     Demandes et messages réels, minutage compressé,{R}", 0.25)
line(f"{DIM}     noms d'appareils sanitisés.  labodeludo.dev/casts/{R}", 2.6)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.220{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Opus 5 with high effort · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/git/automatron{R}", 1.4)
line()

# --- 1. the report ------------------------------------------------------
prompt("le double appui marche, l'assistant répond comme il faut, mais l'anneau du",
       "satellite du bureau vire au rouge dès que le mot de réveil part")

says("L'anneau rouge au réveil, avec un assistant qui répond correctement —")
cont("ça sent la couche d'affichage, pas la chaîne vocale. Je vérifie quand", 0.8)
cont("même la piste connue avant de spéculer.", 1.5)

# --- 2. hypothesis one: the known signature -----------------------------
says("Le 5 août, un moteur TTS tombé en « unavailable » donnait exactement")
cont("cette signature. C'est la première chose à écarter.", 1.2)
calling("Bash", 2)
spinner("Interrogation des moteurs", "8s", "1.1k")
line(f"  {DIM}tts.cloud_a       {R}{GREEN}ok{R}   {DIM}dernier appel il y a 1 s{R}", 0.45)
line(f"  {DIM}tts.local_b       {R}{GREEN}ok{R}   {DIM}dernier appel il y a 1 s{R}", 0.45)
line(f"  {DIM}stt.local         {R}{GREEN}ok{R}", 1.3)
says("Tous sains, et deux d'entre eux ont répondu à une seconde d'intervalle.")
cont("Ce n'est pas la signature d'août. Hypothèse écartée.", 1.6)

# --- 3. hypothesis two: about to be tested the slow way -----------------
says("Deuxième piste : l'animation d'écoute du firmware peint l'anneau en")
cont("même temps que mon automatisation. Un conflit en direct expliquerait", 0.8)
cont("pourquoi la couleur est bonne au repos et fausse au réveil.", 1.2)
says("Je redémarre l'appareil pour repartir d'un état propre.")
calling("Bash", 1)
spinner("Redémarrage", "22s", "0.4k")
line(f"  {GREEN}voix-01 en ligne{R}  {DIM}anneau : (255, 0, 0) · luminosité 64{R}", 1.4)
says("Le redémarrage n'a rien changé. Ça pointe vers un conflit vivant")
cont("plutôt que vers un état rémanent — je prépare un test qui coupe", 0.8)
cont("l'animation pour isoler.", 1.8)

# --- 4. the sentence that ends it ---------------------------------------
prompt("l'autre satellite fait la même animation pis sa couleur est correcte")

line()
line(f"  {YELLOW}{BOLD}Ça tue les deux hypothèses d'un coup.{R}", 1.2)
line()
says("Si le jumeau exécute le même firmware et la même animation sans le")
cont("défaut, ce n'est ni le TTS ni l'animation. La différence est ailleurs,", 0.8)
cont("et elle est forcément propre à voix-01.", 1.4)
calling("Bash", 2)
spinner("Comparaison des deux anneaux", "6s", "0.9k")
line(f"  {DIM}voix-01  bureau          {R}{RED}(255, 0, 0){R}   {DIM}luminosité 64{R}", 0.5)
line(f"  {DIM}voix-02  salle à manger  {R}{BLUE}(0, 90, 255){R}  {DIM}luminosité 180{R}", 1.6)
says("Une seule différence entre les deux : l'anneau de voix-01 a été peint")
cont("en ambre par mon automatisation. Celui de voix-02 n'a jamais reçu", 0.8)
cont("de couleur de Home Assistant.", 1.6)

# --- 5. the cause -------------------------------------------------------
says(f"{BOLD}ESPHome persiste la dernière couleur et la dernière luminosité{R}")
cont(f"{BOLD}écrites par HA — en flash.{R} Les animations vocales s'en servent", 0.8)
cont("comme base. L'ambre que j'ai posé est devenu le socle de tout ce que", 0.8)
cont("le firmware dessine ensuite.", 1.8)
line()
line(f"  {YELLOW}Et c'est pour ça que le redémarrage m'a induit en erreur :{R}", 0.9)
line(f"  {YELLOW}il restaure fidèlement la valeur persistée.{R} {DIM}Un état qui{R}", 0.7)
line(f"  {DIM}survit au redémarrage ressemble exactement à une piste écartée.{R}", 2.2)
line()
says("Deuxième erreur de ma part : j'ai validé la couleur pendant que")
cont("l'appareil était au repos. Le repos est le seul état où rien d'autre", 0.8)
cont("ne dessine — ça ne prouvait rien, et c'était toute ma base pour dire", 0.8)
cont("que le changement était sans risque.", 1.8)

# --- 6. the fix ---------------------------------------------------------
says("La remise à zéro tient en deux gestes, et les deux portent :")
cont(f"{GREEN}peindre blanc à pleine luminosité, attendre une seconde, éteindre.{R}", 0.9)
cont("Éteindre seul laisse la couleur en flash — c'est ce qui a créé le", 0.8)
cont("problème la première fois.", 1.6)
calling("Edit", 1)
spinner("Correction de l'automatisation", "31s", "2.4k")
line(f"  {GREEN}rouge tant que désarmé · restauration au ré-armement{R}", 1.8)

# --- 7. the lesson ------------------------------------------------------
line()
line(f"  {CYAN}{'─' * 62}{R}", 0.6)
says("Deux hypothèses, un redémarrage trompeur et un test qui ne prouvait")
cont("rien — et une phrase de ta part a réglé ça en une seconde.", 1.2)
says(f"{BOLD}Ce labo a des paires de presque tout.{R} Le jumeau non modifié est")
cont("un témoin, et j'aurais dû aller le chercher avant de spéculer.", 2.6)
line()

# --- write --------------------------------------------------------------
header = {
    "version": 2, "width": COLS, "height": ROWS,
    "title": "Le témoin : deux hypothèses tuées par un jumeau",
    "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"},
}
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(header, ensure_ascii=False) + "\n")
    for e in events:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
print(f"{OUT}: {len(events)} events, {t:.1f}s")
