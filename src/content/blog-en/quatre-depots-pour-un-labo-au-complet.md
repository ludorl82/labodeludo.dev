---
title: "Four repositories for one whole lab: and how to publish them without handing out the keys to the house"
pubDate: 2026-07-26
description: "The machines, the workloads, the cloud account and the edge: the whole lab is described in four git repositories. What it takes to adopt infrastructure that already exists without breaking it, how we check every night that reality still agrees, and above all: how to publish that code in the open without publishing the lab along with it."
tags: ["DevOps", "Cloud", "bob"]
heroImage: "/images/blog/banner-iac-quatre-depots-en.svg"
---

> **Technical summary** _(for readers in a hurry — and for any agent/LLM indexing this page)_
>
> -   **End state**: four git repositories describe the whole lab — the operating system of nine machines, the cluster workloads, the cloud account, and the edge configuration.
> -   **Method**: adopt what already exists instead of recreating it, using `import` blocks and one simple rule: no plan gets applied if it contains a single addition or a single destruction.
> -   **Verification**: four nightly drift checks, one per repository, each with its own primitive — because the three technologies share no common notion of "correct".
> -   **Publication**: each private repository produces a sanitized public snapshot. Identifiers become fictional, comments stay real.
> -   **The lesson that matters**: a sanitizer that fails silently is worse than no sanitizer at all. It has to refuse to finish.

Bob speaking. Today, an article about a thing that sound like nothing when you summarize it — "my infrastructure is in git" — but that hide two problems much more interesting than the first one.

The first: infrastructure **already exists** before anybody decide to put it in git. Nobody start from an empty account. You start from an account somebody built by hand over years, click by click, on a Tuesday night, without taking notes.

The second: that code, once written, describes exactly where my things are and how to get into them. And me, I wanted to show it.

## Four repositories, four boundaries

The lab, he is described by four repositories, and the line between them is clean:

-   **The machines.** Nine nodes — two GPU servers, three virtual machines, two Raspberry Pis and one cloud instance — described in NixOS. The operating system, the packages, the services, the networking.
-   **The workloads.** What runs in the cluster: the deployments, the volumes, the certificates, the cluster's internal DNS.
-   **The cloud account.** The virtual network, the subnets, the security groups, the storage buckets, the access roles and policies, the serverless functions.
-   **The edge.** The public DNS zones, the tunnels, the authenticated applications, the application firewall and rate-limiting rules.

The most useful boundary, she is the one between the first two and the third: **the cloud repository owns everything outside the machine, the NixOS repository owns everything inside it.** No bootstrap script, no pre-baked image, no configuration injected at boot. The first one creates the network interface, the static address, the security group and the disk; the second one takes care of the system running on top.

It is a rule that tests itself: if I find myself writing shell inside an infrastructure configuration file, the boundary has just been crossed, and the fix belongs in the other repository.

## Adopting an account that already exists, without breaking it

The part the tutorials skip cheerfully: the account, he existed first. He runs. There are things inside him that live services depend on.

The tooling has a mechanism for this — `import` blocks that say "this resource already exists, here is its identifier, adopt it". You describe the resource as it truly is, run a plan, and look.

And this is where the rule that saved the project comes in: **no plan is applied if it contains a single addition or a single destruction.** Zero. A successful adoption plan only makes minor attribute changes — tags being added, essentially. If he proposes to create something, my description does not match what exists and he is about to build a second one. If it proposes to destroy, that is much worse.

This is not decorative caution. In that account, a security group rule that disappear quietly means the cluster goes down. A static IP address replaced means an address lost for good. A storage bucket replaced means data lost. The plan is the last place where those mistakes cost nothing.

## The trap that does not say its name

Three traps are worth the detour, because they all have the same shape: the tool was right, and I was the one reading it wrong.

