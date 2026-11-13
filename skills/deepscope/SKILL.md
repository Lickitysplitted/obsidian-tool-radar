---
name: deepscope
description: 'Security and privacy due-diligence review of software before the user trusts it — a self-hosted app, web platform or SaaS, source repo, chunk of code, package/image, or a running local API. Use whenever the user invokes /deepscope, says "deep scope" / "scope out" a target, or asks you to vet, audit, or "can I trust / is this sketchy / should I run" a tool, image, package, repo, website, or service they''re thinking of deploying or already self-hosting — even when they don''t say "security". The theme is DON''T TRUST, VERIFY: look past vendor claims, corroborate from independent sources, and actively probe targets the user owns or hosts. Produces a shareable write-up ending in a trust verdict (Deploy / Deploy with hardening / Isolate / Avoid) plus mitigations. Do NOT trigger for adjacent tasks that aren''t a trust review: debugging or configuring a tool already in use, writing a compose file or reverse proxy, code-reviewing a PR for quality, or comparing/recommending which tool to pick.'
---

# Deep Scope

A due-diligence review that answers one question honestly: **how much should the user trust this
thing, and what should they do before (or instead of) trusting it?**

The user experiments with and self-hosts a lot of software and keeps running into the problem that
modern supply chains are hard to trust. This skill is the "don't trust, verify" reflex made
systematic. The failure mode to avoid is taking the target at face value — reading its README,
summarizing its own marketing, and calling it safe. A good deep scope **corroborates every claim
from somewhere the target doesn't control**, and looks for the things a target wouldn't advertise:
who really owns it, what it talks to, what it does on first run, whether its "auth" is auth.

## The one rule that governs everything

**Passive by default. Active only on what the user owns or hosts.**

- **Passive** techniques — reading public code, WHOIS/DNS lookups, reputation services, searching for
  CVEs and incident history, inspecting published artifacts, reading a Dockerfile — are always fine,
  for any target.
- **Active** techniques — sending requests to a service, port/endpoint probing, running the target's
  code, installing a package, fuzzing auth — are **only** for targets the user owns or self-hosts.
  A public website, a third party's hosted API, or someone else's server gets **passive research
  only**. Probing infrastructure you don't control is the user's legal risk to take, not yours to
  take for them.

When a target the user *does* own needs active work, do it — don't stop to ask. Clone and run code,
install packages, probe ports, hit endpoints. Do this work in the **isolated sandbox** you're
running in (a throwaway container/VM), never against the user's production host and never from their
personal machine, so that running hostile code can't reach anything that matters. Treat every
downloaded artifact as hostile until proven otherwise: put it in its own empty directory, don't
execute interpreters or build tools from inside it, and pass paths as arguments. This is the whole
reason the sandbox exists — use it freely, but keep the blast radius inside it.

If you're ever unsure whether a target is the user's to probe, that uncertainty itself is the
answer: stay passive and say so in the report.

## Step 1 — Identify the target (and disambiguate a bare name)

