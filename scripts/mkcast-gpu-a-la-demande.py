#!/usr/bin/env python3
"""Build the asciicast for « Le GPU à la demande » (reconstitution).

Condensed from the real session of 2026-08-22, the day the second gaming
station got its card. The companion article is « gpu-a-la-demande-a-la-maison »
(Ludo). The session ran on for days afterwards (Plasma 6, Remote Play, the
removal of the second network leg); none of that is here. This recording
covers August 22 only.

Four beats, each one a thing that looked like something else:

1. « Ajoute ma 3050 sur arcade2. » The card sits alone in its IOMMU group, the
   change is three files, CI is green. The agent's drain-and-reboot is refused
   by the permission classifier, and turns out to be unnecessary.
2. Ludo proposes removing the guests' home-network address; the agent argues
   to keep it (an earlier « ne répond pas au ping » was just a boot, cut here).
   Then Ludo names the real
   problem himself: asymmetric routing on a dual-homed guest. The agent stops
   with two options, Ludo picks A: source-based policy routing.
3. The stop switch stays yellow. The guest hung on the NVIDIA driver teardown;
   after a forced stop, the card reads all 0xFF on the host (D3cold). The
   agent is blocked on the PCI rescan and waits; Ludo says reboot.
4. « fix it for good » : arcade1 is not down, it is PAUSED. Its games SSD fell
   off the bus. /games moves to a qcow2 on the host's NVMe; the library is lost.

Prompts are verbatim from the transcript (typos kept); one address inside a
prompt is replaced by a documentation range. Tool output is rewritten short.
Names follow the article: the host is gaming-01, the guests arcade1/arcade2.
Addresses: 192.0.2.0/24 (server network), 198.51.100.0/24 (home network).
Palette and line grammar per net-cfgs/asciicast-style.md; prompt helper is the
fixed (no-pause) one.

Run from the repo root:  python3 scripts/mkcast-gpu-a-la-demande.py
"""

import claude_tui as T
from claude_tui import BOLD, DIM, GREEN, R, RED, YELLOW, calling, cont, line, prompt, says, spinner, waiting

T.setup(
    out="public/casts/gpu-a-la-demande.cast",
    title="Le GPU à la demande (reconstitution)",
    session="arcade",
    windows=["backlog", "arcade"],
    current="arcade",
    start="22-Aug-26 14:26:09",
    cwd="~/git/labo",
    model="Fable 5 · Claude Max",
    seed=22,
)

T.disclaimer("Demandes et messages réels (22 août 2026 seulement), minutage compressé,",
             "sorties réécrites, noms et adresses sanitisés.")
T.banner()


# --- 1. the card ---------------------------------------------------------
prompt("Salut peux tu ajouter ma rtx3050 sur arcade2. je viens de l'ajouter dans le serveur")

calling("Bash", 5)
spinner("Inventaire PCI de gaming-01", "43s", "2.1k")
line(f"  {DIM}17:00.0  10de:2584  RTX 3050      groupe IOMMU 5   {R}{YELLOW}pas encore sur vfio{R}", 0.4)
line(f"  {DIM}17:00.1  10de:2291  audio HDMI    groupe IOMMU 5   seule dans son groupe{R}", 1.2)
says(f"Isolation propre, pas besoin de bricoler. {BOLD}Trois changements dans le dépôt :{R}")
cont(f"{GREEN}vfio-pci.ids{R} sur l'hôte, {GREEN}gpu = true{R} sur arcade2, deux {GREEN}<hostdev>{R} dans son XML.", 1.3)
line(f"  {DIM}commit sur master · CI {R}{GREEN}vert{R}{DIM} · comin applique la génération sur gaming-01{R}", 0.6)
line(f"  {DIM}drain + redémarrage de gaming-01   {R}{RED}refusé par le classificateur de permissions{R}", 1.4)
says("Le redémarrage n'était pas nécessaire : la VM a pris la carte à son lancement.")
line(f"  {DIM}arcade2 › nvidia-smi   {R}{GREEN}NVIDIA GeForce RTX 3050 · 6144 MiB{R}", 1.3)

# --- 2. the wrong leg ----------------------------------------------------
prompt("il faudrait peut être leur enlever leur ip dans 198.51.100/24m")
says(f"Avant d'y toucher : {BOLD}c'est sur ce réseau-là que vivent les clients Remote Play.{R}")
cont("Steam découvre l'hôte par diffusion sur le réseau local. Ma recommandation :", 0.8)
cont("garder les deux pattes.", 1.0)
waiting()

prompt("Le problème c'est que arcade1 et arcade2 résolvent avec l'ip du vlan10 mais les",
       "clients sont sur vlan50, alors ils envoient leur requêtes sur Vian 10 mais c'est",
       "vlan50 qui leur répond")
