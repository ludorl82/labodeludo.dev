#!/usr/bin/env python3
"""Build the asciicast for « Le cluster ramasse les cartes ».

Condensed from the real session of 2026-09-14 (evening, continued past
midnight UTC into the 15th), the one Bob wrote up as
« quand-personne-ne-joue-le-cluster-ramasse-les-cartes ». The session also
renamed the tower and fixed its DNS and BMC; this recording keeps only the
GPU thread.

1. « Rendre la GTX 960 disponible pour Kubernetes »: the driver goes on the
   host, the reboot leaves a ghost (Ready, lease fresh, no container starts).
   The agent blames k3s's PATH, and locks itself out of SSH with its own
   wait loop. It stops and asks.
2. Ludo has no keyboard and sends a photo of the screen: a chain of hung
   tasks led by iptables-restor, modprobe stuck behind bridge. The agent
   retracts the PATH theory, reverts the driver, and asks for a power cycle.
3. The driver goes into a VM (vm-03). The agent catches its own synchronous
   virsh call inside the libvirt hook and makes it asynchronous.
4. Three cards will not boot. The bisect compares a VM with an install CD to
   a VM without one; a screenshot shows the UEFI shell. MMIO window: no
   effect, the agent settles for one card. Ludo asks for other ideas:
   <rom bar='off'/> on the six functions, three cards in 24 s.
5. The live swap test finds four bugs: sudo masked by PATH (the setuid one
   lives in /run/wrappers/bin), a cordon that survives the reboot, a fixed
   systemd-run unit name « already loaded », a shutdown sent before the
   guest agent is up. Then « rends jeu-ctl patient », and no destroy.

Prompts are verbatim from the transcript (typos kept); host names are
replaced by the article's: the tower is gaming-01, the GPU node vm-03, the
two gaming VMs jeu-01 / jeu-02, the swap script jeu-ctl. Tool output is
rewritten short. No domains, addresses, keys or commit hashes from the real
lab. Palette and line grammar per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-le-cluster-ramasse-les-cartes.py
"""
import json
import random

OUT = "public/casts/le-cluster-ramasse-les-cartes.cast"
COLS, ROWS = 96, 22
random.seed(14)  # keep regenerated casts byte-stable

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

BRANCH = "master"

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
            t += random.uniform(0.035, 0.085)
    out(R + "\r\n")
    pause(1.3)
    line()


def says(text, d=0.9):
    line(f"{FG}●{R} {text}", d)


def cont(text, d=0.9):
    line(f"  {text}", d)


def calling(tool, n=1, d=0.7):
    line()
    line(f"  {DIM}Calling {tool} {n} time{'s' if n > 1 else ''}…{R}", d)


def spinner(word, secs, tokens, d=1.4):
    line(f"{SPIN}· {word}…{R} {DIM}({secs} · ↓ {tokens} tokens){R}", d)
    line()


def waiting():
    line()
    line(f"  {DIM}waiting for you…{R}", 2.6)


# --- disclaimer ---------------------------------------------------------
line(f"{YELLOW}  ⚠  Reconstitution condensée — pas une capture en direct.{R}", 0.25)
line(f"{DIM}     Demandes et messages réels (14-15 sept. 2026), minutage compressé,{R}", 0.25)
line(f"{DIM}     sorties réécrites, noms sanitisés.  labodeludo.dev/casts/{R}", 2.2)
line()

# --- banner -------------------------------------------------------------
line(f"{PINK}  ▄▄▄▄▄▄▄▄{R}   {BOLD}Claude Code{R} {DIM}v2.1.214{R}", 0.2)
line(f"{PINK}  █ ██ ██ █{R}  {DIM}Opus 5 with high effort · Claude Pro{R}", 0.2)
line(f"{PINK}  ▀▀    ▀▀{R}  {DIM}~/git/labo{R}", 0.9)
line()

# --- 1. the driver on the host, and a ghost ------------------------------
prompt("Je viens de déplacer la gtx 960 et j'ai mis la nouvelle 3050 à sa place. Peux tu",
       "connecter la nouvelle 3050 à jeu-01 et rendre gtx960 disponible pour kubernetes")
