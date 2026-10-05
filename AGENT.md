# AGENT.md

## Purpose

This file provides durable context for AI agents and human collaborators working on MNIP Test Automation. Read this file, the root README, and the relevant document under `docs/` before changing code or architecture.

## Project identity

- **Repository:** https://github.com/mbuer/mnip-test-automation
- **Primary purpose:** Automate device onboarding, provisioning, validation, and long-duration testing.
- **Initial device family:** Riedel MN-IP, beginning with a FusioN ST 2110 gateway.
- **Initial switch platform:** NVIDIA/Mellanox SN2410 running Onyx.
- **Development platform:** Linux Utility VM with Docker.
- **Current interface:** CLI and container output.

This is not intended to remain a factory-reset-only utility. Factory reset is the first proven action in a larger onboarding workflow.

## User priorities

1. Documentation must be exceptionally clear and useful to support engineers.
2. The README must balance readability with enough technical detail to explain value, findings, technology, status, and outlook.
3. Deep details belong in focused files under `docs/`, linked from the README.
4. This file must preserve important findings, decisions, limitations, pitfalls, and next steps for future agents.
5. Never add secrets or sensitive environment data to the repository.
6. Clearly distinguish validated behavior from planned behavior.
7. Prefer small, working increments over speculative framework code.

## Intended end state

```text
Connect device
  -> discover and identify
  -> reset to a known state
  -> wait for recovery
  -> configure
  -> provision four receiver SDP definitions from ST 2110 senders
  -> validate stream reception and expected video output
  -> monitor for hours or days
  -> create logs and a pass/fail result
```

Future phases may add more Riedel devices and other switch manufacturers, including Netgear and Luminex.

## Validated on October 4, 2026

### End-to-end proof of concept

1. A Docker image was built on the Linux Utility VM.
2. The container connected to Onyx through SSH.
3. The application queried LLDP for Ethernet 1/25.
4. The application extracted the advertised MN-IP management IPv4 address.
5. The application sent the MN-IP factory-reset REST request.
6. The device returned HTTP 200 with `system rebooting` and rebooted.
7. The same image was exported, loaded into Onyx Docker, and executed successfully on the SN2410.
8. The Onyx-hosted container exited with status 0 after completing the action.

### Onyx SSH behavior

- The configured Onyx account is a CLI-only account.
- Executing a remote UNIX command such as `ssh user@switch "show ..."` is rejected with `UNIX shell commands cannot be executed using this account.`
- The advertised SSH authentication methods included `publickey` and `keyboard-interactive`.
- Paramiko `exec_command()` is not the correct interaction model for the Onyx CLI account used in the PoC.
- A working approach is `SSHClient.connect()` followed by `invoke_shell()`, then transmitting CLI commands through the interactive channel.
- `terminal length 0` was rejected by this Onyx version. Use a supported value, such as `terminal length 999`, or implement prompt/paging handling.
- Fixed sleeps worked for the PoC but are not robust. Replace them with prompt-aware reading and explicit timeouts.

### LLDP behavior

Validated command:

```text
show lldp interfaces ethernet 1/25 remote
```

Useful returned fields included:

- Local interface
- Remote chassis ID
- Remote port ID
- Remote system name
- Remote system description
- Remote management IPv4 address

The PoC parsed the IPv4 row with a regular expression. Production code should parse defensively, validate the address, preserve the raw output for diagnostics where appropriate, and reject ambiguous or missing results.

### MN-IP factory-reset behavior

Validated request:

```http
PUT /emsfp/node/v1/self/system
Content-Type: application/json
```

```json
{
  "config_reset": "system"
}
```

Observed successful response:

```json
{
  "code": 200,
  "info": "system rebooting",
  "debug": null
}
```

Treat factory reset as destructive. Future code must provide clear port/workflow configuration, duplicate-trigger protection, useful logs, and safe failure behavior.

### Docker portability

