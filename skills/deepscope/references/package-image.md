# Playbook: Package or container image

The target is something the user would pull and run — a Docker/OCI image, or a package from a
registry (npm, PyPI, crates, etc.). Inspecting metadata and contents is passive and always fine.
**Pulling and running** it is active — do it in the sandbox, treating the image/package as hostile,
and only when the user is going to run it. Much can be learned without executing anything.

## Provenance of the artifact itself

- **Who published it, and does it match the source.** Tie the image/package back to a source repo and
  a maintainer, then apply `repo.md` to that source. A package with no discoverable source, or whose
  source doesn't match its contents, is a serious finding.
- **Name confusion.** Typosquatting and dependency-confusion: is this the real `immich/immich` or a
  look-alike? Check the exact namespace/owner, not just the name.
- **Signing & pinning.** Is the artifact signed (cosign/sigstore, package signing)? Is the user
  pulling a mutable tag (`:latest`) or a pinned digest? Recommend pinning the digest you actually
  reviewed, because a tag can change under them after you've vetted it.

## Look inside without running

- **Image layers & history.** Inspect the layers and build history: base image and its provenance,
  what each layer adds, the entrypoint/cmd, exposed ports, declared env, and the user it runs as
  (running as root is a finding). Pull the filesystem and look for unexpected binaries, cron/startup
  hooks, embedded credentials, or added packages the description doesn't mention.
- **Package contents & install hooks.** For a language package, read the actual published contents
  (not just the repo — published artifacts sometimes differ from the repo). Check install/build
  hooks (`postinstall`, `setup.py`, build scripts) that run at install time, and any bundled/minified
  code or binaries.
- **Declared dependencies.** Resolve them and check against advisory databases; note anything
  abandoned, obscure, or suspicious.

## Confirm behavior in the sandbox

For the user's intended deployment, run it isolated and watch first-contact behavior: network egress
on startup, what it writes to disk, processes it spawns, and whether it reaches hosts the docs don't
mention. This catches what static inspection misses.

## Mapping to risk areas

Provenance (publisher/signing/source match), Code & supply chain (layers/hooks/deps/blobs), Network &
data behavior (startup egress), Authentication & access (runs-as-root, baked-in secrets). Flag any
unreviewable blob as Unknown rather than assuming it's benign.
