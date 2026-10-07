# Development Guide

## Principles

- Keep switch discovery, reachability recovery, device operations, workflow state, and reporting separate.
- Preserve validated behavior before refactoring.
- Test failure and cleanup paths, not only successful reset.
- Prefer explicit states, bounded retries, and typed records.
- Update README, AGENT, and focused docs with every behavioral change.

## Current development workflow

1. Work on the Linux Utility VM.
2. Keep credentials in ignored local configuration.
3. Activate a project virtual environment for direct Python tests.
4. Run syntax checks and tests.
5. Build a versioned Docker image.
6. Export it with `docker save`.
7. Transfer and load it on Onyx.
8. Start with mode `now` during validation.
9. Observe link, LLDP, temporary VLAN configuration, device behavior, and container status.
10. Preserve the known-good version before the next change.

## Python environment

Newer Debian/Ubuntu Python may enforce PEP 668. Use a virtual environment rather than modifying the managed system Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The virtual environment is for development only and must not be copied into the Docker build context.

## Docker build hygiene

Maintain `.dockerignore` with at least:

```text
.venv/
__pycache__/
*.pyc
*.pyo
*.tar
.git/
local backup files
```

The first watcher export reached 141 MB because the build context included local artifacts. Excluding them reduced the v0.4 TAR to 58 MB.

## Repository hygiene

Recommended Git ignores include:

```gitignore
*.tar
*.tar.gz
*.tbz
.env
config.local.yaml
.venv/
__pycache__/
*.pyc
*.log
```

Before committing:

```bash
git status --short
git diff --cached
```

Deleting a secret or generated binary in a later commit does not remove it from prior history.

## Minimum test matrix

### Parsing

- Link Up and Down output
- Valid LLDP neighbor
- No LLDP neighbor yet
- Paged/incomplete output
- Multiple and malformed management addresses
- Unexpected CLI error or prompt

### Temporary addressing

- Ordinary host address uses adjacent candidate
- `.254` uses the lower candidate
- `.0`, `.255`, invalid, multicast, loopback, and prohibited ranges are rejected
- Candidate conflict is detected
- Add succeeds, add fails, cleanup succeeds, cleanup fails

### Workflow states

- Device already reachable
- Device requires temporary reachability
- REST timeout or non-success response
- Short reboot link drop does not re-arm
- 60 seconds continuous Down does re-arm
- Link returns during removal timer
- Process/container restarts in each state

### Deployment

- Utility VM build
- Onyx load/start/remove
- Runtime without Internet access
- Correct switch/container routing behavior

## Versioning

Preserve the historical one-shot implementation and tag validated milestones. Do not create a new source directory for every prototype version. Migrate active code into `src/` and use Git tags/releases once the next refactor begins.
