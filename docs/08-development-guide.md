# Development Guide

## Principles

- Keep switch discovery separate from device actions.
- Make validated behavior reproducible before generalizing it.
- Prefer explicit state transitions and bounded retries.
- Add tests for parsing, eligibility, and destructive-action guards.
- Update documentation with every behavioral or architectural change.

## Local workflow

1. Create a branch.
2. Keep secrets in ignored local configuration or runtime environment variables.
3. Run unit tests and linting.
4. Build the Docker image.
5. Test on the Utility VM.
6. Test on Onyx when the change affects switch deployment.
7. Review staged content and commit.

## Repository hygiene

Generated image archives must not be committed. Recommended ignores include:

```gitignore
*.tar
*.tar.gz
*.tbz
.env
config.local.yaml
__pycache__/
*.pyc
*.log
```

Before committing:

```bash
git status
git diff --cached
```

If a secret or large generated file was committed, remove it from history before publishing. Deleting it in a later commit does not remove the earlier object.

## Testing priorities

- LLDP output with a valid neighbor
- No neighbor
- Incomplete or paged output
- Multiple management addresses
- Command or authentication failure
- Device API timeout and non-200 response
- Repeated observations of the same device
- Removal and re-arming
- Restart during each workflow state

## Versioning

Preserve `v0.1/` as the historical PoC for now. Future releases should use Git tags instead of new version-number directories.
