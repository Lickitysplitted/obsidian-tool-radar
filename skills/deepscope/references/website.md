# Playbook: Website / hosted platform / SaaS

The target is a domain you'd sign up for, point a self-hosted client at, or send data to. You do
**not** control it, so this is **passive research only** — reputation, provenance, and behavior you
can observe without attacking. No fuzzing, no auth-bypass attempts, no scanning the host. Reading
what the site serves to a normal visitor (its pages, its public JS, its headers, its privacy policy)
is fine; probing for weaknesses is not.

## Domain & provenance

- **Registration age and history.** WHOIS / RDAP for creation date and registrant (as far as privacy
  protection allows). A brand-new domain behind a product claiming years of maturity is a tell. Check
  historical ownership and screenshots where available (e.g. web archives) — did this domain used to
  be something else entirely?
- **DNS and hosting.** Where is it hosted, what's in the DNS records, does mail auth (SPF/DMARC)
  exist. Look at neighboring domains on the same registrant/IP/analytics ID — the "one hop out" move.
- **Certificate.** Issuer, validity, and certificate-transparency history (what other subdomains and
  names have certs — often reveals staging, internal, or related infrastructure the site doesn't link).

## Reputation & track record

- **Reputation services.** Check domain/URL reputation (safe-browsing style blocklists, known-malware
  or phishing associations). Treat a clean result as "no known bad," not "good."
- **Independent signal.** Reviews, HN/Reddit/forum threads, security researcher write-ups, breach
  databases. Has this product or company been breached, and how did they handle disclosure?
- **Company behind it.** Is there a real, identifiable entity? Jurisdiction matters for privacy/data
  law. "No identifiable owner" is a finding.

## What the site actually does

- **Observable behavior.** What does the page load from? Third-party scripts, trackers, analytics,
  ad networks, and any calls to unexpected hosts. Read the public client-side JS for what it sends
  and where.
- **Headers & hygiene.** Security headers (CSP, HSTS, etc.) and TLS configuration as served — a proxy
  for how much the operator cares. These you can read passively from the response.

## Privacy posture

- **The policy vs. the behavior.** Read the privacy policy and terms, then check them against what the
  site is observably doing. A policy claiming "we don't track you" on a page full of ad trackers is a
  high-value finding. Note data collection, third-party sharing, retention, and jurisdiction.
- **Account/data model.** If the user would send data here (a sync service, a cloud component of a
  self-hosted app), what exactly leaves their control, is it encrypted in transit and at rest per the
  docs, and can they self-host that component instead?

## Mapping to risk areas

Provenance (registration/ownership), Track record (reputation/breaches), Network & data behavior
(third-party calls/trackers), Privacy (policy vs. behavior). Auth and code areas usually read
**Unknown** for a black-box hosted service — say so; don't invent a rating.