The user may hand you a URL, a repo (`owner/name` or a Git URL), a path to local files, a running
service (`host:port` or a compose file), or **just a name** ("deepscope Immich", "is Audiobookshelf
safe"). A bare name is ambiguous — there is usually an official site, a source repo, a Docker image,
and possibly the user's own running instance, and they may not be the same project. **Don't guess.**
Ask a short disambiguating question before burning research on the wrong artifact:

> "Quick scope question on *Immich*: which do you want me to focus on? (a) the project/source on
> GitHub, (b) the Docker image you'd actually deploy, (c) a URL or instance you're already running,
> or (d) all of the above as one picture?"

Once you know the target type, read the matching playbook in `references/` and work through it. More
than one type can apply at once (a name expands into a site **and** a repo **and** an image); run
each relevant playbook and merge the findings.

| Target type | Playbook |
|---|---|
| Website / hosted platform / SaaS | `references/website.md` |
| Source repository (GitHub/GitLab/etc.) | `references/repo.md` |
| Code you've been handed (files, snippet, diff) | `references/code.md` |
| Running local/self-hosted service or API | `references/local-service.md` |
| Package / container image | `references/package-image.md` |

The playbooks are the substance of this skill — the checks that go past face value. Read the ones
that apply before writing anything. Don't try to recall their contents from memory; open them.

## Step 2 — Investigate with a "verify, don't trust" mindset

Across every target type, the moves that separate a real scope from a face-value summary:

- **Corroborate from outside the target's control.** The project says it's widely used and audited —
  who else says so? Independent reviews, CVE databases, the issue tracker, security advisories,
  reputation services, the maintainer's track record. One source is a lead, not a finding.
- **Look beyond what's given.** A repo owner has other repos; a domain has other domains on the same
  registrant/IP; an image has layers the description doesn't mention; an API has endpoints the docs
  don't list. The interesting findings usually live one hop out from what you were handed.
- **Watch for the tells of something to hide.** Freshly registered domain fronting an "established"
  product, a maintainer account created last month, obfuscated or minified code in a repo that
  should be readable, telemetry/callbacks to hosts the docs never mention, bundled binaries with no
  source, licenses that don't match the claims, a quiet history of security incidents.
- **For anything executable, find what it does on first contact.** Install scripts, entrypoints,
  `postinstall` hooks, first-run network calls, what it reads from the host, what it phones home.
- **Keep the evidence.** Every finding in the report should point to what you actually saw — a URL, a
  file and line, a command and its output — so the user can check your work. "Don't trust, verify"
  applies to *your* conclusions too.

Record findings as you go; don't hold them in your head until the end.

## Step 3 — Rate the risk per area

Score each area you examined, so the verdict is legible and the user can argue with specifics. Use
a consistent scale and keep the band labels short:

- **Provenance & ownership** — who's behind it, how verifiable, how long-standing
- **Code & supply chain** — code quality/readability, dependencies, build integrity, bundled binaries
- **Network & data behavior** — what it talks to, what it collects, where data goes, telemetry
- **Authentication & access** — how auth works, defaults, secrets handling, exposure (esp. for services)
- **Track record** — CVEs, incident history, responsiveness to security reports
- **Privacy** — data collection, sharing, retention, and how honest the stated policy is

Rate each **Low / Medium / High / Unknown** risk. **"Unknown" is a first-class result** — if you
couldn't verify something, say so rather than defaulting it to fine; unverifiable is itself a
signal, and it tells the user where to look next.

## Step 4 — Deliver the write-up and a verdict

The deliverable is a **shareable document** so the user can keep it and send it on. Produce it as a
Claude doc (editable, shareable) when a docs tool/connector is available in the session; load the
docs guidance first if it isn't already loaded, create the doc skeleton, then fill it. **If no docs
connector is available** (e.g. a sandboxed run), write the report as a standalone **Markdown file**
instead and hand it over — don't block on a connector that isn't there.

Follow this structure exactly, because a scope is only useful if the verdict and the evidence are
both easy to find:

```
# Deep Scope: <target>

**Verdict:** <Deploy | Deploy with hardening | Isolate | Avoid>
**Scope performed:** <what was passive vs. active; what was in/out of bounds and why>
**Date:** <date> · **Target identified as:** <the specific artifact(s): URL, repo@commit, image@digest, …>

## Summary
<3-5 sentences: what it is, the headline risks, and the one-line reason for the verdict.>

## Risk ratings
| Area | Risk | Basis |
|---|---|---|
| Provenance & ownership | <Low/Med/High/Unknown> | <short, with evidence pointer> |
| Code & supply chain | … | … |
| Network & data behavior | … | … |
| Authentication & access | … | … |
| Track record | … | … |
| Privacy | … | … |

## Findings
<The detail. Each finding: what you checked, what you found, and the evidence (URL / file:line /
command + output). Lead with the ones that drove the verdict. Call out Unknowns explicitly.>

## Mitigations
<Concrete, ordered, actionable. What to lock down, isolate, or monitor to make the verdict safer —
network egress rules, auth hardening, running it isolated/behind a reverse proxy, pinning a digest,
what to watch after deploying. Tie each mitigation to the finding it addresses.>

## Verification checklist
<A checklist the user (or a future scope) can re-run: the specific things that were verified and the
ones still open, as checkboxes. This is what "verify" leaves behind.>
```

### The verdict scale

- **Deploy** — low risk across the board; nothing found that warrants special handling.
- **Deploy with hardening** — usable, but only with specific mitigations applied first. List them.
- **Isolate** — don't trust it on the main network/with real data, but it can run walled off
  (isolated VLAN/network, no egress, dummy data, sandboxed). Say exactly how to wall it off.
- **Avoid** — the risks outweigh the benefit; recommend against deploying and say what would have to
  change to revisit.

Match the verdict to the evidence, and never upgrade it to be reassuring. A confident "Avoid" with
reasons is more useful than a hedged "probably fine." If the research genuinely couldn't reach a
verdict, say that plainly and point to what's blocking it — an honest "can't tell yet, here's why"
beats a fabricated rating.

**Always deliver all three together: the full findings, the verdict, and the mitigations.** A clear
verdict is never a reason to trim the findings down to a sentence — the user wants the verdict *and*
the evidence behind it *and* what to do about it, every time, even when the answer is a clean
"Deploy." The verdict without the findings is an opinion; the findings without the verdict are
homework. Give the complete picture.

## Scope discipline

Do the scope that was asked and stop there. Don't deploy the thing "to be helpful," don't file
issues on the user's behalf, don't contact maintainers, and don't export extra artifacts the user
didn't ask for. The output is the assessment; the user decides what to do with it.
