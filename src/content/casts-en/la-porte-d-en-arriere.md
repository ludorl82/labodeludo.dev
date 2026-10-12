---
title: "The back door"
pubDate: 2026-09-23
description: "Two days on hosts with two legs that answer through the wrong one: the failure reproduced from cloud-01, three source-routing rules tried by hand and then declared in a NixOS module, an SSH freeze the agent had wrongly set aside, and the container whose reply took the one path the rules could not see."
cast: "/casts/la-porte-d-en-arriere.cast"
poster: "npt:1:32"
caption: "Two days' thread: the failure understood, a first try that sets nothing, rules 100 and 101 on a witness and then on nine hosts, rule 102 for the Mac's freeze, and rule 103 for the container. The agent stops three times for a merge or a choice, and owns up to a case set aside wrongly. The recording is in French."
type: "reconstitution"
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, edited afterwards from the real transcript of the September 23 and 24, 2026 sessions. Ludo's prompts are quoted word for word, typos included, except the host name, replaced by the article's; tool output is rewritten and shortened, the timing is compressed and names are sanitized."
article: ["corollaire-la-porte-d-en-arriere"]
---

The problem already had a name in the lab: hosts plugged into two VLANs that
answer from the right address but through the wrong leg, and a pfSense that drops
what it sees coming back through the wrong door. The session picks the thread up
again after a detour through the Mac. From the Mac, a 200 MB transfer goes
through; from cloud-01, outside both networks, ping works and TCP fails. The
first manual try sets no rule at all, because the variable never split under zsh.
Redone through standard input, it gives the clean signature: failure, banner,
failure.

Rules 100 and 101 go first on a witness, vm-02, then on all nine hosts through a
NixOS module, `labo.dualHomed`, after a manual try on each of the two other
wiring styles. Eighteen legs out of eighteen answer from cloud-01.

The next day, an SSH session from the Mac freezes. It is the case the agent had
set aside the day before on the strength of a ten-second transfer, too short to
ever meet a thirty-second idle timeout. Rule 102 fixes it. In the evening, the
freeze is back on port 2222: the reply leaves from a Docker container, so from an
address rule 102 never looks at. A connection mark and a rule 103 close that last
door.

The mechanism, piece by piece, is in
[Corollary: Linux Answers Politely, but Through the Back Door](/en/blog/corollaire-la-porte-d-en-arriere/);
the failure itself is filmed for real in
[the real take](/en/casts/la-mauvaise-patte-prise-reelle/).
