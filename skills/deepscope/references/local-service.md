# Playbook: Running local / self-hosted service or API

The target is a service the **user is running** — a container, a self-hosted app, an API on
`host:port`, something behind their reverse proxy. Because it's theirs, **active probing is in
bounds**: hit endpoints, test auth, inspect what it exposes. Do it from the sandbox against the
service, don't run destructive operations against data the user cares about, and if the instance
holds real data, say so and prefer a throwaway instance for anything intrusive.

Confirm it's the user's before probing. If there's any doubt the host belongs to them, treat it as a
third party and stay passive (see `website.md`).

## Map what's exposed

- **Surface.** What ports/endpoints are open and what's listening. For an HTTP API, enumerate the
  documented endpoints and look for undocumented ones (common admin/debug/actuator/metrics paths,
  API versions, swagger/openapi specs the service may expose). The gap between documented and actual
  surface is where the risk lives.
- **Binding & reachability.** Is it bound to localhost or `0.0.0.0`? Is it reachable from the LAN or
  (worse) the internet when it shouldn't be? A service the user thinks is private but answers on the
  LAN is a top finding.
- **Information leakage.** Verbose errors, stack traces, version banners, directory listings, exposed
  config or `.env`, debug endpoints. What does the service tell an unauthenticated stranger about
  itself?

## Vet authentication and integrity — the core of this playbook

The theme is **"is its 'auth' actually auth?"**

- **Default and weak credentials.** Does it ship with defaults? Are they changed? Can you reach
  anything meaningful unauthenticated?
- **Auth mechanism.** How does it authenticate — session cookies, tokens, API keys, basic auth, none?
  Is auth enforced on every sensitive endpoint or just the login page (auth that protects the UI but
  not the API behind it is a classic self-hosted flaw)? Test whether an unauthenticated or
  low-privilege request can reach privileged endpoints directly.
- **Transport & integrity.** TLS or plaintext? If tokens/keys are used, are they transmitted and
  stored sanely? Can requests be tampered with — does the service validate input and authorization,
  or trust whatever the client sends (IDOR-style: can you read/modify another user's object by
  changing an ID)?
- **Secrets at rest.** Where does it keep credentials/keys/tokens — config files, environment,
  database — and how protected are they? World-readable secrets on the host count.

## What it talks to

- **Egress.** Watch the service's outbound connections while it runs. Does it phone home, check for
  updates, send telemetry, or reach hosts the docs never mention? This is the self-hosted equivalent
  of "what leaves my network," and it's often the thing that actually matters to the user.
- **Data handling.** What it stores, where, and whether anything sensitive goes out.

## Mapping to risk areas

Authentication & access is usually the headline here (defaults, enforcement, integrity, secrets),
with Network & data behavior (egress/telemetry) close behind. Provenance/Track record come from the
underlying project — pull those from the repo/image playbooks if the user wants the full picture.
Every active test belongs in the report's "Scope performed" line so it's clear what was probed.
