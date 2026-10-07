# Deployment

## Security notice

Do not bake credentials into the image or commit them to Git. The current PoC configuration model is temporary and must be replaced with runtime secret injection before production use.

## Build on the Utility VM

```bash
docker build -t mnip-test-automation:VERSION .
```

Use `.dockerignore` so virtual environments, TAR exports, Git metadata, caches, and backups are not copied into the build context.

Set unbuffered Python output in the image:

```dockerfile
ENV PYTHONUNBUFFERED=1
```

## Export

```bash
docker save -o mnip-test-automation-VERSION.tar mnip-test-automation:VERSION
```

The TAR is a generated deployment artifact and must remain ignored by Git.

## Transfer

Use the approved management transfer path. In the validated lab flow, the archive was copied to the Onyx image storage used by `docker load`.

Do not assume the CLI account can browse or delete files through SFTP. Do not change switch filesystem permissions for convenience.

## Load on Onyx

At the Onyx configuration prompt:

```text
docker
load mnip-test-automation-VERSION.tar
```

## Start for validation

```text
start mnip-test-automation VERSION unique-container-name now
```

`now` starts the watcher immediately but does not configure boot-time restart. Use this mode until the specific image and workflow behavior are validated.

A later persistent policy such as `now-and-init` should only be enabled after restart behavior, state recovery, and logging are defined.

## Verify status

Use the supported Onyx `show docker container <name>` command and verify `status: running` for the watcher.

Status alone does not prove a workflow succeeded. During current validation, operators also observed:

- link operational state;
- LLDP neighbor and current management address;
- brief appearance and removal of the temporary VLAN address;
- device reboot and return to factory addressing; and
- continued watcher runtime.

## Stop and remove container configuration

Enter Docker configuration mode and use the supported `no start <container-name>` flow.

## Remove loaded image

From configuration mode:

```text
docker remove image mnip-test-automation VERSION
```

## Remove stored TAR archive

```text
image delete mnip-test-automation-VERSION.tar
```

Loaded Docker images and stored archives are separate. Removing one does not remove the other.

## Runtime networking requirement

For arbitrary-subnet recovery, run the REST action from the switch-hosted container. Adding an address to the switch VLAN does not give the Utility VM an equivalent path.

## Offline operation

The switch does not need Internet access at runtime. Dependencies are installed during image build and included in the archive.

## Rollback

- Keep the last known-good image and source tag.
- Start new versions with `now` and a unique name.
- Do not overwrite known-good tags.
- Preserve diagnostics before removal.
- Verify that temporary VLAN addresses are absent after any failed test.
