# AGENT.md

## Purpose

Durable operating context for AI agents and human collaborators working on MNIP Test Automation. Read this file, `README.md`, and the relevant focused document under `docs/` before changing code, architecture, deployment, or validated claims.

Keep this file concise and factual. Human explanation belongs in the README and focused documents. Update this file whenever a validated finding changes an architectural assumption.

## Project identity

- Repository: `https://github.com/mbuer/mnip-test-automation`
- Mission: automate onboarding, provisioning, validation, and long-duration testing of Riedel MN-IP devices.
- Switch platform: NVIDIA/Mellanox SN2410 running Onyx.
- Development platform: Linux Utility VM with Docker.
- Runtime: Onyx Docker.
- Current release candidate: v0.6 multi-lane factory-reset watcher.
- Current device lanes:
  - FusioN, default Ethernet `1/25`, expected 25G.
  - MuoN A10, default Ethernet `1/13`, expected 10G.
- Shared access network: VLAN 1 in the current lab design.

Factory reset is the first proven device action, not the final purpose of the framework.

## User priorities

1. Keep answers and technical walkthroughs short and step-by-step.
2. Keep repository documentation synchronized with validated findings.
3. Write human-facing documents for support engineers; keep this file efficient for future agents.
4. Clearly distinguish validated behavior, implemented-but-unvalidated behavior, and future work.
5. Never commit credentials, local runtime configuration, Docker TAR files, virtual environments, keys, or logs with sensitive details.
6. Prefer small tested changes over speculative framework code.
7. In Onyx instructions, always state the required CLI prompt. Most Docker/image/show commands in this project are executed from `(config) #`; `no start` is entered after `docker` at `(config docker) #`.

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

## Validated milestones

### October 4, 2026: one-shot feasibility

- Built the Python Docker image on the Utility VM.
- Queried Onyx LLDP on Ethernet 1/25 through `invoke_shell()`.
- Extracted the MN-IP management IPv4 address.
- Sent the factory-reset request and observed HTTP 200 with `system rebooting`.
- Ran the same image on the SN2410.

### October 6, 2026: persistent single-lane watcher

- Proved LLDP discovery is independent of Layer 3 reachability.
- Added and removed an additional IPv4 address on VLAN 1.
- Reached devices on arbitrary lab subnets and reset them from the switch-hosted container.
- Added 10-second polling and a 60-second continuous-down re-arm guard.
- Validated cleanup and prevention of reboot-induced reset cycles.

### October 12, 2026: v0.6 multi-lane implementation and deployment workflow

Implemented and unit-tested:

- typed multi-lane configuration;
- independent lane runtime state;
- port-aware Onyx adapter;
- exact narrow factory-reset request;
- shared watcher for FusioN and MuoN A10;
- duplicate management-IP guard across the shared VLAN;
- persistent Onyx configuration stored in a Docker label;
- interactive `mnip-configure` helper;
- helper hold mode started with `MNIP_MODE=hold`;
- secret-safe Docker image that does not contain local credentials;
- 10 passing unit tests;
- final Docker TAR remains approximately 58 MB.

Validated on Onyx:

- `mnip-config` label mounts read/write at `/mnip-config`;
- helper container remains running in hold mode;
- `docker exec mnip-config-helper mnip-configure` supports interactive prompts and hidden password entry;
- configuration persists after removing the helper container;
- watcher starts from the persistent configuration label;
- the FusioN lane successfully runs under the multi-lane watcher.

MuoN A10 support is implemented using the identical endpoint and narrow payload, but do not claim hardware validation until an actual MuoN A10 reset cycle is completed and recorded.

## Exact factory-reset API contract

Both device families use:

```text
PUT /emsfp/node/v1/self/system
```

with exactly:

```json
{"config_reset": "system"}
```

`src/mnip_test_automation/device.py` owns this request. `tests/test_device.py` locks the exact method, path, payload, and timeout. Do not send a full system representation or unrelated fields.

## v0.6 configuration model

Runtime configuration is stored outside the image:

