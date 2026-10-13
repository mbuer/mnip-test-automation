# Deployment

## Primary runbook

Use [v0.6 Deployment Runbook](11-deployment-runbook.md) for the complete copy/paste procedure from Windows PowerShell through image transfer, Onyx configuration, helper execution, watcher startup, verification, reconfiguration, rollback, and cleanup.

## Required Onyx prompt

Unless a step explicitly says otherwise, run project Docker/image commands at the Onyx `(config) #` prompt. Reach it with:

```text
enable
configure terminal
```

If the prompt is `(config docker) #`, run `exit` once before entering a command beginning with `docker`.

## Deployment model

- Build on the Linux Utility VM.
- Export a standard Docker TAR.
- Transfer the TAR to Onyx image storage.
- Load the image from `(config) #`.
- Store runtime configuration in the persistent `mnip-config` Docker label.
- Use a hold-mode helper container to run `mnip-configure`.
- Remove the helper and start the watcher with the same label.

## Security

The image contains only `config/config.example.yaml`. Real credentials are entered interactively and stored in `/mnip-config/config.yaml` on the Onyx label. Never commit the runtime config or include it in the Docker image. The label contains sensitive data and must be protected and deleted deliberately when decommissioning.

## Build and export

```bash
docker build -f docker/Dockerfile -t mnip-test-automation:v0.6 .
docker save -o mnip-test-automation-v0.6.tar mnip-test-automation:v0.6
```

The archive is generated and Git-ignored. The validated optimized archive is approximately 58 MB.

## Upgrade rule

Do not delete `mnip-config` during a normal image upgrade. Stop/remove containers, replace the loaded image, then start the new watcher with the existing label.

## Validation rule

Validate one lane at a time after deployment. The FusioN lane is validated under v0.6. MuoN A10 support must not be marked validated until an actual MuoN A10 reset cycle and cleanup check complete successfully.