calling("Bash", 9)
spinner("Lecture du bus PCI", "3m 12s", "4.4k")
line(f"  {DIM}17:00.0  10de:1401  GTX 960   (Maxwell)  → libérée de vfio{R}", 0.3)
line(f"  {DIM}65:00.0  10de:2507  RTX 3050  (GA106)    → jeu-01 · ce n'est PAS la 3050 de jeu-02{R}", 1.2)
says(f"La 960 est une Maxwell : pilote {GREEN}legacy_580{R} imposé, sinon aucun pilote.")
cont("Pilote + CDI sur gaming-01, poussé. Veux-tu que je redémarre ?", 0.6)
waiting()

prompt("Oui vas y")
calling("Bash", 7)
spinner("Redémarrage de gaming-01", "6m 04s", "2.9k")
line(f"  {DIM}nœud gaming-01   {R}{GREEN}Ready{R}  {DIM}· bail renouvelé il y a 8 s{R}", 0.4)
line(f"  {DIM}pod de test      {R}{RED}ContainerCreating · délai dépassé (sandbox){R}", 0.4)
line(f"  {DIM}ssh              {R}{RED}« Not allowed at this time »{R}", 1.4)
says(f"C'est {BOLD}mon changement{R} qui a cassé la création de conteneurs. Suspect :")
cont("le PATH de l'unité k3s, que j'ai peut-être remplacé au lieu de l'étendre.", 0.8)
says("Et je ne peux pas le vérifier : ma boucle d'attente a martelé sshd au")
cont(f"démarrage, {BOLD}je me suis verrouillé dehors{R}. J'aurais dû sonder le bail.", 0.8)
cont(f"Si tu peux taper {GREEN}journalctl -u k3s -n 40{R} devant la machine…", 0.6)
waiting()

# --- 2. the photo -------------------------------------------------------
prompt("Je vais pas de clavier, voici l'écran")
line(f"  {DIM}[photo de l'écran]  INFO: task iptables-restor blocked for more than 122 s{R}", 0.4)
line(f"  {DIM}                    bridge · k3s-agent · modprobe · udev-worker → en attente{R}", 1.3)
says(f"Ce n'est pas le PATH, {BOLD}je retire cette hypothèse{R}. C'est un blocage noyau :")
cont("modprobe coincé, k3s n'obtient jamais br_netfilter, aucun conteneur ne naît.", 0.8)
cont(f"Le seul élément nouveau : le module NVIDIA ({RED}Tainted: P{R}). Je le retire.", 1.0)
says("Retour arrière poussé, mais sshd n'ouvre plus de session.")
cont(f"{BOLD}Peux-tu l'éteindre et la rallumer ?{R}", 0.6)
waiting()

# --- 3. the driver goes in a box ----------------------------------------
prompt("Peux tu vérifier si vm-03 n'est pas déjà sur gaming-01? Sinon créé la et on va",
       "faire ça tout de suite")
calling("Write", 4)
spinner("Écriture de vm-03", "4m 51s", "7.8k")
line(f"  {DIM}vm-03   q35 + OVMF · GTX 960 en passthrough · pilote dans l'invité{R}", 1.0)
says("Un point me gêne dans ce que je viens d'écrire : le hook libvirt appelle")
cont(f"virsh {BOLD}de façon synchrone{R}, pendant que libvirtd tient ses verrous.", 0.8)
cont(f"Il passe par {GREEN}systemd-run --no-block{R}. Le noyau de l'hôte reste propre.", 1.4)

# --- 4. three cards, a bad bisect, one line of XML ----------------------
prompt("Oui construit vm-03. Est-ce qu'on peut aussi attendre des tâches gpu sur",
       "gaming-01 quand les 2 rtx 3050 ne sont pas en fonction sur jeu")
