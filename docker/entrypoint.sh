#!/bin/sh
# Drop root and run as PUID:PGID so files written to the vault are owned by the host user.
set -e

if [ "$(id -u)" = "0" ]; then
  mkdir -p /data "$STATE_DIR"
  chown "$PUID:$PGID" /data "$STATE_DIR"
  if [ ! -w /vault ] || ! gosu "$PUID:$PGID" test -w /vault; then
    echo "entrypoint: /vault is not writable by $PUID:$PGID. Set PUID/PGID to the owner of your vault folder (id -u / id -g)." >&2
    exit 1
  fi
  exec gosu "$PUID:$PGID" "$@"
fi

exec "$@"
