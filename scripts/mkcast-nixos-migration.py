#!/usr/bin/env python3
"""Build the asciicast for the NixOS migration article.

Condensed from the real session transcript of one node's conversion
(2026-07-24). The prompts and Claude's stop messages come from that session;
timing is compressed and the long waits cut.

Hostnames are sanitized to match the article's fictional naming, not the real
inventory: the converted VM is `vm-05` (asked for as `vm-03` at first, then
kept under its own name), its Hyper-V host is `hv-01`, and the
fleet's build/deploy box is `gpu-01`. The technical narrative — Secure Boot
blocking kexec, then an initrd that won't unpack in 4 GB — is unchanged.

Palette and line grammar per net-cfgs/asciicast-style.md.

Run from the repo root:  python3 scripts/mkcast-nixos-migration.py
"""

import claude_tui as T
from claude_tui import BOLD, DIM, GREEN, R, YELLOW, cont, line, prompt, says, spinner, waiting

T.setup(
    out="public/casts/nixos-migration.cast",
    title="Une conversion de nœud vers NixOS (reconstitution)",
    session="nixos-vm-05",
    windows=["backlog", "nixos-vm-05"],
    current="nixos-vm-05",
    start="24-Jul-26 10:08:51",
    cwd="~/git/nixos-iac",
    model="Opus 5 with high effort · Claude Max",
    seed=7,
)

T.disclaimer("Demandes et messages réels, minutage compressé,",
             "noms d'hôte sanitisés.")
T.banner()

# --- 1. the ask ---------------------------------------------------------
prompt("Can you ssh into vm-05 and convert it to nixos as vm-03?")
says("I'll start by reading the relevant memory files for context.", 1.1)
spinner("Gathering", "18s", "1.2k")
says("Noting that the rename isn't free: vm-05 is a k3s node, so vm-03 means")
cont("draining it, deleting the old node object and re-joining under the new", 0.9)
cont("name — plus DNS, the DHCP reservation and the monitoring checks.", 1.2)

# --- 2. the user steers mid-flight -------------------------------------
prompt("nvm keep the name vm-05")
says("Got it — no rename. Converting in place as `vm-05`.", 1.0)

says("Important find before I wipe anything: vm-05 runs a scheduled S3 backup")
cont("(`~/scripts/homelab-backup.sh` + its key). Preserving that first.", 1.2)
line()
line(f"  {DIM}Bash  scp -p vm-05:~/scripts/homelab-backup.sh ./salvage/{R}", 0.7)
spinner("Salvaging", "12s", "0.8k")

says("Now writing the vm-05 config, then checking it evaluates.", 1.0)
line()
line(f"  {DIM}Bash  nix eval .#nixosConfigurations.vm-05.config.system.build.toplevel{R}", 0.7)
spinner("Evaluating", "41s", "2.6k")
says("Config evaluates cleanly. Committing to the repo.", 1.1)

# --- 3. point of no return ---------------------------------------------
says("Now the kexec phase — this is the point of no return for vm-05's")
cont("Debian install.", 1.2)
line()
line(f"  {DIM}Bash  nixos-anywhere --flake .#vm-05 root@vm-05{R}", 0.7)
spinner("Installing", "1m 04s", "3.4k")

# --- 4. first wall: Secure Boot ----------------------------------------
says("Kexec was rejected: Secure Boot is enabled on this VM, so the kernel")
cont("refuses to load the unsigned NixOS kernel. Checking how boxed-in we are.", 1.2)
spinner("Investigating", "27s", "1.9k")

says("Blocked on a real fork. vm-05 is a Gen-2 VM with Secure Boot On, and the")
cont("kernel is in `integrity` lockdown — that blocks both kexec paths, so the")
cont("install can't start. NixOS also can't Secure Boot without lanzaboote.", 1.3)
line()
line(f"  {YELLOW}{BOLD}I can disable Secure Boot from the hypervisor and power-cycle it.{R}", 0.9)
line(f"  {YELLOW}That reboots vm-05. Say go and I'll do it.{R}", 0.6)
waiting()

prompt("go ahead")
line()
line(f"  {DIM}Bash  ssh hv-01 powershell -c \"Set-VMFirmware vm-05 -EnableSecureBoot Off\"{R}", 0.7)
spinner("Reconfiguring", "34s", "1.1k")
says("Lockdown is now `[none]` — kexec will work. Re-running.", 1.0)
spinner("Installing", "2m 11s", "4.2k")

# --- 5. second wall: initrd won't unpack -------------------------------
says("Mid-kexec, host unreachable as expected. But it never came back.", 1.1)
says("I have hypervisor access, so let me grab the VM console screen directly.", 1.0)
line()
line(f"  {DIM}Bash  ssh hv-01 powershell -c \"Get-VMConsole vm-05 | Out-File screen.txt\"{R}", 0.7)
spinner("Capturing", "19s", "1.5k")

says("Found it — the console shows the kexec kernel booted but")
cont(f"{YELLOW}Initramfs unpacking failed: XZ-compressed data is corrupt{R}, then hung.")
cont("That's the classic symptom of too little RAM to unpack the ~430 MB", 0.9)
cont("installer initrd. vm-05 has 4 GB. Bumping it temporarily to 8 GB.", 1.2)
spinner("Retrying", "3m 48s", "5.7k")

# --- 6. it comes back ---------------------------------------------------
says("Host is answering — connection refused, not unreachable. It's booting,")
cont("sshd not up yet.", 1.1)
says(f"{GREEN}vm-05 is up on NixOS 26.11{R}, booted from disk, both NICs and the IPv6")
cont("address correct. Two things to check — DNS is failing.", 1.2)

says("Found the real issue: private names fail while public names work.")
cont("systemd-resolved is routing queries to its fallback instead of the local")
cont("resolver, because nothing marks the interface's DNS as authoritative.", 1.0)
cont("Fixing that in the config, not by hand on the box.", 1.2)
spinner("Rebuilding", "58s", "2.2k")

# --- 7. the real test ---------------------------------------------------
says("Now restoring the VM to its original 4 GB and doing a cold boot — the")
cont("real test that it comes up unattended.", 1.2)
spinner("Verifying", "1m 27s", "3.0k")

says(f"{GREEN}Everything verified.{R} vm-05 runs NixOS 26.11, converted entirely over")
cont("SSH. Disk layout, both NICs, IPv6, DNS and the cluster agent all check out")
cont("after a cold boot at the original 4 GB. Config committed and pushed.", 1.4)
line()
line(f"  {DIM}8 of 9 nodes converted.{R}", 2.6)

T.save()
