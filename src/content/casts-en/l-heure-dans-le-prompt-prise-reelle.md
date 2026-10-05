---
title: "The clock in the prompt, for real"
pubDate: 2026-10-05
description: "The same prompt sent three times in a row to Bob's model, a Qwen3.8-27B served by Ollama, with the time to the second placed in three spots: at the top of the system prompt, at its end, then inside the question. llama-server's log says how many tokens it had to read again each time: 3,483, then 1,024, then 29."
cast: "/casts/l-heure-dans-le-prompt-real-en.cast"
poster: "npt:1:18"
caption: "Three panes: the commands on top, llama-server's log in the middle, the narration at the bottom. The time at the top of the prompt: everything is read again, 3,483 tokens, 4.9 s. At the end of the system prompt: 1,024 tokens, 2.3 s, from a checkpoint taken just before the end. Inside the question: 29 tokens, 0.37 s."
article: "un-cerveau-plus-lent-pour-bob"
session: "aucune"
frame: "none"
disclaimer: "✔ This is a real capture, made on October 4, 2026 with asciinema in a dedicated tmux session, with no editing. The mesure-prefixe.sh script, published in the site's repository, sends its requests to Bob's real model, with the production settings; the middle pane follows Ollama's log on the machine that serves it. The keystrokes were sent by a script and not typed by Ludo, the prompt is “ludo@labo”, only pauses longer than two seconds are shortened, and the container ID in the tmux bar is replaced by a name of the same length."
---

The mechanism from [Ludo's article](/en/blog/un-cerveau-plus-lent-pour-bob/) and
[Bob's corollary](/en/blog/trois-cartes-deux-cerveaux-une-horloge/), replayed for real
on the model that serves both the house's voice and this site's chat.

On top, `scripts/voice/mesure-prefixe.sh` asks the same question three times in a row,
"Quel jour on est ?" ("What day is it?"), with the same prompt: Bob's persona and the
voice rules, about 3,500 tokens. Only the time changes, to the second. The time shown
is how long Ollama took to read the prompt.

In the middle, the same script follows llama-server's log, which says how many tokens
it had to read again. The number comes from there because Ollama's API does not give
it: it always returns the full size of the prompt.

-   **The time at the top of the system prompt**: the first line changes, so
    everything after it is read again, 3,483 tokens on every question.
-   **The time at the end of the system prompt**: the model is hybrid and can only
    resume from a checkpoint taken before the difference. The closest one was taken
    a little more than 1,000 tokens before the end: 1,024 tokens to read again.
-   **The time inside the question**: the first one pays for the change of prompt,
    then only the question itself is left to read, 29 tokens.

What was touched after the take, and nothing else: pauses longer than two seconds
and the container ID in the tmux bar.
