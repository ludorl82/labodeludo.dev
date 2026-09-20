#!/usr/bin/env python3
# Lance le recorder asciinema depuis un pseudo-terminal de taille FIXE, attaché
# à la session tmux `cast` : la barre tmux est dans l'image, et la géométrie
# ne dépend d'aucun client. Usage : python3 scripts/cast-rec-attach.py 96 26 prise.cast
# (la session `cast` existe déjà, window-size manual, 96x25 pour laisser la barre).
import os, pty, sys, fcntl, termios, struct, signal
cols, rows, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
pid, fd = pty.fork()
if pid == 0:
    os.environ.pop("TMUX", None)
    os.environ["TERM"] = "xterm-256color"
    os.execvp(os.path.expanduser("~/.local/bin/asciinema"), ["asciinema", "rec", "--overwrite", "--idle-time-limit", "2",
        "-t", "Un pod stateless change de nœud", "-c", "tmux -L console attach -t cast", out])
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
os.kill(pid, signal.SIGWINCH)
while True:
    try:
        if not os.read(fd, 65536): break
    except OSError: break
os.waitpid(pid, 0)
