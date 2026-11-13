# Obsidian tool radar: research watcher + Claude Code (headless)
FROM node:22-bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 ca-certificates tini gosu \
 && rm -rf /var/lib/apt/lists/*

# Pin a Claude Code version for reproducible builds: --build-arg CLAUDE_CODE_VERSION=x.y.z
ARG CLAUDE_CODE_VERSION=latest
RUN npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
 && npm cache clean --force \
 && claude --version

COPY vault_research_watcher.py /app/vault_research_watcher.py
COPY skills/deepscope /opt/deepscope
COPY docker/entrypoint.sh /usr/local/bin/entrypoint
RUN chmod 755 /usr/local/bin/entrypoint && chmod -R a+rX /app /opt/deepscope

# Updates come from rebuilding the image, not from inside the container.
ENV DISABLE_AUTOUPDATER=1 \
    HOME=/data \
    STATE_DIR=/data/state \
    VAULT_PATH=/vault \
    DEEPSCOPE_DIR=/opt/deepscope \
    PUID=1000 \
    PGID=1000

VOLUME ["/data"]
ENTRYPOINT ["tini", "--", "entrypoint"]
CMD ["python3", "-u", "/app/vault_research_watcher.py"]
