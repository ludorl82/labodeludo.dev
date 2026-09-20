#!/usr/bin/env bash
# Tape une ligne dans un panneau tmux à cadence humaine (45–115 ms/caractère), puis Entrée.
t="$1"; shift; text="$*"
for ((i=0; i<${#text}; i++)); do
  tmux -L console send-keys -t "$t" -l -- "${text:$i:1}"
  sleep "$(awk -v r=$RANDOM 'BEGIN{printf "%.3f", 0.045 + (r%71)/1000}')"
done
tmux -L console send-keys -t "$t" Enter
