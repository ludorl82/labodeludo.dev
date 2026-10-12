#!/usr/bin/env python3
"""Build the asciicast for « Mes VM changent de maison sans s'éteindre ».

Condensed from two real sessions:

- 2026-10-07 (EDT, the small hours): the morning after a bob reboot froze the
  console, Ludo asks whether the console VM could live on the NAS and be
  highly available between bob and stella. The agent turns the NAS down (it
  reboots by itself after a firmware update; a stuck NFS mount freezes the
  whole host) and proposes copying the disk instead. Ludo does not want an
  automatic failover, only moves he triggers from Home Assistant.
- 2026-10-08 (EDT, afternoon and evening): the module, the script, the
  dashboard buttons, and the first real moves, with the agent's misses left
  in: a `sed` missing from the script's declared tools, a shellcheck note
  that broke the host build while CI stayed green, win11 refused twice, then
  the console moving its own session. The k3s cordon/drain switches come last.
- 2026-10-12: the margin rule refusing a move, for real.

Prompts are verbatim from the transcripts (typos kept), except host names.
Names: bob, stella, win11 and the arcades are public; the console VM is
`console-vm` and the two CPU k3s workers are `k3s-a` (bob) and `k3s-b`
(stella), as the public gate requires. Addresses are documentation ranges.
Tool output is rewritten short; the vm-move lines keep their real wording.

Run from the repo root:  python3 scripts/mkcast-deplacer-les-vm.py
"""

import random

import claude_tui as T
from claude_tui import BOLD, DIM, GREEN, R, RED, YELLOW, calling, cont, line, says, spinner, waiting


def prompt(*parts, speed=1.0):
    """T.prompt, with long dictated requests typed faster (speed < 1)."""
    uniform = random.uniform
    random.uniform = lambda a, b: uniform(a, b) * speed
    try:
        T.prompt(*parts)
    finally:
        random.uniform = uniform


def vm(text, colour=DIM, d=0.35):
    line(f"  {colour}{text}{R}", d)


T.setup(
    out="public/casts/deplacer-les-vm.cast",
    title="Mes VM changent de maison (reconstitution)",
    session="vm-move",
    windows=["backlog", "vm-move"],
    current="vm-move",
    start="07-Oct-26 01:32:04",
    cwd="~/git/labo",
    model="Opus 5.5 · Claude Max",
    seed=8,
)

T.disclaimer("Demandes et messages réels (7, 8 et 12 oct. 2026), minutage compressé,",
             "sorties réécrites, noms sanitisés.")
T.banner()


# --- 1. the NAS idea, turned down ---------------------------------------
prompt("Si on migrating console-vm sur le stockage du qnap, est-ce qu'on pourrait le rendre",
       "hautement disponible entre Stella et Bob?", speed=0.5)
calling("Bash", 3)
spinner("Lecture de l'historique du NAS", "41s", "2.1k")
says(f"{BOLD}Je le déconseille pour la console.{R} Deux choses vues ici même :")
cont("le QNAP redémarre tout seul après une mise à jour de son firmware, et un montage", 0.6)
cont(f"NFS qui ne répond plus met les processus en {RED}état D{R} : c'est l'hôte au complet qui", 0.6)
cont("fige, pas juste la VM. La console dépendrait d'une machine de plus.", 1.0)
says(f"Sans stockage partagé, libvirt sait {GREEN}copier le disque{R} pendant que la VM roule")
cont("(--copy-storage-all), puis la mémoire. Plus lent, mais chaque hôte garde ses disques.", 1.2)

# --- 2. moves, not failover ---------------------------------------------
prompt("Pour console-vm et win11 je n'ai pas besoin de relève automatique mais j'aimerais pouvoir",
       "déplacer ces vms entre les 4 x11sra qui auront toutes w2135 48gb avec homme assistant.",
       "Comment pourrait on y parvenir?", speed=0.35)
calling("Read", 4)
spinner("Plan", "1m 52s", "3.4k")
says("Trois morceaux :")
cont(f"1. un module NixOS commun, {BOLD}labo.vmHost{R} : même réseau, même dossier d'images,", 0.5)
cont("   clés SSH entre les hôtes, ports de migration ouverts entre eux seulement ;", 0.5)
cont(f"2. {BOLD}vm-move <vm> <hôte>{R} : virsh migrate --live --persistent --undefinesource", 0.5)
cont("   --copy-storage-all. La définition part avec la VM : jamais deux copies ;", 0.5)
cont("3. un bouton par VM dans Home Assistant, par une clé à commande forcée.", 1.0)
says(f"{YELLOW}win11 a une carte passée{R} : elle ne pourra pas bouger tant qu'elle l'a.", 1.2)
waiting()

# --- 3. the next day: build it ------------------------------------------
T.separator("8 octobre")
T.set_clock("08-Oct-26 13:22:26")
prompt("Fusionné mais je veux pouvoir migrer les vms entre stella et Bob manuellement avec",
       "home assistant", speed=0.5)
