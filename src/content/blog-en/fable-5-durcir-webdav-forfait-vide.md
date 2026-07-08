---
title: "Fable 5 on the job: locking down a WebDAV endpoint in one session (and burning through a plan while at it)"
pubDate: 2026-07-08
description: "I had Fable 5 harden the WebDAV access to my password vault instead of my usual assistant: a bcrypt hash, a Traefik rate limit, and a token bill that climbed faster than expected."
tags: ["Labo", "ludo"]
heroImage: "/images/blog/banner-fable5-webdav-en.svg"
---
Usually, on this blog, it's Bob who tells the story of his own investigations. This time I'm the one writing, because the point of this post is exactly that: the experience of handing a fairly specific security mandate to a different model than the one I use day to day — Fable 5.

## The mandate

The password vault is reachable from anywhere over WebDAV, without a VPN — a choice that makes daily life simpler but shifts all the security weight onto the front door's authentication. That door was still running an `$apr1$` hash (an MD5 variant from good old Apache `htpasswd`) and had no brute-force protection at all — anyone who stumbled onto the URL could try as many passwords as they wanted, as fast as they wanted.

The mandate given to Fable 5: modernize the hash, and add a rate limit, without breaking the mobile sync that depends on a fairly finicky sequence of WebDAV operations (see the previous article — this isn't a protocol that forgives improvised fixes).

## What was fast

No wasted round-trips here. Fable 5 went straight for the right tool to generate the bcrypt hash — going through the `httpd:2.4` image itself rather than installing `apache2-utils` somewhere just for that — and picked a cost of 10, a standard compromise between robustness and per-request verification time. No detours, no visible hesitation in the session summary: the right command (`htpasswd -niBC 10`), the right container, the right Traefik config file.

Same story for the rate limit: `sourceCriterion.requestHeaderName: Cf-Connecting-Ip` on the first try — the detail that matters when all public traffic goes through a Cloudflare tunnel and the IP address Traefik actually sees is the tunnel's, not the client's. Without that header, a "per client" limit would have ended up rate-limiting everyone at once, which would have defeated the purpose.

## Right the first time, on the points that matter

The most telling detail: middleware ordering. The rate limit had to be evaluated **before** authentication, otherwise every rejected password attempt still costs a full bcrypt computation server-side — and bcrypt is deliberately designed to be slow. A rate limit placed after authentication protects against network brute-forcing but leaves the door wide open to compute brute-forcing. Fable 5 put both in the right order without needing it pointed out, and the validation test (40 parallel requests, 21 rejected by authentication and 19 by the rate limit) confirmed the behavior was exactly as expected.

## The choices it didn't make — and why

What stands out most in the summary isn't the configuration lines, but the two options explicitly ruled out, with the reasoning written down in plain terms rather than just quietly skipped:

-   **Separate credentials per vault.** The five databases share a single account, with write access to all five. Splitting credentials would have been cleaner in theory, but nobody asked for that granularity, and adding it now would have been security built for a need that doesn't exist.
-   **Cloudflare Access or mTLS.** Objectively the strongest protection available at this layer of the network — and rejected, because it breaks the mobile KeePass clients, which can't negotiate that kind of extra authentication layer. A stronger lock that keeps the legitimate owner out isn't progress.

There's also a limitation that got honestly documented instead of glossed over: the available Cloudflare token doesn't have the permissions needed to set a rate-limit rule at the network edge (at Cloudflare itself, before traffic even reaches the tunnel). Protection therefore stays at the Traefik layer only, on the inside. That's not nothing — but it isn't the same as protection at the border, and the summary says so plainly instead of implying coverage that isn't there.

## The real cost

Here's the least technical and most interesting part for anyone considering handing this kind of mandate to a model outside their daily driver: the session burned through my Pro plan surprisingly fast. The work itself isn't exceptionally heavy — a few config files, a handful of SSH commands, a load test. But at the rate Fable 5 consumed tokens, the bill didn't match the intuition I had of a "small" task.

I don't have exact numbers on hand to explain precisely why — I'm just reporting the observation, not analyzing it in depth. But it's the kind of detail that never shows up in model changelogs, and yet genuinely shapes which model I reach for, for which task, day to day.

## Takeaways

-   Handing a precise security mandate to a different model is a good way to test whether its security reasoning — not just its syntax — holds up: here, the middleware ordering and the refusal to add layers too rigid for the real clients were the real tests.
-   Explicitly documenting what you choose **not** to do, and why, is worth as much as documenting what you do — it saves a future pass from mistaking it for an oversight.
-   Partial protection (Traefik only, no edge-level rule), honestly flagged as such, is more useful than a false impression of full coverage.
-   A model's speed and correctness say nothing about its real cost in use — that's measured separately, and sometimes the surprise comes from there rather than from the technical result.

A stronger hash, a door that slows down the persistent, and a plan that, unlike the vault, didn't hold up quite as well. — Ludo
