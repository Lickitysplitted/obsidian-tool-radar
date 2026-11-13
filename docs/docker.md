# Docker option

Runs the research watcher in a container with Claude Code and the deepscope skill built in. An optional second container runs the Self-hosted LiveSync headless CLI, so the vault stays synced with no Obsidian app on the server.

```
host: VAULT_DIR ──bind mount──▶ /vault ◀── watcher   (Python + Claude Code, runs as PUID:PGID)
                               /vault ◀── livesync  (optional profile, LiveSync CLI daemon)
      LIVESYNC_DB_DIR ───────▶ /data  (livesync: local DB + .livesync/settings.json)
      volume watcher-data ───▶ /data  (watcher: research state + Claude Code config)
```

## What you create (all gitignored)

| File | Purpose | From |
|---|---|---|
| `.env` | Paths, user IDs, versions for Compose | `.env.example` |
| `vault-research.env` | Claude auth (secret) | `vault-research.env.example` |
| `<vault>/Lab Profile.md` | Your environment, for the fit verdict | `templates/Lab Profile.example.md` |
| `<LIVESYNC_DB_DIR>/.livesync/settings.json` | CouchDB connection (secret, LiveSync profile only) | Setup URI import (below) |

In Docker, leave `VAULT_PATH`, `STATE_DIR` and `DEEPSCOPE_DIR` unset in `vault-research.env`; the image sets them.

## Setup checklist

- [ ] **1. Configure:**
  ```bash
  cp .env.example .env                              # set VAULT_DIR, PUID, PGID
  cp vault-research.env.example vault-research.env  # set CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY
  chmod 600 vault-research.env
  ```
  Set `PUID`/`PGID` to the owner of your vault folder (`id -u`, `id -g`). The watcher refuses to start if it can't write to the vault.
- [ ] **2. Create `Lab Profile.md` and `Research Queue.md`** in the vault root.
- [ ] **3a. Vault already synced on this host** (Syncthing, etc.):
  ```bash
  docker compose up -d --build
  ```
- [ ] **3b. Or sync with LiveSync in Docker:**
  ```bash
  mkdir -p livesync-db                                   # or the LIVESYNC_DB_DIR you set
  docker compose --profile livesync run --rm livesync setup "obsidian://setuplivesync?settings=..."
  docker compose --profile livesync run --rm livesync --vault /vault sync   # first pull, into an EMPTY vault folder
  docker compose --profile livesync up -d --build
  ```
  Set `LIVESYNC_TAG` in `.env` to your plugin version (e.g. `1.0.43-cli`). Read [livesync-cli-settings.md](livesync-cli-settings.md) first: back up your CouchDB database, and know how to handle the config-mismatch and remote-lock messages.
- [ ] **4. Watch it work:**
  ```bash
  docker compose logs -f watcher
  ```
  The first lines confirm that deepscope and the lab profile were loaded. Add a line to `Research Queue.md` and watch for ⏳, then ✅.

## ARM64 hosts

The upstream LiveSync CLI image is published for amd64 only. On ARM64, build it from source instead:
```bash
docker compose -f compose.yaml -f compose.livesync-build.yaml --profile livesync up -d --build
```
Set `LIVESYNC_REF` in `.env` to the matching release tag. The watcher image builds natively on both architectures.

## Updating

- **Claude Code:** auto-update is disabled in the container. Rebuild to update: `docker compose build --no-cache watcher && docker compose up -d`. Pin a version with `CLAUDE_CODE_VERSION` in `.env`.
- **LiveSync CLI:** change `LIVESYNC_TAG`, then `docker compose --profile livesync pull && docker compose --profile livesync up -d`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `entrypoint: /vault is not writable by …` | Set `PUID`/`PGID` in `.env` to the vault folder's owner |
| `claude reported: Not logged in` | `vault-research.env` is missing a token or key, or the token expired; run `claude setup-token` again |
| Lines stay plain, nothing happens | The watcher waits 20s after the last edit; check `docker compose logs watcher` |
| LiveSync `Configuration Mismatch` / `Remote database is locked` | See [livesync-cli-settings.md](livesync-cli-settings.md) |
| Reset the watcher's history (dedupe index, retries) | `docker compose down && docker volume rm <project>_watcher-data` |
