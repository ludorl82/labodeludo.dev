#!/usr/bin/env python3
"""Build the asciicast for « La porte d'en arrière ».

Condensed from the real sessions of 2026-09-23 and 2026-09-24: the hosts
with two legs (VLAN 10 and VLAN 50) that answer by the wrong one, and the
module that fixed it. The companion article is Bob's
« corollaire-la-porte-d-en-arriere »; the real-capture cast
« la-mauvaise-patte-prise-reelle » shows the failure itself. This one tells
the session that understood and fixed it.

1. Back to the original problem. From the Mac everything passes (200 MB in
   ten seconds); the failure hits cloud-01, outside both subnets. The agent's
   first manual try runs nothing (its own shell is zsh, the variable never
   split); redone through stdin: fail, banner, fail. Rules 100/101, a witness
   on vm-02, then the stop for the merge.
2. Merged: two more wirings proven by hand, the fleet module, 18 legs of 18.
   A failing pod is checked, dated a week earlier, not the agent's.
3. The next day: SSH from the Mac freezes. The case the agent had left out on
   purpose, because a ten-second transfer never meets a 30 s idle timeout.
   The pfSense state (22:0 pkts), and rule 102.
4. The same evening, the freeze again: port 2222 is a Docker container, the
   reply leaves from the container's address, rule 102 never sees it.
   Connection mark + rule 103, tried by hand, then deployed.
   (Traefik, the same mechanism on the k3s nodes, is left out: see the
   article.)

Prompts are verbatim from the transcript (typos kept); the real host name in
two of them is replaced by the article's. Tool output is rewritten short.
Names and addresses follow the article: vm-02, console-vm, pi-01, srv-01,
cloud-01, the Mac, pfSense; 192.0.2.0/24 (VLAN 10), 203.0.113.0/23 (VLAN 50),
198.18.0.2 for cloud-01. No PR numbers or commit hashes from the real lab.
Palette and line grammar per net-cfgs/asciicast-style.md; prompt helper is
the fixed (no-pause) one.

Run from the repo root:  python3 scripts/mkcast-la-porte-d-en-arriere.py
"""

from datetime import datetime, timedelta

import claude_tui as T
from claude_tui import BOLD, DIM, GREEN, R, RED, calling, cont, line, prompt, says, spinner, waiting


T.setup(
    out="public/casts/la-porte-d-en-arriere.cast",
    title="La porte d'en arrière (reconstitution)",
    session="deux-pattes",
    windows=["backlog", "deux-pattes"],
    current="deux-pattes",
    start="23-Sep-26 20:42:15",
    cwd="~/git/labo",
    model="Opus 5.5 · Claude Max",
    seed=23,
)

T.disclaimer("Demandes et messages réels (23 et 24 sept. 2026), minutage compressé,",
             "sorties réécrites, noms sanitisés.")
T.banner()


# --- 1. back to the original problem ------------------------------------
prompt("ok merci ça fonctionne. est-ce qu'on peut revenir maintenant au problème original",
       "avec les dual homed qui répondent par la patte 50")
calling("Bash", 4)
spinner("Reproduction de la panne", "4m 12s", "2.9k")
line(f"  {DIM}Mac → vm-02 (VLAN 10)      {R}{GREEN}200 Mo en 10 s{R}", 0.4)
line(f"  {DIM}cloud-01 → vm-02 (VLAN 50) {R}{GREEN}ping ok{R}  {RED}TCP : échec{R}", 0.4)
line(f"  {DIM}ip route get 198.18.0.2 from 203.0.113.134  →  via 192.0.2.254 dev {R}{RED}ens2{R}", 1.4)
says("Depuis ton Mac, tout passe. La panne frappe un pair hors des deux réseaux,")
cont("comme cloud-01 : la réponse part de l'adresse 50, mais suit la route par", 0.8)
cont(f"défaut, côté VLAN 10. {BOLD}pfSense voit revenir la réponse par l'autre porte.{R}", 1.4)
says("J'applique les deux règles à la main, je teste, je les retire.")
says(f"{RED}Rien n'a tourné{R} : mon propre shell est aussi zsh, et la variable ne")
cont("s'est pas découpée. Aucune règle posée. Je refais par l'entrée standard.", 1.2)
calling("Bash", 3)
line(f"  {DIM}vm-02, depuis cloud-01   avant : {R}{RED}échec{R}{DIM}   règles posées : {R}{GREEN}bannière{R}"
     f"{DIM}   retirées : {R}{RED}échec{R}", 1.4)
says(f"{GREEN}100{R} : la table principale {BOLD}sans sa route par défaut{R} (suppress_prefixlength 0)")
cont("— le LAN et les pods gardent leur chemin. " f"{GREEN}101{R} : le reste repart côté 50.", 0.8)
cont(f"Module {GREEN}labo.dualHomed{R}, activé sur vm-02 seulement, comme témoin.", 0.6)
waiting()