says(f"Bien vu. {BOLD}Du routage asymétrique{R}, classique d'un hôte à deux pattes :")
cont(f"la requête arrive par le routeur sur {GREEN}192.0.2.141{R}, la réponse part directement", 0.8)
cont("sur le réseau maison. Le pare-feu ne voit jamais le retour, TCP décroche.", 1.0)
cont(f"{BOLD}A.{R} routage par politique dans les VM : on répond par où on a reçu.", 0.6)
cont(f"{BOLD}B.{R} faire résoudre les clients de la maison vers 198.51.100.141.", 0.6)
waiting()

prompt("ok fais A puis on verra ensuite")
calling("Edit", 2)
spinner("Règles par adresse source", "3m 50s", "4.4k")
line(f"  {DIM}arcade1 › ip rule   from 192.0.2.141 lookup 10 · from 198.51.100.141 lookup 50{R}", 0.4)
line(f"  {DIM}arcade2 › ip rule   from 192.0.2.142 lookup 10 · from 198.51.100.142 lookup 50{R}", 1.2)
says("Déployé par comin, sans redémarrer les VM. Reste le vrai test, depuis un client")
cont(f"{BOLD}de la maison{R} : je n'en ai pas, et tester depuis l'hôte mentirait.", 1.6)

# --- 3. the yellow switch ------------------------------------------------
prompt("i tried stopping arcade 2 but the button stays yellow Even though is not responding",
       "to ping ")
calling("Bash", 6)
spinner("Console de la VM", "1m 58s", "3.2k")
line(f"  {DIM}arcade2 › console   {R}{RED}nvidia-modeset: Error while waiting for GPU progress{R}{DIM}  ×∞{R}", 0.6)
line(f"  {DIM}virsh destroy arcade2   ok{R}", 0.4)
line(f"  {DIM}gaming-01 › config PCI 17:00.0   {R}{RED}ff ff ff ff ff ff ff ff   (D3cold){R}", 1.4)
says(f"L'invité a figé sur l'arrêt du pilote. Après l'arrêt forcé, {BOLD}la carte n'est plus{R}")
cont(f"{BOLD}là pour l'hôte{R}, et arcade2 refuse de démarrer.", 0.8)
says("Je suis bloqué par le classificateur sur le retrait/rescan PCI. À toi de choisir :")
cont(f"{BOLD}A.{R} le rescan à la main, sans toucher à arcade1 ;", 0.6)
cont(f"{BOLD}B.{R} redémarrer gaming-01 — garanti, mais arcade1 tourne en ce moment.", 0.6)
waiting()

prompt("both arcades are turned off reboot serveur if necessary")
calling("Bash", 4)
spinner("Redémarrage de gaming-01", "1m 22s", "1.9k")
line(f"  {DIM}17:00.0 › 10de:2584   {R}{GREEN}de retour · vfio dès le démarrage{R}", 0.4)
line(f"  {DIM}arcade2 › démarrer, arrêter par l'agent   {R}{GREEN}10 s{R}{DIM} · deuxième cycle   {R}{GREEN}10 s{R}", 1.2)
says("Pas reproductible : traité comme un accident, noté avec les pistes si ça revient.", 1.4)

# --- 4. paused, not down ------------------------------------------------
prompt("arcade1 is not reachable again. can you do something to fix it for good?")
line(f"  {DIM}virsh domstate --reason arcade1   {R}{YELLOW}paused (ioerror){R}", 0.4)
line(f"  {DIM}gaming-01 › dmesg   {R}{RED}ata5.00: failed to IDENTIFY · capacité 0 · disque désactivé{R}", 1.4)
says(f"arcade1 n'est pas en panne réseau : {BOLD}libvirt l'a mise en pause.{R} Le SSD de ses")
cont("jeux a disparu du bus sous les écritures de Steam. Vue de dehors : une panne réseau.", 1.2)
calling("Bash", 7)
line(f"  {DIM}qemu-img create -f qcow2 arcade1-games.qcow2 200G   sur le NVMe de gaming-01{R}", 0.4)
line(f"  {DIM}même étiquette ext4 · config de l'invité inchangée · /games   {R}{GREEN}196 G libres{R}", 1.2)
says(f"{BOLD}La bibliothèque Steam qui était sur ce SSD est perdue{R} : les jeux se")
cont("retéléchargent. Et arcade2 tourne encore sur le SSD jumeau, même modèle,", 0.8)
cont("même âge : c'est le prochain candidat.", 1.6)

# --- the lesson ---------------------------------------------------------
line()
says(f"Deux « ne répond pas », et aucun n'était le réseau. {BOLD}Avant de le soupçonner, demander{R}")
cont(f"{BOLD}à l'hyperviseur dans quel état il croit que la machine est.{R}", 1.2)
line()
T.separator("la suite (Plasma 6, Remote Play, une seule patte), dans une autre session", 1.6)

T.save()