- A standard Python 3.11 slim image ran on the Utility VM.
- The image was exported with `docker save` and loaded through the Onyx Docker CLI.
- The same application image ran on the SN2410 without code changes.
- Onyx injected platform environment variables into the container, including system type, Onyx version, and VRF context.
- A completed one-shot container remains registered with status `Exited (0)` and its name cannot be reused until the stopped container is removed or a different name is selected.
- Onyx did not automatically expose the application's stdout in the workflow used during the PoC. Observability must be designed intentionally.

## Architecture decisions

### Static port mapping plus dynamic LLDP

The physical switchport determines the lane or intended workflow. LLDP supplies the current device metadata and management address.

For the PoC:

```text
Ethernet 1/25 -> factory-reset workflow
```

Do not make a device IP a permanent port property. The port selects the workflow; LLDP discovers the currently attached device.

### Separation of responsibilities

- **Switch adapter:** Obtain interface state and LLDP data from a specific switch platform.
- **Discovery service:** Convert switch data into a normalized discovery record.
- **Device adapter:** Perform supported operations against a device family.
- **Workflow engine:** Coordinate reset, waits, provisioning, verification, and failure handling.
- **Reporting:** Preserve operator-readable and machine-readable results.

Do not place MN-IP REST logic inside the Onyx adapter. Do not place Onyx CLI parsing inside MN-IP device logic.

### Trigger model

A direct Onyx link-up event hook has not been validated. The recommended next implementation is a continuously running poller:

```text
No eligible device
  -> interface/LLDP polling
  -> eligible neighbor appears
  -> execute once
  -> mark lane busy/processed
  -> wait for removal
  -> re-arm
```

Interface-up may occur before LLDP data is available. If interface state is used for fast detection, LLDP must still be retried until ready or timed out.

## Security rules

- Never commit switch passwords, device passwords, API tokens, private keys, or personal credentials.
- Do not commit real local configuration containing secrets.
- Keep `.env`, local overrides, generated archives, logs, and key material ignored.
- Example addresses must be identified as lab examples and must not imply production defaults.
- Avoid disabling SSH host-key verification in production. `AutoAddPolicy` was acceptable only for the PoC.
- Plan for least-privilege accounts and an explicit secret-injection mechanism.
- Before every commit, inspect `git diff --cached` and run a secret scan if available.

## Repository guidance

The existing `v0.1/` directory preserves the first working PoC. Do not expand version-number directories indefinitely. When active development resumes, migrate code into a conventional source layout and use Git tags/releases for versions.

Recommended target layout:

```text
src/mnip_test_automation/
  switches/
  devices/
  discovery/
  workflows/
  reporting/
tests/
docker/
docs/
```

Do not delete the PoC until equivalent behavior is covered by tests and documented migration history.

## Current limitations

- One-shot action rather than a persistent watcher
- One Onyx command and one configured switchport
- Regex-based LLDP extraction
- Fixed timing sleeps
- Limited error handling and no recovery state machine
- No post-reset reachability or readiness validation
- No provisioning, SDP import, media checks, or report generation
- No structured log retention
- No automated tests
- Development credentials were supplied by local configuration in the PoC

## Recommended next steps

1. Preserve and tag the working PoC.
2. Add a safe configuration model with secrets outside the repository.
3. Implement prompt-aware Onyx command execution.
4. Normalize LLDP into a typed discovery record.
5. Add continuous polling, de-bouncing, one-shot protection, removal detection, and re-arming.
6. Add post-reset recovery checks and clear exit/result states.
7. Add unit tests for LLDP parsing and workflow transitions.
8. Add structured application logging.
9. Implement configuration and four-receiver SDP provisioning.
10. Define ST 2110 and video-output validation methods.
11. Add long-duration monitoring and reports.
12. Add switch and device adapters only after stable interfaces are defined by real use cases.

## Definition of done for future changes

A change is not complete until:

- Code behavior is tested or a manual validation procedure is documented.
- User-facing and agent-facing documentation is updated.
- Validated facts and future plans are clearly distinguished.
- No secrets or generated binary artifacts are staged.
- The same deployment assumptions are checked for Linux Docker and Onyx Docker when relevant.
- Failure paths produce actionable information for support engineers.
