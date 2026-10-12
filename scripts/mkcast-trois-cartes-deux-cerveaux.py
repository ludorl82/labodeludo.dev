#!/usr/bin/env python3
"""Build the asciicast for « Trois cartes, deux cerveaux ».

Condensed from two real sessions. The first, on the evening of 2026-09-25
(EDT), was run by Ludo from his phone: Bob's voice moves from the
mixture-of-experts model to the dense 27B. The second, from 2026-10-04 to
2026-10-06, wrote the two companion articles, « un-cerveau-plus-lent-pour-bob »
(Ludo) and « trois-cartes-deux-cerveaux-une-horloge » (Bob), and measured the
prefix with mesure-prefixe.sh along the way.

The real measurement is shown live in « l-heure-dans-le-prompt-prise-reelle ».
This recording tells how the choice was made and what was found, with the
agent's wrong turns left in:

1. Where the voice spends its time: the whole prompt re-read at each
   question. The agent blames the hybrid architecture, « cause probable, pas
   prouvée ».
2. The 27B bench. The cache does work on the hybrid models; what breaks it is
   three lines at the top of the voice prompt (temperature, time to the
   minute, forecast). The agent stops and waits for a go.
3. Ludo is away from his computer: weather becomes a tool, 16 tokens re-read
   instead of 4 505, then the dense model everywhere. The merges are refused
   to the agent; Ludo merges from his phone.
4. « the site chat busts the cache »: the agent agrees and proposes two
   slots. The log answers that this architecture has only one.
5. Nine days later, the measurement script: prompt_eval_count lies, the
   llama-server log does not, and the end of the system prompt is not enough
   (1 024 tokens re-read from a checkpoint). Two corrections of what the agent
   had said on the 25th.
6. « Le cache de Ollama se vide dans quel contexte ? » It did not empty: it
   was warm for the wrong prompt (one per device). And the site chat had
   evicted nothing.

Prompts are verbatim from the transcripts (typos kept). Tool output is
rewritten short. Names follow the articles: the Ollama machine is gpu-01;
no other host, domain, address, PR number or commit hash from the real lab.
Palette and line grammar per net-cfgs/asciicast-style.md; prompt helper is
the fixed (no-pause) one.

Run from the repo root:  python3 scripts/mkcast-trois-cartes-deux-cerveaux.py
"""

import random
from datetime import datetime, timedelta

import claude_tui as T
from claude_tui import BOLD, DIM, GREEN, R, RED, YELLOW, calling, cont, line, says, spinner, waiting


def prompt(*parts, speed=1.0):
    """T.prompt, mais les longues demandes dictées se tapent plus vite
    (speed < 1), comme dans l'ancien script : seul le délai entre les
    caractères change."""
    uniform = random.uniform
    random.uniform = lambda a, b: uniform(a, b) * speed
    try:
        T.prompt(*parts)
    finally:
        random.uniform = uniform


T.setup(
    out="public/casts/trois-cartes-deux-cerveaux.cast",
    title="Trois cartes, deux cerveaux (reconstitution)",
    session="voix-de-bob",
    windows=["backlog", "voix-de-bob"],
    current="voix-de-bob",
    start="25-Sep-26 20:17:52",
    cwd="~/git/labo",
    model="Opus 5.5 · Claude Max",
    seed=25,
)

T.disclaimer("Demandes et messages réels (25 sept. et 4-5 oct. 2026), minutage compressé,",
             "sorties réécrites, noms sanitisés.")
T.banner()


# --- 1. where the voice spends its time ---------------------------------
prompt("Peux tu consulter les ligues de homme assistant pour voir ce qui prend du temps",
       "quand on demande qqch?")
calling("Bash", 4)
spinner("Lecture des traces d'Assist", "38s", "2.9k")
line(f"  {DIM}LLM, premier passage   {R}{RED}2,4 à 3,3 s{R}  {DIM}· outil 0,2 s · second passage 0,5 s{R}", 0.4)
line(f"  {DIM}gpu-01 : new prompt, 5 201 jetons → {R}{RED}forcing full prompt re-processing{R}", 0.4)
line(f"  {DIM}         (likely due to SWA or hybrid/recurrent memory){R}", 1.3)
says("Chaque question relit tout son prompt, environ 2,1 s avant le premier mot.")
says(f"{BOLD}Cause probable, pas prouvée :{R} le modèle est hybride, et llama.cpp ne peut")
cont("pas réutiliser une cache partielle sur ce genre de modèle.", 1.3)

# --- 2. the dense bench, and the real culprit ---------------------------
prompt("Je veux surtout évaluer si le modèle 27b pourrait offrir des meilleures performances",
       "avec des ajustements")
calling("Bash", 7)
spinner("Banc sur gpu-01", "6m 05s", "4.4k")
line(f"  {DIM}                    lecture du prompt   avec cache   génération{R}", 0.3)
line(f"  {DIM}35B-A3B (prod)      2 778 j/s           0,1 s        77 j/s{R}", 0.3)
line(f"  {DIM}27B dense             850 j/s           0,2 s        {R}{YELLOW}18 j/s{R}", 1.4)
says(f"{BOLD}La cache fonctionne sur ces modèles hybrides, contrairement à ce que je croyais.{R}")
cont("À préfixe identique, la lecture tombe à 0,1 s. Ce qui la casse, c'est ton prompt", 0.8)
cont("de la voix : ses premières lignes changent à chaque question.", 0.8)
line(f"  {DIM}Température actuelle : {{{{ … }}}}°C{R}", 0.3)
line(f"  {DIM}Aujourd'hui : … {{{{ now().strftime('%d/%m/%Y, %H:%M') }}}}{R}", 0.3)
line(f"  {DIM}Prévisions : {{{{ … }}}}{R}", 1.2)
says("La modif demande d'arrêter et de redémarrer Home Assistant : j'attends ton go.")
waiting()