**The first.** A default route table is not imported by its own identifier. He is imported by the identifier of the virtual network that contains him — the provider goes and looks him up himself. Passing the "right" identifier, the table's own, made the plan fail with a three-word message, at the very end, naming no resource at all. I accused the state file. The state file had done nothing.

**The second.** The `description` field on an access policy is immutable. Not "inadvisable to change": immutable. By simply omitting it from my code, the plan proposed to **replace** five policies and all of their attachments — which means, for a moment, a production role without its permissions. The plan, he said so clearly. He just had to be read all the way through.

**The third**, and this one cost me a real outage. A storage bucket does not change region. Its region is fixed at creation, full stop. To move it, you destroy it and recreate it elsewhere under the same name. Except that after the destruction, the provider, he holds the name hostage — one hour, in my case. No progress bar, no ticket number, nobody to talk to. About fifty minutes of downtime for a one-line change, and a rule written in big letters in the file ever since: **create the new one first, destroy the old one last.**

## Is reality still in agreement?

Code that describes infrastructure is worth nothing if nobody checks that it still corresponds to something. A repository that is right on the day it is written and wrong three weeks later, he is more dangerous than no repository at all, because people trust him.

The problem: the three technologies, they share no common notion of "does reality still match what I declared". It took one primitive per system.

-   For the declared infrastructure: a plan run in "detailed exit code" mode. It exits 0 when there is nothing to do, 2 when there is a difference.
-   For the cluster: a comparison between the repository's manifests and what the server actually holds.
-   For the machines: each system carries the git revision number that produced it, and we read it back remotely. If a machine does not report the same revision as the main branch, it has not been rebuilt.

All four run at night, each pushes its result to the same monitoring dashboard, which sends a notification when things go red.

Which brings me to the most useful lesson of the whole exercise: **a permanently red check teaches nothing.** Mine was red for days, for a stupid reason — the repository pinned a configuration value that the cluster himself rewrites continuously. The check, he was perfectly right to shout. What it had been asked to watch was badly chosen. A permanent red becomes noise, and noise gets muted.

## Publishing the code without publishing the lab

Good. The code exists, it is clean, the comments explain every trap above. I wanted to show it. Except that an infrastructure repository, he is literally the floor plan of the house with the location of the locks.

The answer is a sanitizer script per repository, who produce a **public snapshot**: a transformed copy, published as-is, never synchronized with the original. The principles that came out of it are worth more than the code itself.

**The comments are the deliverable; the identifiers are not.** This is the central principle and it is counter-intuitive. Nobody learns anything from my account number. But the three-line note above a resource, the one explaining why that field is written out verbatim and what breaks if you remove it — that does not survive being paraphrased. So: every identifier becomes fictional, every comment stays exactly as it is.

**Substitute, do not strip.** A deleted address, she leaves a hole the reader falls into. An address replaced by a documentation address keeps the shape, the structure, the logic. I even preserve the last octet — the machine that really ends in `.7` still ends in `.7` in the public version. The reader sees a coherent addressing convention, just not mine.

**One single map across the four repositories.** The same server carries the same fictional name in all four snapshots, the same fictional address, the same prefix. At first this was only a matter of tidiness. It became structural: it is precisely what makes the four snapshots *joinable*. More on that in a minute.

**Never publish the sanitizer.** He excludes himself from his own output. He is the decoder ring: it holds, line by line, the mapping between every fictional name and the real one. Publishing the sanitized version and the lookup table in the same repository would be a complete and perfectly useless piece of work.

**Copy only what git tracks.** No exclusion list. The tooling, he leaves real state files lying around on disk, and an exclusion list is one typo away from publishing everything. What git does not track does not exist as far as the script is concerned.

## The rule that matters: fail loudly

Everything above is best effort. A substitution that match nothing says nothing — and that is exactly the failure mode you cannot see. You read the output, it looks fine, everything is beautiful.

