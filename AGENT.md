# AGENT.md

## Purpose

This file is durable operating context for AI agents and human collaborators working on MNIP Test Automation. Read this file, the root `README.md`, and the relevant focused documents under `docs/` before changing behavior, architecture, or deployment guidance.

Keep this file factual and compact. Put explanatory narrative in the README or focused documents. Update this file whenever a validated finding changes an architectural assumption.

## Project identity

- **Repository:** `https://github.com/mbuer/mnip-test-automation`
- **Mission:** Automate device onboarding, provisioning, validation, and long-duration testing.
- **Initial device family:** Riedel MN-IP, beginning with a FusioN ST 2110 gateway.
- **Initial switch platform:** NVIDIA/Mellanox SN2410 running Onyx.
- **Development platform:** Linux Utility VM with Docker.
- **Validated runtime:** Onyx Docker on the SN2410.
- **Current user interface:** CLI/container status and observable switch/device effects.
- **Current active prototype:** persistent factory-reset watcher associated with Ethernet 1/25.

This is not a factory-reset-only project. Reset is the first proven destructive action in a larger supported onboarding workflow.

## User priorities

1. Documentation must be exceptionally clear and useful to support engineers.
2. README content must explain value, findings, technology, current status, limitations, and outlook without becoming the only source of detail.
3. Deep or vendor-specific details belong in focused files under `docs/`.
4. Clearly label validated behavior, current prototype behavior, proposed design, and future work.
5. Preserve operational findings that would otherwise be rediscovered in the lab.
6. Prefer small validated increments over speculative abstractions.
7. Never add secrets, private environment details, or generated Docker archives to Git.
8. Keep repository documentation and architecture notes synchronized with verified findings.

## Intended end state

```text
Connect device
  -> discover and identify
  -> establish reachability when required
  -> reset to a known state
  -> wait for recovery
  -> configure
  -> provision four receiver SDP definitions
  -> validate ST 2110 reception and expected video output
  -> monitor for hours or days
  -> create logs and a pass/fail result
```

Future phases may add other Riedel products and switch platforms such as Netgear and Luminex, but do not generalize interfaces before a real second implementation establishes the common behavior.

## Validated milestone: October 4, 2026

### One-shot end-to-end proof of concept

- Built a Python 3.11 slim Docker image on the Utility VM.
- Connected to Onyx through Paramiko using an interactive shell.
- Queried LLDP for Ethernet 1/25.
- Extracted the advertised MN-IP management IPv4 address.
- Sent `PUT /emsfp/node/v1/self/system` with `{"config_reset": "system"}`.
- Observed HTTP 200 with `system rebooting`; the device rebooted.
- Exported, transferred, loaded, and ran the same image on the SN2410.

## Validated milestone: October 6, 2026

### Discovery and Layer 3 reachability are independent

Lab observation:

```text
Switch VLAN 1 primary: 192.168.39.10/24
Device advertised by LLDP: 10.10.10.10
Initial reachability: failed
```

LLDP continued to return device identity and `10.10.10.10` despite the absence of Layer 3 reachability. Never treat a valid LLDP record as proof that REST communication is possible.

### Onyx additional VLAN address

Onyx accepted an additional IPv4 address on VLAN 1 without replacing the primary address:

```text
interface vlan 1
ip address 10.10.10.11/24
```

Adding the address immediately restored switch-to-device reachability. Removing it with the corresponding `no ip address` command removed reachability again.

The test was repeated with:

```text
Device: 172.20.50.100/24
Temporary switch address: 172.20.50.101/24
```

The complete factory-reset workflow succeeded from the Onyx-hosted container and cleaned up the temporary address afterward.

Addresses above are lab examples, not defaults.

### Current temporary-address policy

The prototype derives an adjacent address under an assumed `/24`:

- if the device's final octet is not `254`, use device address + 1;
- if the final octet is `254`, use device address - 1.

This is a prototype policy, not a generally safe address-allocation algorithm. LLDP does not provide the device prefix length. Future code must reject invalid addresses, check for conflicts, make the prefix policy configurable, and fail safe when the assumptions are not acceptable.

### Persistent watcher behavior

The tested watcher:

- polls the configured port on an approximately 10-second policy;
- waits for link up and then retries LLDP until neighbor information is available;
- processes the connected device once;
- marks the lane as processed after reset;
- keeps running after the action;
- does not re-arm for brief link loss during device reboot;
- re-arms only after the port remains continuously down for 60 seconds; and
- successfully processed a device on another private subnet after re-arming.

A device remained connected and stable for more than three minutes after returning to its factory address without being reset again. This validated the 60-second guard against reboot-induced reset cycles.

### Cleanup behavior

Temporary VLAN addresses were removed after successful switch-hosted runs. A prior VM-hosted REST timeout demonstrated that an unhandled exception could skip cleanup. Current and future workflow code must use `try/finally` around any temporary network configuration. Cleanup failure must be a high-severity result, not a hidden warning.

## Onyx interaction facts

### SSH model

- The tested account is an Onyx CLI account, not a UNIX shell account.
- Remote UNIX commands are rejected with `UNIX shell commands cannot be executed using this account.`
- Use `SSHClient.connect()` and `invoke_shell()`. Do not use `exec_command()` for this account.
- A fresh automated session starts at the unprivileged `>` prompt.
- Configuration requires this exact privilege progression:

```text
enable
configure terminal
interface vlan 1
...
```

- `conf t` was rejected from the initial `>` prompt because privilege had not been elevated.
- `terminal length 0` was rejected; use a supported value such as `terminal length 999` until proper pager handling is implemented.
- Onyx `ping` runs continuously and was stopped by sending Ctrl+C. `ping <address> count 2` was not valid in the tested CLI and interpreted `count` as a hostname.
- Fixed command sleeps are still present. Replace them with reads that recognize prompts, command completion, errors, and explicit timeouts.