calling("Bash", 23)
spinner("Démarrage de vm-03 avec trois cartes", "26m 40s", "9.6k")
line(f"  {DIM}0 carte            {R}{GREEN}installeur debout en 24 s{R}", 0.4)
line(f"  {DIM}1 carte            {R}{RED}rien{R}", 0.4)
line(f"  {DIM}virsh screenshot   {R}{YELLOW}Shell> — lecteur CD vide{R}", 1.3)
says(f"{BOLD}Mon bisect était faussé.{R} La variante à une carte venait du XML du dépôt,")
cont("où le lecteur est vide : j'ai comparé une VM avec CD à une VM sans.", 0.8)
cont(f"Une carte démarre. Trois calent. Fenêtre MMIO à 64 Gio : {RED}sans effet{R}.", 0.8)
cont("J'installe vm-03 avec la 960 seule et je m'arrête là pour ce soir.", 1.6)

prompt("Any clue how else we can pas the cards to vm-03?")
says(f"Piste 1 : {GREEN}<rom bar='off'/>{R}. OVMF exécute la ROM de chaque carte pendant")
cont("l'énumération PCI. Une VM de calcul n'affiche rien, elle n'a besoin d'aucun GOP.", 0.6)
waiting()
prompt("Ouais vas-y ")
calling("Bash", 6, 0.5)
says(f"Réglé par la première piste : {BOLD}c'était l'option ROM{R}, pas le nombre de cartes.", 0.6)
line(f"  {DIM}vm-03   démarrage en 24 s · nvidia-smi : 960 4 Go · 3050 8 Go · 3050 6 Go{R}", 0.4)
line(f"  {DIM}pod CUDA   {R}{GREEN}GPU 0, 1, 2{R}  {DIM}· 18 Go de VRAM quand personne ne joue{R}", 1.6)

# --- 5. the swap, tested live -------------------------------------------
prompt("Peux tu tester jeu 1 et jeu 2 aussi?")
calling("Bash", 31)
spinner("Cycles start / stop", "45m 30s", "12.1k")
line(f"  {DIM}drain vm-03   {R}{RED}sudo: …/sw/bin/sudo must be owned by uid 0 and have the setuid bit set{R}", 0.5)
line(f"  {DIM}release       {R}{RED}vm-03 revient SchedulingDisabled{R}", 0.5)
line(f"  {DIM}2ᵉ cycle      {R}{RED}Unit gamemode-start-vm-03.service was already loaded{R}", 0.5)
line(f"  {DIM}stop jeu-01   {R}{RED}QEMU guest agent is not connected{R}", 1.4)
says("Quatre bogues, et mes deux premiers correctifs « évidents » ont échoué :")
cont(f"le seul sudo setuid de NixOS vit dans {GREEN}/run/wrappers/bin{R}, que mon PATH", 0.8)
cont("masquait. Le cordon survit au reboot : le hook décordonne au release.", 0.8)
cont(f"Noms d'unité générés + {GREEN}--collect{R}. 3ᵉ cycle : {GREEN}vm-03 drained{R}.", 1.6)

prompt("Rend jeu-ctl patient stp. ")
says("stop attend l'agent invité (plafond 90 s), puis arrête proprement.")
cont(f"Et {BOLD}jamais de destroy{R} en repli : tuer une VM en plein démarrage, c'est", 0.8)
cont("comme ça qu'une de ces cartes est déjà restée coincée jusqu'au reboot de l'hôte.", 1.4)

# --- the lesson ---------------------------------------------------------
line()
says(f"Ce n'est pas la relecture qui a tranché. {BOLD}C'est le cycle rejoué en direct.{R}")
cont("Et deux fois ce soir, une capture d'écran a dit en une image ce que", 0.6)
cont("vingt minutes de déduction n'avaient pas trouvé.", 1.6)
line()

# --- write --------------------------------------------------------------
header = {
    "version": 2, "width": COLS, "height": ROWS,
    "title": "Le cluster ramasse les cartes (reconstitution)",
    "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"},
}
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(header, ensure_ascii=False) + "\n")
    for e in events:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
print(f"{OUT}: {len(events)} events, {t:.1f}s")