# --- 3. from the phone: weather becomes a tool, then the dense model ----
prompt("Je veux que tu fasses les changements je ne suis pas à mon ordi")
calling("Bash", 9)
spinner("Outil meteo, prompt allégé", "4m 20s", "3.6k")
line(f"  {DIM}quelle est la température    3,6 s   4 505 jetons relus   (cache vide){R}", 0.3)
line(f"  {DIM}quelle est la météo demain   1,4 s   {R}{GREEN}   16 jetons relus{R}", 0.3)
line(f"  {DIM}quel jour on est             0,5 s   {R}{GREEN}   22 jetons relus{R}", 1.4)
prompt("On va je changer pour de bon, assurés toi qu'il est utilisé sur le site, sur ha et",
       "sur les jobs nocturnes")
calling("Edit", 6)
spinner("Changement de modèle", "11m 40s", "7.8k")
says(f"La voix roule sur {GREEN}Qwen3.8-27B{R}, testée : 1,3 à 5 s par question.")
says(f"Les trois fusions me sont {RED}refusées{R} (« Merge Without Review ») : c'est à toi.", 0.6)
waiting()

# --- 4. the site chat, accused ------------------------------------------
prompt("Hey maybe it's not worth it if the site chat busts the cache")
says("Tu as raison : Ollama n'a qu'une place de traitement. Une seule question au chat")
cont(f"du site viderait la cache de la voix. Remède : {GREEN}OLLAMA_NUM_PARALLEL=2{R}, une place chacun.", 1.4)
prompt("Fusionné, est-ce que ça va redémarrer Bob?")
calling("Bash", 3)
line(f"  {DIM}gpu-01 : {R}{YELLOW}WARN \"model architecture does not currently support parallel{R}", 0.2)
line(f"  {YELLOW}         requests\" architecture=qwen35{R}", 1.4)
says(f"{BOLD}Aucun effet.{R} Cette version d'Ollama force une seule place pour ce modèle.")
cont("Pas moyen de donner à la voix et au chat des caches séparées.", 1.3)

# --- 5. nine days later: measure it -------------------------------------
T.separator("4 octobre · la session des articles")
T.set_clock("04-Oct-26 10:32:18")
prompt("J'aimerais que tu écrives les deux articles maintenant. Celui de Bob et celui de Ludo.",
       "Ils sont au backlog. J'aimerais aussi qu'on fasse un asciicast et qu'on les traduise. On",
       "les publiera sur article LinkedIn aussi (celui de Ludo). Mardi en français et jeudi en",
       "anglais. Cette fois je voudrais utiliser la bannière de l'article comme affiche pour",
       "l'article LinkedIn, pas la vidéo.", speed=0.15)
calling("Bash", 5)
spinner("mesure-prefixe.sh, répétition", "1m 12s", "2.2k")
line(f"  {DIM}prompt_eval_count   {R}{RED}4 501 · 4 501 · 4 501{R}  {DIM}— Ollama renvoie toujours le total{R}", 0.5)
line(f"  {DIM}→ lire le journal de llama-server à la place{R}", 0.6)
line(f"  {DIM}l'heure en tête du prompt système   4,88 s   {R}{RED}3 483 jetons relus{R}", 0.4)
line(f"  {DIM}l'heure à la fin du prompt système  2,23 s   {R}{YELLOW}1 024 jetons relus{R}", 0.4)
line(f"  {DIM}l'heure dans la question            0,37 s   {R}{GREEN}   29 jetons relus{R}", 1.5)
says(f"{BOLD}La fin du prompt système ne suffit pas.{R} Un hybride ne reprend qu'à un point de")
cont("contrôle, et le seul pris avant l'heure tombe environ mille jetons plus haut.", 1.0)
says("Et deux choses que je t'ai dites le 25 septembre étaient fausses : Home Assistant")
cont(f"n'ajoute pas l'heure à la fin, il donne l'outil {GREEN}GetDateTime{R} ; et le « 5 200 → 4 500", 0.8)
cont("jetons » n'était pas l'effet du correctif, mais l'écart entre deux appareils.", 1.3)

# --- 6. warm for the wrong prompt ---------------------------------------
prompt("Le cache de Ollama se vide dans quel contexte? Je cherche à expliquer pourquoi ça prenait",
       "parfois encore plusieurs secondes autres notre première correction", speed=0.45)
says(f"Elle ne se vidait presque jamais. {BOLD}Elle était chaude pour le mauvais prompt.{R}")
cont("Une question du Voice PE ajoute sa pièce et ses minuteries : le prompt diffère dès", 0.8)
cont("le jeton 3 761, avant tout point de contrôle. Le réchauffement de 6 h, lui, ne", 0.8)
cont("pouvait pas dire de quel appareil il venait.", 1.0)
line(f"  {DIM}salle à manger : 'Dis-moi juste bonsoir.'   {R}{RED}7,4 s{R}", 0.3)
line(f"  {DIM}salle à manger : 'Dis-moi juste allô.'      {R}{GREEN}0,8 s{R}", 1.3)
says(f"Et ce n'était {BOLD}pas le chat du site{R} : après une question au chat, la voix a")
cont("restauré son point de contrôle et relu 4 jetons. On l'a soupçonné deux fois.", 1.8)

# --- the lesson ---------------------------------------------------------
line()
says(f"{BOLD}Dans un prompt mis en cache, ce qui change va à la fin.{R} Sur un hybride, la")
cont("fin, c'est après le dernier point de contrôle : la question, ou la réponse d'un outil.", 2.4)
line()

T.save()
