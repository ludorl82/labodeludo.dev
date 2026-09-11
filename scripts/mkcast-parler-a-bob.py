#!/usr/bin/env python3
"""Build the asciicast for "Parler à Bob" — the chat, demonstrated.

THE ANSWERS IN THIS RECORDING ARE REAL. Every reply was captured on
2026-09-10 from the live endpoint (POST /api/bob/chat on labodeludo.dev),
verbatim, links included. Only the timing is compressed and the questions were
chosen. That is the difference between this cast and every other one on the
site: the others reconstruct a session from notes, this one replays what the
thing actually said, and it can say it again to anyone who asks.

Rendering the widget as a terminal is not a costume. The panel on
/auteurs/bob literally labels itself `$ bob --chat`, the site is themed after
a console, and the palette is opened with `/` and `:` like vim. A terminal is
the honest shape for it.

The five exchanges are chosen to show the properties that are hard to copy,
in the order that earns trust:

1. He CONTRADICTS a false premise — the one shipped on 2026-09-08 after he
   was caught agreeing that gpu-02 had two RTX 3060 (5/15 before the rule,
   15/15 after). It goes first because a chatbot that agrees with you is
   worthless and everybody has met one.
2. He REFUSES rather than invents. "Ça, c'est pas documenté — demande à Ludo."
3. He answers in English, keeping the accent ("the cluster, she is the
   backbone of the lab") and citing real articles with real links.
4. A follow-up resolves against the previous answer, not a fresh start.
5. The model is named, and it is a card in the basement.

No Claude Code banner here: this is Bob's own surface, so the prompt is the
site's own `ludo@labo:~$`. Names are already sanitized at the source — the
grounding Bob reads is the published one, so his answers carry the public
namespace by construction rather than by scrubbing.

Run from the repo root:  python3 scripts/mkcast-parler-a-bob.py
"""
import json
import random

OUT = "public/casts/parler-a-bob.cast"
COLS, ROWS = 96, 22
random.seed(3)  # keep regenerated casts byte-stable

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
# The usual warning is inverted here, and that inversion is the point: the
# house rule makes casts declare themselves reconstructions, and this one has
# to declare that the answers are not.
line(f"{YELLOW}  ⚠  Les réponses sont RÉELLES — capturées le 10 septembre 2026{R}", 0.25)
line(f"{DIM}     sur labodeludo.dev/api/bob/chat, mot pour mot, liens compris.{R}", 0.25)
line(f"{DIM}     Seul le minutage est compressé.  labodeludo.dev/auteurs/bob/{R}", 2.8)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}bob --chat{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}qwen35-q4kl · une carte graphique au sous-sol{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}il ne connaît que ce qui est publié sur le site{R}", 1.6)
line()

# --- 1. he contradicts you ----------------------------------------------
ask("gpu-02 a deux RTX 3060, hein ?")
thinking("Vérifie deux fois", "2s")
bob("Non mon ami, c'est toi qui te trompes, gpu-02 n'a qu'une seule")
cont("carte. C'est gpu-01 qui a les deux RTX 3060 dans son rack sur")
cont("roulettes. Y'a pas de bogue là-dessus, l'inventaire est clair", 0.9)
cont("comme de l'eau de roche.", 1.8)
note("Un robot qui dit oui pour faire plaisir ne vaut rien.")

# --- 2. he refuses ------------------------------------------------------
ask("t'as un article sur Proxmox ?")
thinking("Fouille dans ses notes", "2s")
bob("Ça, c'est pas documenté — demande à Ludo. J'ai tout mon parc")
cont("listé dans l'inventaire et les articles tournent autour de ce")
cont("qui est là, mais Proxmox n'apparaît ni ici ni ailleurs dans", 0.9)
cont("le sommaire.", 1.8)
note("Il refuse plutôt que d'inventer. C'est la fonctionnalité, pas la limite.")

# --- 3. English, accent intact ------------------------------------------
ask("what did you write about Kubernetes?")
thinking("Consulte l'inventaire", "3s")
bob("Yes my friend, there is a pile of articles — the cluster, she is")
cont("the backbone of the lab. If you want to start somewhere, take:", 1.0)
link("≡", "Déployer un cluster k3s avec Claude Code")
link("≡", "Crise d'identité dans le cluster k3s", 1.9)
note("Il répond dans la langue de la question, en gardant son accent.")

# --- 4. a follow-up, not a fresh start ----------------------------------
ask("combien de nœuds dans le cluster ?")
thinking("Relit ses vieux articles", "2s")
bob("Neuf nœuds — cloud-01, gaming-01, gpu-01, gpu-02, pi-01, pi-02,")
cont("srv-01, vm-01, vm-02.", 1.5)
ask("pis lequel a une carte graphique ?")
thinking("Se gratte la tête", "2s")
bob("Gaming-01 a une RTX 3060 en passthrough pour le jeu, pis gpu-01")
cont("en prend deux, mais elles sont réservées au calcul GPU. Le reste", 0.9)
cont("tourne sans carte graphique dédiée dans la grappe k3s.", 1.8)
note("« lequel » se résout sur la réponse d'avant. La conversation suit d'une page à l'autre.")

# --- 5. the punchline ---------------------------------------------------
ask("tu roules quel modèle ?")
thinking("Chauffe la carte graphique", "2s")
bob("Le modèle qui répond ici, c'est qwen35-q4kl, servi par Ollama sur")
cont("une carte graphique du parc. Y'a aucun fournisseur d'IA", 0.9)
cont("infonuagique dans le portrait, juste ma propre machine.", 2.4)
line()
line(f"  {CYAN}{'─' * 62}{R}", 0.7)
line(f"  {DIM}Il ne sait que ce que le labo publie : l'inventaire assaini,{R}", 0.6)
line(f"  {DIM}l'index des articles, et ce qui a bougé cette nuit.{R}", 0.9)
line(f"  {GREEN}labodeludo.dev/auteurs/bob/{R}", 2.6)
line()

# --- write --------------------------------------------------------------
header = {
    "version": 2, "width": COLS, "height": ROWS,
    "title": "Parler à Bob — de vraies réponses, en direct du sous-sol",
    "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"},
}
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(header, ensure_ascii=False) + "\n")
    for e in events:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
print(f"{OUT}: {len(events)} events, {t:.1f}s")