# --- 2. merged: the fleet -----------------------------------------------
prompt("C'est fusionné")
spinner("Déploiement par comin, puis essais", "8m 03s", "4.4k")
says("Le témoin tient. Avant d'élargir, les deux autres câblages, à la main :")
line(f"  {DIM}pi-01  (physique)      avant : {R}{RED}échec{R}{DIM}   règles : {R}{GREEN}bannière{R}"
     f"{DIM}   retirées : {R}{RED}échec{R}", 0.4)
line(f"  {DIM}srv-01 (hyperviseur)   avant : {R}{RED}échec{R}{DIM}   règles : {R}{GREEN}bannière{R}"
     f"{DIM}   retirées : {R}{RED}échec{R}", 1.2)
cont("Les treize systèmes s'évaluent. La PR pour les huit autres est prête.", 0.6)
waiting()

prompt("Fusionné")
spinner("Vérification depuis cloud-01", "2m 31s", "3.0k")
line(f"  {DIM}9 hôtes déployés en < 2 min · TCP, deux pattes chacun : {R}{GREEN}18 / 18{R}", 0.4)
line(f"  {DIM}k3s : 10 noeuds Ready · 1 pod en échec{R}", 1.2)
says("Ce pod est un essai raté d'une CronJob, daté du 16 septembre. Il est")
cont("antérieur à mon changement : pas de ma faute, mais à regarder un jour.", 1.8)

# --- 3. the next day: the freeze ----------------------------------------
T.separator("le lendemain")
T.set_clock("24-Sep-26 13:05:40")
prompt("ok pas grave, je ne reinitialiserai pas le mb. Peux-tu voir pourquoi quand je me",
       "connecte par ssh à console-vm.lab.example aprèes une ou deux minutes la connexion",
       "ssh gèle?")
says("Ça ressemble fortement à ce que j'avais volontairement laissé de côté.")
cont("Ton Mac joint l'adresse VLAN 10 par pfSense ; la réponse revient directement", 0.8)
cont("par la patte 50. Je le vérifie avant de toucher quoi que ce soit.", 1.0)
calling("Bash", 5)
spinner("Lecture de la table d'états", "6m 40s", "3.6k")
line(f"  {DIM}mvneta0.10  203.0.113.37 -> 192.0.2.136:22   {R}{RED}SYN_SENT:CLOSED{R}", 0.4)
line(f"  {DIM}            expires in 00:00:24 · {R}{RED}22:0 pkts{R}", 1.4)
says(f"Pour pfSense, la connexion ne s'est jamais établie. {BOLD}Il l'oublie après 30 s{R}")
cont("de silence, et jette le caractère suivant.", 1.0)
says(f"{BOLD}Un cas laissé de côté exprès, à tort.{R} Mon transfert de 200 Mo durait dix")
cont(f"secondes : {BOLD}un essai court ne rencontre jamais un délai d'inactivité.{R}", 1.2)
cont(f"Règle {GREEN}102{R} : ce qui part de l'adresse VLAN 10 vers le LAN repasse par pfSense.", 1.6)

# --- 4. the same evening: the container ---------------------------------
prompt("J'ai encore le problème de connexion ssh sur console-vm. Peux tu vérifier si la",
       "règle de routage de source est toujours bien appliquée?")
calling("Bash", 6)
spinner("Règles et fiches de pfSense", "5m 02s", "4.1k")
line(f"  {DIM}ip rule sur console-vm          {R}{GREEN}100 101 102 présentes{R}", 0.4)
line(f"  {DIM}port 2222 → DNAT vers le conteneur de la console, port 22{R}", 0.4)
line(f"  {DIM}mvneta0.10  … -> 192.0.2.136:2222   {R}{RED}SYN_SENT:CLOSED · 24:0 pkts{R}", 1.4)
says("Les règles marchent pour ce qu'elles couvrent. Ta connexion prend le seul")
cont(f"chemin qu'elles ne voient pas : la réponse part de {BOLD}l'adresse du conteneur{R}.", 0.8)
cont("Option 1 : marquer la connexion à l'entrée, la reprendre à la sortie.", 0.6)
waiting()

prompt("ok faisons l'option 1")
calling("Bash", 4)
line(f"  {DIM}45 s de silence, marque posée    {R}{GREEN}ESTABLISHED:ESTABLISHED · ligne reçue{R}", 0.4)
line(f"  {DIM}45 s de silence, marque retirée  {R}{RED}Broken pipe{R}", 1.2)
says(f"Option {GREEN}dnatReplies{R} : CONNMARK + règle {GREEN}103{R}, sur console-vm seulement.", 1.6)

prompt("ok vas y")
spinner("Déploiement, puis 45 s et 150 s de silence", "4m 55s", "2.2k")
says("Tu peux retourner sur ssh console-vm.lab.example -p 2222 : la session ne gèle plus.")
cont(f"Les deux lignes arrivent. pfSense voit {GREEN}les deux sens{R}, fiche gardée 24 h.", 2.8)
line()

T.save()
