# Development

## Local environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt pytest
```

## Tests

```bash
PYTHONPATH=src python -m pytest -q
```

The suite must cover:

- exact narrow reset request;
- temporary-address derivation;
- port-aware Onyx commands;
- configuration and subnet validation;
- three independent lane states;
- short and sustained link-down behavior;
- duplicate management-IP prevention.

## Build release candidate

```bash
docker build -f docker/Dockerfile -t mnip-test-automation:v1.0-rc1 .
docker save -o mnip-test-automation-v1.0-rc1.tar mnip-test-automation:v1.0-rc1
```

The optimized TAR should remain near 58 MB. A materially larger image usually means the build context included `.venv`, TAR files, or other generated artifacts.

## Repository hygiene

Generated and local files must remain ignored:

```text
.venv/
.pytest_cache/
__pycache__/
*.pyc
*.tar
config/config.yaml
.env
*.log
```

Before committing:

```bash
git status --short
git diff --check
PYTHONPATH=src python -m pytest -q
```

Review staged changes for credentials and generated binaries.

## Coding boundaries

- Keep REST behavior in `device.py`.
- Keep Onyx behavior in `switch.py`.
- Keep orchestration in `watcher.py`.
- Keep startup in `app.py`.
- Keep public examples generic and clearly labeled.
- Do not describe hardware behavior as validated until observed.

## Release flow

1. Develop on `feature/v1.0-production`.
2. Run unit tests and build `v1.0-rc1`.
3. Validate all three lanes in the lab.
4. Update `docs/validation-history.md` and release status.
5. Merge to `master`.
6. Build final image `v1.0`.
7. Tag the validated commit.
