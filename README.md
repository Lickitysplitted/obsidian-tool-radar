# Obsidian tool radar: research queue → evaluation notes

```
Obsidian (any device) ──sync──▶ server: ~/vault/Research Queue.md
                                         │  new line = a tool's name and/or link
                                         │  watcher polls every 10s, waits 20s of quiet
                                         ▼
          1. claude -p  (WebSearch + WebFetch only)
               + deepscope skill (passive-only)    ← ~/.claude/skills/deepscope (bundled)
          2. claude -p  (no tools) → Fit section
               + your Lab Profile note             ← ~/vault/Lab Profile.md
                                         │  output sanitized before it's written
                                         │
                                         ▼
          ~/vault/Research/<Canonical Name>.md  ──sync──▶ back to Obsidian
          inbox line → [[Research/<Name>|<Name>]] ✅ · <your link>
```

## What you type in `Research Queue.md`

```
- Immich
- https://github.com/immich-app/immich
- [Immich](https://immich.app)
- https://github.com/some/repo, saw this on HN
```

A link always wins: it tells Claude exactly which project you mean, and any text beside it is treated as a comment. A bare name is resolved to the most likely project. If it's ambiguous, the note says which project was chosen and lists the other candidates.

Line states: plain = queued · ⏳ = researching · ✅ = done (linked) · ⚠️ = failed 3× (delete the ⚠️ to retry)

**Duplicates aren't researched twice.** A name, the repo link, the website link, or a deeper GitHub URL (`/tree/main/...`) for a tool you already have all link to the existing note. To force fresh research, delete the note. Research never overwrites an existing note: if a new link turns out to be a tool you already have, you get a second note (`Name (2).md`).

## What each note contains

**Frontmatter** (queryable with Dataview / Bases): `name, url, repo, website, type, category, license, open_source, self_hostable, docker_images, has_api, latest_release, last_activity, fit, trust, alternatives, added_as, researched, tags`

**Sections:**
1. Summary
2. At a glance (table)
3. What it does (purpose / function / architecture)
4. Requirements (hardware, OS, **ARM64 support**, dependencies, ports)
5. Self-hosting & deployment (with a table of existing Docker images)
6. API & integrations (API types, SSO/OIDC/LDAP, plugins, data portability)
7. Pros
8. Cons
9. Alternatives & competitors (comparison table, with open-source options called out)
10. Potential tech debt (lock-in, relicensing risk, bus factor, upgrade pain, exit cost)
11. Security & trust (deepscope: **Trust:** Deploy / Deploy with hardening / Isolate / Avoid, plus risk table, findings, mitigations and verification checklist)
12. Fit for my lab (**Fit:** Adopt / Trial / Watch / Skip, judged against `Lab Profile.md` in a separate run with no tools)
13. Open questions
14. Sources

## Install: pick one

| | Docker | Native (systemd) |
|---|---|---|
| What you need | Docker + Compose | Python 3, Claude Code, systemd |
| Vault sync | Bring your own, or the bundled LiveSync CLI container | Bring your own (Syncthing, LiveSync CLI) |
| Guide | **[docs/docker.md](docs/docker.md)** | The checklist below |

Docker quick start:
```bash
cp .env.example .env && cp vault-research.env.example vault-research.env   # edit both
docker compose up -d --build                    # or: docker compose --profile livesync up -d --build
```

## Setup checklist (native)

- [ ] **1. Get the vault onto the server.** Syncthing is easiest: add `.*.tmp` to the vault's `.stignore`. For Self-hosted LiveSync, use its headless CLI; see [docs/livesync-cli-settings.md](docs/livesync-cli-settings.md).
- [ ] **2. Install Claude Code on the server:** `curl -fsSL https://claude.ai/install.sh | bash`, then `claude --version`
- [ ] **3. Auth for unattended runs.** Each user needs their own Claude subscription token or API key, and research runs count against that account.
      ```bash
      cp vault-research.env.example ~/.config/vault-research.env
      chmod 600 ~/.config/vault-research.env   # then set CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY
      ```