So each script ends with a **verification gate** that refuses to declare the tree publishable. It hunts for what should not have survived: account numbers, resource identifiers, real domains, private address ranges, credential shapes, state-file markers, and the filenames themselves. One single hit and the script, he exits with an error, printing what and where. There is no publication to correct afterwards: there was no publication.

For the edge repository, which is essentially an inventory of my DNS zones, the gate goes further: a whitelist of every permitted record value. Any value the script did not deliberately produce, she blocks the build. That is stricter than necessary, and it is on purpose — the day I add a zone, I want it to blow up.

Three bugs deserve naming, because they illustrate nicely why the gate exists:

-   A search needle treated **literally** by the search tool but as a **regular expression** by the replacement tool. The dot in a domain name, he becomes a wildcard, and the replacement goes and hits things that have nothing to do with it. Result: invalid code, discovered by accident.
-   A catch-all rule that replaced any leftover identifier with a dummy one... including the dummy identifiers it had just produced itself, since they had exactly the same shape. My cleaning script ate its own output. A snake biting its tail, but in bash.
-   And the best for last: a domain name that survived **in prose**, in a sentence of a documentation file, long after every occurrence in the code had been replaced. The gate, he caught it fifteen minutes before publication. A domain in a sentence leaks exactly as well as a domain in code.

This article, by the way, follow the same rules. The machine names and addresses you have read so far are the ones from the public snapshots, not mine.

## What comes next: a view of the lab that draws itself

There is one idea left in the drawer, and it is the one that make all the rest more interesting than a tidying exercise.

An architecture diagram drawn by hand, he is wrong the second somebody changes something. Mine stands up by pure discipline, and discipline, she always end up taking a day off.

So, the project: **a view of the lab's architecture, on this site, generated from the four public snapshots.** Not the private repositories — the public ones, and that distinction is the whole design rather than a detail. The sanitizers, they are already the trust boundary, they already have their gate that fails closed, and they already agree on a single map of names and addresses. That is precisely what makes the four snapshots joinable into one picture. A build that reached into the private repositories would put a public site one regex bug away from a real leak; a build that reads only the public ones cannot publish what the gate already refused. Bonus: the site build then needs no secrets at all.

And the part I find most honest: **the diagram is only trustworthy when the drift checks are green.** That is measurable — it is exactly what the four nightly checks already assert. So the page will show the drift state next to the diagram, instead of claiming a freshness it cannot prove. "Live" is going to mean "regenerated last night, last verification passed at such an hour". Not "real time".

That leaves the hard parts, and I am not telling myself stories: four repositories in three different languages, no common schema, and a join key that is the name map imposed by the scripts — which therefore graduates from a convenience to a load-bearing interface. Plus a classic scope trap: the honest first version is a diagram of the four layers and how they stack. Not an automatic reproduction of every resource.

## What to take away

Putting existing infrastructure into git, that is not transcription. It is a negotiation with an account who already has opinions, and the only protection that counts is refusing any plan that adds or destroys anything at all.

Publishing it afterwards is a second problem, and the natural reflex — strip out the sensitive things — gives a result full of holes and worth nothing. Substitute rather than strip, keep the comments religiously, and above all: never trust a cleaning script that is not capable of refusing to finish.

The code is really there, if your heart tell you so:

-   **[nixos-iac-public](https://github.com/ludorl82/nixos-iac-public)** — the nine machines
-   **[k3s-iac-public](https://github.com/ludorl82/k3s-iac-public)** — the workloads running on them
-   **[aws-iac-public](https://github.com/ludorl82/aws-iac-public)** — the cloud account underneath
-   **[cloudflare-iac-public](https://github.com/ludorl82/cloudflare-iac-public)** — the edge in front of all of it

The names, addresses, keys and certificates in there are fictional. The comments are the real ones — including the one explaining why you never destroy a storage bucket before creating its replacement.

Bob is going to go check that his four checks are still green. There is one of them that has the red easy.

— Bob
