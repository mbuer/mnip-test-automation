# Deployment

## Security notice

Do not place real credentials in the image or commit them to the repository. The examples below intentionally omit environment-specific usernames, passwords, and addresses.

## Utility VM deployment

Typical lifecycle:

```bash
docker build -t mnip-test-automation:VERSION .
docker run --rm -it --env-file path/to/local.env mnip-test-automation:VERSION
```

The exact build context and runtime arguments should be updated when the PoC is migrated into the target source layout.

## Export for Onyx

```bash
docker save mnip-test-automation:VERSION -o mnip-test-automation-VERSION.tar
```

The archive is a generated deployment artifact and must remain ignored by Git.

Transfer the archive using the approved management path, then load it from Onyx Docker configuration mode. Verify the exact commands against the deployed Onyx version.

## Onyx execution considerations

- Use an image version that exists in `show docker images`.
- Container names remain reserved by stopped containers until removed.
- A one-shot success may appear as `Exited (0)`.
- Define logging before unattended use; successful work may not be visible through the basic status commands.
- Validate management reachability and VRF behavior from inside the container.
- Apply resource limits where appropriate.

## Rollback

Retain the last known-good image version and configuration. Do not overwrite a known-good tag with an unvalidated build. If a deployment fails, preserve diagnostics before removing the container.