- [ ] **4. Install the bundled deepscope skill:** `mkdir -p ~/.claude/skills && cp -r skills/deepscope ~/.claude/skills/`. The script reads these files and puts them in the prompt; Claude itself gets no file access. If the folder is missing, a built-in passive security checklist is used instead.
- [ ] **5. Create your Lab Profile:** copy `templates/Lab Profile.example.md` to your vault root as `Lab Profile.md` and replace the placeholders.
- [ ] **6. Install the script:** `mkdir -p ~/bin && cp vault_research_watcher.py ~/bin/`
- [ ] **7. Create `Research Queue.md`** in the vault root and add one tool.
- [ ] **8. Test one pass** (wait 20s after adding the line):
      ```bash
      set -a; . ~/.config/vault-research.env; set +a
      VAULT_PATH=~/vault python3 ~/bin/vault_research_watcher.py --once
      ```
      The first two log lines confirm whether deepscope and the lab profile were loaded.
- [ ] **9. Run it as a service:**
      ```bash
      mkdir -p ~/.config/systemd/user && cp systemd/vault-research.service ~/.config/systemd/user/
      systemctl --user daemon-reload && systemctl --user enable --now vault-research
      sudo loginctl enable-linger $USER
      journalctl --user -u vault-research -f
      ```

## Files you create (kept out of git)

These hold credentials or personal data, so `.gitignore` excludes them. Create your own from the template or doc listed.

| File | Contains | Create it from |
|---|---|---|
| `~/.config/vault-research.env` (Docker: `./vault-research.env`) | Claude OAuth token or API key | `vault-research.env.example` |
| `.env` (Docker only) | Vault path, user IDs, versions | `.env.example` |
| `<db-dir>/.livesync/settings.json` | CouchDB URL, user, password, E2EE passphrase | `docs/livesync-cli-settings.md` (only if you use LiveSync) |
| `Lab Profile.md` (vault root) | Your environment, for the fit verdict | `templates/Lab Profile.example.md` |
| `Research Queue.md`, `Research/` | Your queue and research notes | Created in your vault; nothing to copy |
| `~/.local/state/vault-research/` | Research history and dedupe index | Created automatically on first run |

## Tuning (env vars in the unit or `vault-research.env`)

| Variable | Default | What it does |
|---|---|---|
| `VAULT_PATH` | `~/vault` | Vault root on the server |
| `INBOX_NOTE` | `Research Queue.md` | Inbox note |
| `RESEARCH_DIR` | `Research` | Folder for evaluation notes |
| `LAB_PROFILE_NOTE` | `Lab Profile.md` | Note used for the fit verdict |
| `DEEPSCOPE_DIR` | `~/.claude/skills/deepscope` | Where the skill files are read from |
| `DEEPSCOPE` | `on` | `off` = use the shorter built-in security checklist |
| `CLAUDE_MODEL` | Claude Code default | `sonnet` is cheaper; `opus` goes deeper |
| `MAX_TURNS` | `80` | Agent turn cap per item (hitting it counts as a failure) |
| `RESEARCH_TIMEOUT` | `2400` | Seconds per item |
| `SETTLE_SECONDS` / `POLL_SECONDS` | `20` / `10` | Quiet time before pickup / check interval |
| `MAX_ATTEMPTS` | `3` | Retries (5 min × attempt backoff) before ⚠️ |

To preview the exact prompt for an input: `python3 vault_research_watcher.py --print-prompt https://github.com/owner/repo`

## Notes

- This is a deep research run, so expect several minutes and dozens of web fetches per item. Items run one at a time, and anything added mid-run is picked up next.
- Deepscope runs **passive-only** here. Nothing is cloned, installed or probed. For an active scope of something you already host, run deepscope interactively.
- Claude gets only WebSearch and WebFetch: no shell, no file access, no MCP servers. The script writes all files itself.
- Your Lab Profile never goes to the run that browses the web, only to a second run with no tools. A malicious page therefore can't trick Claude into fetching a URL that carries your lab details.
- Before anything is written to the vault, model output is defused: `dataview`/`dataviewjs` and other plugin code blocks become plain `text`, Dataview inline queries and Templater `<% %>` tags are broken up, raw HTML is shown as text, and image embeds (other than `![[note]]`) become plain links. The Fit section, the only part written by the run that saw your Lab Profile, has every URL removed. Links elsewhere in a note come from the web research run, which never saw your lab details.
- Self-check: `python3 test_vault_research_watcher.py`
- Your original line text is kept in the note's `added_as` field. The inbox line keeps your link.
- State (dedupe aliases, retries) lives in `~/.local/state/vault-research/state.json`.