calling("Edit", 5)
spinner("vm-move, clés de migration", "6m 10s", "8.2k")
says("Le script tourne dans une unité systemd : si la session qui l'a lancé tombe,")
cont("le déplacement continue. Ça compte quand c'est la console qu'on déplace.", 1.0)
prompt("Ajoute les bouton au tableau de bord")
calling("Bash", 4)
spinner("Tableau Homelab", "3m 40s", "4.0k")
vm("Déplacer entre bob et stella")
vm("  Hôte de console-vm   bob      [ Déplacer console-vm ]")
vm("  Hôte de win11        bob      [ Déplacer win11 ]")
vm("  Hôte de k3s-a        bob      [ Déplacer k3s-a ]", d=1.0)
says("Premier essai, k3s-a vers stella :")
vm(f"{RED}vm-move: line 119: sed: command not found{R}", d=1.0)
says(f"{BOLD}Mon test passait parce qu'il voyait tous les outils de la console.{R} Le script")
cont("n'a droit qu'à ceux que le module déclare. sed ajouté, et le test roule désormais", 0.6)
cont("avec la seule liste déclarée.", 1.2)

prompt("Qu'est-ce qui prend du temps?")
calling("Bash", 2)
vm(f"comin: {RED}build failed{R} · SC2015 (info): Note that A && B || C is not if-then-else.", d=1.0)
says(f"{BOLD}La CI était verte, mais elle évalue la config sans la compiler.{R} Le build de bob")
cont("roule shellcheck, et une simple note l'a fait échouer. Je l'aurais vu tout de suite en", 0.6)
cont("lisant le journal de comin au lieu d'attendre en boucle.", 1.2)
calling("Edit", 1)
vm("vm-move: creating k3s-a.qcow2 on stella (60 GiB, qcow2)")
vm("vm-move: copying UEFI vars")
vm("vm-move: migrating k3s-a to stella (192.0.2.40), live, disks included")
vm(f"{GREEN}vm-move: OK: k3s-a runs on stella{R}   {DIM}3 min 16 s · noeud k3s resté Ready{R}", d=1.4)

# --- 4. win11, refused twice --------------------------------------------
prompt("Je viens de cliquer pour déplacer win11")
calling("Bash", 3)
vm(f"{RED}vm-move: FAILED: win11 has a <hostdev> (passed-through device); it cannot move live{R}", d=0.8)
says("Refus voulu : elle avait encore sa carte. Retirée, elle n'en a plus besoin. Deuxième essai :")
vm(f"{RED}vm-move: FAILED: virsh migrate failed; win11 should still be running here{R}")
vm("libvirt : migration refusée, fonction CPU invtsc (host-passthrough, migratable='off')", d=1.0)
says(f"Son CPU exposait un compteur que libvirt ne transporte pas. {GREEN}migratable='on'{R},")
cont("un redémarrage à froid, puis :", 0.6)
vm(f"{GREEN}vm-move: OK: win11 runs on bob{R}   {DIM}6 min · disque de 128 GiB, toujours allumée{R}", d=1.4)

# --- 5. the console moves its own session -------------------------------
prompt("Je peux le lancer moi même?")
says("Oui :")
vm("ssh bob sudo vm-move console-vm stella", colour=BOLD)
says("À ce moment-là, cette session se figera quelques secondes.", 1.0)
waiting()
prompt("U there?")
T.spinner("Migration de console-vm", "7m 02s", "0.4k", d=2.2)
vm("vm-move: creating console-vm.qcow2 on stella (100 GiB, qcow2)")
vm("vm-move: migrating console-vm to stella (192.0.2.40), live, disks included")
vm(f"{GREEN}vm-move: OK: console-vm runs on stella{R}", d=0.8)
says(f"{BOLD}Le test est réussi : cette session a survécu à son propre déplacement.{R}")
cont("7 minutes en direct, 100 Gio de disque. Je t'écris depuis stella en ce moment.", 1.6)

# --- 6. the k3s switches -------------------------------------------------
prompt("Peux tu me ajouter un toggle pour chaque nœud k3s pour que je cordon et drain ou",
       "uncordon les nœuds moi-même", speed=0.5)
calling("Edit", 3)
spinner("power-ctl k3s-on / k3s-off", "5m 30s", "5.1k")
says("Un interrupteur par noeud : fermé, cordon puis drain en arrière-plan ; ouvert, uncordon.")
cont(f"Il {YELLOW}refuse{R} de fermer un noeud s'il en resterait moins de trois autres Ready.", 1.4)
waiting()

# --- 7. four days later: the margin rule, for real ----------------------
T.separator("12 octobre")
T.set_clock("12-Oct-26 07:29:49")
prompt("J'ai tenté de déplacer k3s-b sur Bob mais ça a échoué je crois")
calling("Bash", 2)
vm(f"{RED}vm-move: FAILED: bob has 2 GiB available; k3s-b needs 4 GiB + 4 GiB headroom{R}", d=1.0)
says(f"Échec voulu : bob a repris ses trois VM, il lui reste 2 Gio. Le script {BOLD}refuse avant{R}")
cont("de créer quoi que ce soit chez l'autre. k3s-b peut redémarrer avec stella : c'est un", 0.6)
cont("noeud k3s, ses pods iront ailleurs le temps du redémarrage.", 1.8)

line()
says(f"{BOLD}Une VM définie à un seul endroit ne peut pas démarrer deux fois.{R} Le reste, c'est")
cont("de la copie : le disque, puis la mémoire, pendant qu'elle roule.", 2.4)
line()

T.save()
