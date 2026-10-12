---
title: "The night pipeline that lied"
pubDate: 2026-09-16
description: "A day on the night pipeline, and three green statuses that said “all good” for reasons unrelated to the work: a stale copy that succeeded, an API refusal read as agreement, a shell that exited zero without running anything."
cast: "/casts/la-chaine-de-nuit-qui-mentait.cast"
poster: "npt:1:43"
caption: "One day's thread: the guard that had never run, the graphics card nobody had counted, the delta, the API refusal reported as “already matched”, then one line of .bashrc that kept every job from starting. The agent stops twice and corrects itself once. The recording is in French."
type: "reconstitution"
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, edited afterwards from the real transcript of the September 16, 2026 session. Ludo's prompts are quoted word for word, typos included; tool output is rewritten and shortened, the timing is compressed and names are sanitized."
article: ["ce-que-coute-une-nuit-de-pipeline", "la-job-etait-verte"]
---

It starts with a suggested question under the site's chat that leads to a
refusal. The guard meant to prevent that was already in the repository, but it
had never run: the scheduler executed a hand-made copy of the script, three days
old. The job was green. It was running the previous Sunday's code.

The rest of the day repeats the pattern. A review session is refused by the
API's content filter in twelve seconds, the program exits zero, and the driver
reports "already matched the repos"; the brand-new delta even records that run
as its starting point. In the evening, every job launched by the scheduler dies
with code 70, because Debian's bash reads `~/.bashrc` under ssh and that file
runs `exec zsh` on its third line.

Two of the agent's stops are kept: a refused write waiting for Ludo's go-ahead,
and a "measure first" proposal that Ludo turns down, since the timings were
already in the transcripts. One correction too: the optimization announced as
the big lever was not one, and the numbers showed it.

The per-session cost tables are in
[What a Night of Pipeline Costs](/en/blog/ce-que-coute-une-nuit-de-pipeline/);
the plumbing is detailed in
[My Job Was Green](/en/blog/la-job-etait-verte/).
