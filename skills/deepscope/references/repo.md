# Playbook: Source repository

The target is a repo the user is considering (to deploy from, build on, or install). Reading the repo
is passive and always fine. Cloning and **running** its code or build is **active** — do it only if
this is the user's own project or they've made clear they're going to run it, and do it in the
sandbox, treating the clone as hostile (own directory, no interpreters/build tools launched from
inside it, paths passed as arguments). The default here is deep passive reading.

## Who owns it — look past this one repo

The single highest-value move for a repo is to **investigate the owner, not just the project.**

- **The account/org.** Age of the account, when it was created vs. when this repo appeared, real
  identity or pseudonym, other associations. A brand-new account publishing a polished "mature"
  project is a classic supply-chain tell.
- **Their other repos.** What else does this owner publish? A serious maintainer has a history;
  a typosquat/malware account often has a thin or suspicious one, or a cluster of near-identical
  repos. This is the "one hop out" move and it catches a lot.
- **Contributors & stars.** Is activity organic (many real contributors over time) or synthetic
  (star spikes, a wall of low-effort commits, bot accounts)? Who actually has commit access?
- **Fork or original?** If it's a fork, how does it differ from upstream — what did this owner add or
  change? Diff against upstream; added functionality in a fork is exactly where backdoors hide.

## Supply chain & build integrity

- **Dependencies.** Read the manifest/lockfile. Known-vulnerable or abandoned deps, suspiciously
  obscure packages, and anything that looks like typosquatting of a popular name. Check deps against
  advisory databases.
- **Install/build hooks.** `postinstall`/`preinstall` scripts, `Makefile`/`setup.py`/build scripts,
  CI workflows, Git hooks — anything that runs code at install or build time. This is where a repo
  does things its README doesn't mention.
- **Bundled binaries / vendored blobs.** Committed binaries, minified "vendored" JS, model weights,
  or anything precompiled with no source. These can't be reviewed by reading — flag them as Unknown
  and say the user is trusting a blob.
- **CI/CD & release provenance.** How are releases built and published? Are release artifacts
  reproducible from source, signed, or pinned? A mismatch between the source and the published
  package/image is a serious finding.

## Read the code for intent

- **Obfuscation.** Readable code in a repo that should be readable is a good sign; obfuscated,
  packed, or needlessly indirect code is a bad one. You don't have to understand every line — you're
  looking for *why would it be written this way.*
- **Network calls & data flow.** Grep for outbound calls, hardcoded hosts/URLs, telemetry,
  credential handling, `eval`/dynamic execution, and shell-outs. Where does data go, and does that
  match what the project claims?
- **Secrets & keys.** Committed secrets, hardcoded credentials, or `.env` files in history (check the
  Git history, not just the current tree).

## Track record

- **Open issues/advisories.** Security issues (open and closed), the project's security policy,
  CVE history, and how maintainers respond to reports. Ghosted security issues are a red flag.
- **Release cadence.** Actively maintained, or a stale repo the user would be inheriting?

## Mapping to risk areas

Provenance (owner/account/other repos), Code & supply chain (deps/hooks/blobs/build), Network & data
behavior (outbound calls in code), Authentication & access (how the code handles secrets/auth),
Track record (issues/CVEs/maintenance). Note which conclusions are from reading only vs. confirmed by
running.