### Correct execution location

- Switch reachability checks must be executed from the switch context.
- The Utility VM did not become able to reach an arbitrary device merely because an additional address was configured on the switch.
- The REST action must run inside the Onyx-hosted container for this recovery design. A VM-hosted `requests.put()` follows the VM's routing path and timed out in the tested arbitrary-subnet case.

### Docker behavior

- Standard `docker save` archives load through the Onyx Docker CLI.
- The tested image runs without Internet access because Python and all dependencies are included at build time.
- Starting a container requires image name, version, container name, and start mode such as `now`.
- `now` is suitable for testing; `now-and-init` is a possible later persistent boot policy but was not selected during v0.4 validation.
- A stopped container retains its name until removed with the Onyx Docker configuration command.
- Loaded Docker images and stored TAR files are separate resources.
- Remove loaded images with `docker remove image <name> <version>`.
- Remove stored deployment archives with `image delete <filename>`.
- The watcher image was reduced from a 141 MB TAR to 58 MB by adding `.dockerignore` exclusions for `.venv`, TAR files, bytecode, backups, and Git metadata.
- `PYTHONUNBUFFERED=1` is set so Python output is emitted promptly, but an operator-friendly Onyx logging path remains unresolved.

## Architecture decisions

### Static lane plus dynamic discovery

- The physical port selects the workflow.
- LLDP supplies current identity and management addressing.
- The current validated lane is Ethernet 1/25.
- Never make a previously observed device address a permanent property of the lane.

### Separate discovery, reachability, and device action

Treat these as distinct concerns:

1. **Port observation:** link state and removal timing.
2. **Discovery:** LLDP identity and advertised management addresses.
3. **Reachability assessment:** can the switch/container communicate with the device?
4. **Reachability recovery:** temporary VLAN addressing and mandatory cleanup.
5. **Device operation:** MN-IP REST actions.
6. **Workflow state:** one-shot guard, reboot handling, re-arm, errors.
7. **Reporting:** operator-readable and machine-readable evidence.

Do not place MN-IP REST logic inside the Onyx adapter. Do not place Onyx CLI parsing inside the MN-IP device adapter.

### Current watcher state model

The prototype effectively uses:

```text
WAITING_FOR_LINK
  -> WAITING_FOR_LLDP
  -> DISCOVERED
  -> CHECKING_REACHABILITY
  -> RECOVERING_REACHABILITY (optional)
  -> RESETTING
  -> PROCESSED
  -> WAITING_FOR_60_SECONDS_DOWN
  -> WAITING_FOR_LINK
```

Future code must implement explicit named states rather than relying on booleans alone. Persist sufficient state before destructive actions if restart recovery is introduced.

## Current source limitations

- Active code is under `src/mnip_test_automation/`; the historical `v0.1/` directory was removed after v0.5 was validated on the SN2410.
- Multiple short-lived SSH sessions are opened per poll/workflow.
- CLI reading uses sleeps and broad `recv()` calls.
- LLDP extraction uses a regex.
- Temporary address selection assumes `/24` and does not check conflicts.
- Port, VLAN, timing, and policy are partly hard-coded.
- No durable state, structured event log, test suite, or result record.
- No post-reset readiness check.
- Host-key verification uses PoC behavior.
- Local YAML credentials were used during development.

## Required next engineering steps

1. Preserve/tag the validated v0.4 milestone.
2. Move active code to a conventional `src/mnip_test_automation/` layout.
3. Implement a prompt-aware Onyx session abstraction with error recognition.
4. Add typed port-status and LLDP discovery records.
5. Make lane, VLAN, poll interval, re-arm duration, and recovery prefix explicit configuration.
6. Add address validation and conflict detection before adding a temporary address.
7. Guarantee and verify cleanup; surface cleanup failure prominently.
8. Add tests for parsing, adjacent-address selection, state transitions, reboot link flaps, and failure cleanup.
9. Add structured events and a supported logging/result destination.
10. Add post-reset LLDP rediscovery and readiness checks.
11. Only then implement baseline configuration and four-receiver SDP provisioning.

## Security rules

- Never commit passwords, tokens, private keys, personal credentials, or real local secret configuration.
- Ignore `.env`, local overrides, `.venv`, logs, generated archives, and key material.
- Treat example addresses as lab examples.
- Replace `AutoAddPolicy` with pinned host-key verification before production use.
- Use least-privilege switch and device accounts and an explicit runtime secret mechanism.
- Inspect `git diff --cached` and run a secret scan before every commit.
- Do not change switch filesystem permissions merely to manage Docker archives; use supported Onyx commands.

## Repository guidance

Preserve the original PoC until equivalent behavior has tests and migration history. Do not create an endless sequence of `v0.x/` source directories. Use tags/releases for milestones.

Recommended target layout:

```text
src/mnip_test_automation/
  switches/
  devices/
  discovery/
  reachability/
  workflows/
  reporting/
tests/
docker/
docs/
```

Generated files such as `*.tar`, virtual environments, caches, and local configs must remain outside Git.

## Definition of done

A behavioral change is not complete until:

- code behavior is covered by an automated test or a documented manual validation;
- failure and cleanup behavior are tested, not only the success path;
- user-facing and agent-facing documentation is updated;
- validated facts and proposals are clearly distinguished;
- no secrets or generated binary artifacts are staged;
- Linux VM and Onyx Docker deployment assumptions are checked where relevant; and
- support engineers receive actionable output for failure paths.
