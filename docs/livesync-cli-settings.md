# LiveSync CLI settings (not in this repo)

If you sync your vault to the server with the Self-hosted LiveSync **headless CLI**, it keeps its settings in `<db-dir>/.livesync/settings.json`. That file holds your CouchDB URL, username, password and E2EE passphrase, so it's gitignored. Create your own as described here.

> Your **setup URI** is just as sensitive as the settings file: it contains the same credentials. Don't paste it into issues, chats or commits.

## Recommended: import from a working device

1. In Obsidian, on a device that already syncs, use LiveSync's option to copy the current settings as a setup URI.
2. On the server:
   ```bash
   mkdir -p ~/livesync-db ~/vault
   livesync-cli ~/livesync-db setup "obsidian://setuplivesync?settings=..."
   chmod 600 ~/livesync-db/.livesync/settings.json
   ```
3. Pull into an **empty** vault folder: `livesync-cli ~/livesync-db --vault ~/vault sync`

## Manual alternative

Generate defaults with `livesync-cli init-settings ~/livesync-db/.livesync/settings.json`, then set at least these:

```json
{
  "couchDB_URI": "https://couchdb.example.com",
  "couchDB_USER": "<user>",
  "couchDB_PASSWORD": "<password>",
  "couchDB_DBNAME": "<one database per vault>",
  "isConfigured": true,
  "encrypt": true,
  "passphrase": "<your E2EE passphrase, if your vault uses one>"
}
```

## Errors you may hit

| Message | Meaning | Fix |
|---|---|---|
| `Configuration Mismatch Detected` (e.g. Data Compression) | The CLI's settings differ from those stored on the remote | Change the **CLI's** value to match the "On Remote" column (e.g. `enableCompression`). Never push the CLI's settings to the remote. |
| `Remote database is locked` | A device rebuilt the database, and new clients must be accepted | Once all other devices are synced, run `livesync-cli ~/livesync-db unlock-remote` (or unlock from the Obsidian plugin), then `sync` again |
| `Device name missing` | Plugin/settings sync is disabled | Harmless on a headless box |
| Build fails with `styleText` | Node.js is too old | Use Node 22 LTS |

## Notes

- Use **one CouchDB database per vault**. Never point two vaults at the same database.
- Build the CLI from the release tag that matches your plugin version.
- Back up the database (CouchDB `_replicate` into a new database) before the first run.
- Don't run another sync tool (Syncthing, iCloud and so on) on the same vault folder.
