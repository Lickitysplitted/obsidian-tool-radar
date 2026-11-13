# Playbook: Code you've been handed

The target is concrete code — files the user pasted or pointed you at, a snippet, a diff, a single
script. Reading and statically analyzing it is always fine. **Running** it is active: only do that
for the user's own code, in the sandbox, treating it as hostile. Most of the value here is static.

## Read for intent, not just correctness

You're not code-reviewing for bugs — you're asking **what does this actually do, and does it match
what it claims to do.**

- **Entry points and control flow.** What runs on load/import/first call? Trace from the entry point
  outward rather than reading top to bottom.
- **Network & I/O.** Every outbound connection, hardcoded host/URL/IP, DNS lookup, file read/write
  outside the obvious, env-var and credential access, and clipboard/keyboard/screen access. Build a
  picture of what leaves the machine and what it touches on the machine.
- **Execution primitives.** `eval`, `exec`, dynamic import, deserialization of untrusted data, shell
  invocation, and any construction of code/commands from input. These are where "a helper script"
  becomes "arbitrary code execution."
- **Obfuscation & indirection.** Base64/hex blobs, string-built identifiers, packed/minified
  sections, unnecessary indirection. Decode what you reasonably can. Code that works to be
  unreadable is telling you something.
- **Dependencies pulled in.** What does it import, and would importing it run install hooks or fetch
  remote code? A short script that pulls a sketchy dependency is as risky as a long one.

## Diffs get special attention

If the target is a diff or a patch (including a fork's delta from upstream), the **added/changed
lines are the whole story.** What functionality was introduced, does it match the stated purpose of
the change, and does anything in the delta touch network, auth, secrets, or execution? Added
functionality in otherwise-trusted code is a prime hiding spot.

## Confirm behavior safely when it's the user's to run

For the user's own code where static reading leaves real questions, confirm dynamically **in the
sandbox**: run it instrumented (watch its network connections, filesystem access, and spawned
processes) rather than guessing. Observed behavior beats inferred behavior. Keep it isolated so that
if it *is* hostile, it can't reach anything.

## Mapping to risk areas

Mostly Code & supply chain and Network & data behavior; Authentication & access if it handles
credentials/secrets. Provenance and Track record often don't apply to a bare snippet — mark them
N/A rather than padding the table.
