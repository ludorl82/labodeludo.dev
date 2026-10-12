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

import claude_tui as T
from claude_tui import BLUE, BOLD, CYAN, DIM, GREEN, R, RED, YELLOW, calling, cont, line, prompt, says, spinner

T.setup(
    out="public/casts/le-temoin.cast",
    title="Le témoin : deux hypothèses tuées par un jumeau",
    session="mot-de-reveil",
    windows=["backlog", "mot-de-reveil"],
    current="mot-de-reveil",
    start="10-Sep-26 20:42:15",
    cwd="~/git/domotique",
    model="Opus 5 · Claude Max",
    seed=11,
)

T.disclaimer("Demandes et messages réels, minutage compressé,",
             "noms d'appareils sanitisés.")
T.banner()

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

T.save()