```text
Onyx Docker label: mnip-config
Container mount:   /mnip-config
Config file:       /mnip-config/config.yaml
```

The interactive helper displays the fixed settings, then asks for:

- Switch/VLAN IP
- Switch username
- Switch password
- FusioN switchport
- MuoN A10 switchport

Fixed v0.6 settings:

- VLAN 1
- temporary prefix `/24`
- 10-second polling
- 60-second continuous-down re-arm
- FusioN expected speed 25G
- MuoN A10 expected speed 10G
- factory-reset workflow and exact narrow API request

Expected speed is descriptive only. v0.6 does not configure or validate switchport speed. Operators must prepare the ports.

## Shared-VLAN rules

All configured onboarding ports are expected to be access ports in VLAN 1.

- Lane ports must be different; the helper and config loader reject duplicates.
- Simultaneously connected devices must not use the same management IP.
- Before processing a lane, the watcher checks other active lanes for the same LLDP management IP and skips reset on conflict.
- This guard does not replace general address-conflict detection for the derived temporary IP.

## Architecture boundaries

- `config.py`: select/load/validate runtime configuration.
- `models.py`: immutable lane configuration plus independent mutable lane state.
- `switch.py`: Onyx SSH, port status, LLDP, switch-side ping, and temporary VLAN address operations.
- `device.py`: exact MN-IP factory-reset API request.
- `watcher.py`: lane orchestration, conflict guard, cleanup, processed state, and re-arm.
- `configure.py`: interactive persistent config writer.
- `app.py`: composition and startup only.

Do not place MN-IP REST logic in the switch adapter. Do not place Onyx CLI parsing in the device adapter.

## Onyx facts and pitfalls

- The tested account is an Onyx CLI account, not a UNIX shell account.
- `exec_command()` and remote UNIX commands are unsuitable; use `invoke_shell()`.
- A new SSH session begins at `>` and configuration requires `enable` then `configure terminal`.
- `terminal length 0` is rejected; current code uses `terminal length 999`.
- Onyx `ping` is continuous and is stopped by sending Ctrl+C.
- `ping <ip> count 2` is invalid on the tested release.
- REST must run from the Onyx-hosted container. A temporary switch VLAN address does not give the Utility VM the same route.
- Loaded Docker images and stored TAR files are separate.
- Remove a loaded image with `docker remove image <name> <version>` from `(config) #`.
- Remove a TAR with `image delete <filename>` from `(config) #`.
- Remove a container with `docker` -> `no start <name>` -> `exit`.
- If a command beginning with `docker` is rejected, check whether the prompt is already `(config docker) #` and run `exit` once.

## Current limitations

- Fixed sleeps and broad `recv()` calls remain.
- Multiple SSH sessions are opened per polling cycle.
- LLDP and CLI parsing remain regex/text based.
- Temporary recovery assumes `/24` and adjacent `+1`, except `.254` uses `-1`.
- No general ARP/address-conflict check for the derived temporary address.
- Expected port speed is not validated or configured.
- No durable processed state across container restart.
- No structured operational log or supported log retrieval path.
- No post-reset health/readiness verification.
- `AutoAddPolicy` and password-based switch login remain prototype choices.
- MuoN A10 hardware validation is pending.

## Required next steps

1. Complete and record MuoN A10 hardware validation on the 10G lane.
2. Update the proof-of-concept results with the actual MuoN observation.
3. Improve prompt-aware Onyx command handling.
4. Verify cleanup explicitly and treat cleanup failure as high severity.
5. Add post-reset rediscovery/readiness checks.
6. Decide how watcher logs/results are retrieved from Onyx.
7. Only then proceed toward configuration, SDP provisioning, and media validation.

## Definition of done

A behavioral change is complete only when:

- tests or a documented manual validation cover the behavior;
- failure and cleanup paths are considered;
- README, AGENT, and relevant focused docs are updated;
- validated claims are separated from unvalidated implementation;
- no secrets or generated artifacts are staged;
- VM build and Onyx runtime assumptions are checked; and
- Onyx command examples state the required prompt mode.
