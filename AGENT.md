# AGENT.md

## Read first

This file is durable context for future AI agents and contributors. Also read `README.md` and the focused document relevant to the task. Keep answers short and step-by-step during technical walkthroughs.

## Current release state

- Branch under development: `feature/v1.0-production`
- Current candidate: `v1.0-rc1`
- Runtime: Docker on NVIDIA/Mellanox SN2410 running Onyx
- Validated switch OS: Onyx `X86_64 3.10.4100`; deployment requires `docker start ... user-env` support.
- Deployment scope: controlled Riedel lab/test-station environment
- Shared access network: VLAN 1
- Required switch VLAN subnet: `192.168.39.0/24`
- Example switch VLAN IP only: `192.168.39.10`
- Example ports only:
  - FusioN 25G: `1/1`
  - FusioN 10G: `1/3`
  - MuoN A10 10G: `1/5`
- LED indication work is deferred.

## Lane behavior

Three independently configured lanes are implemented:

1. FusioN, expected 25G
2. FusioN, expected 10G
3. MuoN A10, expected 10G

Port values are operator-entered. Expected speed is informational; v1.0 does not configure or validate speed.

Each lane has independent processed state and link-down timer. A processed lane re-arms only after 60 seconds continuously down.

## Exact API contract

Both device families use:

```text
PUT /emsfp/node/v1/self/system
```

with exactly:

```json
{"config_reset": "system"}
```

`device.py` owns the request. Tests must continue to lock method, path, narrow payload, timeout, and HTTP status handling.

## Network rules

- All onboarding ports must already be access ports in VLAN 1.
- Switch VLAN IP must be a usable address in `192.168.39.0/24`.
- The helper and config loader must enforce that subnet.
- Temporary recovery assumes `/24`.
- Duplicate enabled port names and port values are invalid.
- If active lanes advertise the same LLDP management IP, skip reset and log the conflict.
- General temporary-address conflict detection is not yet implemented.

## Runtime configuration

Configuration is stored outside the image:

```text
Onyx label: mnip-config
Mount: /mnip-config
File: /mnip-config/config.yaml
```

The image contains only `config/config.example.yaml`. Real credentials are entered by `mnip-configure` and must never be committed or baked into the image.

## Module boundaries

- `app.py`: startup/composition only
- `config.py`: select, load, and validate configuration
- `configure.py`: interactive writer and clearly labeled examples
- `device.py`: exact REST action
- `models.py`: lane state
- `switch.py`: Onyx CLI operations
- `watcher.py`: lane orchestration, conflict guard, cleanup, and re-arm

Do not mix device REST logic into `switch.py`. Do not put Onyx parsing into `device.py`.

## Onyx command-mode rule

Operational instructions must state the prompt.

Most project commands run at:

```text
(config) #
```

Reach it with:

```text
enable
configure terminal
```

Container removal uses:

```text
(config) # docker
(config docker) # no start <container>
(config docker) # exit
```

If a command beginning with `docker` is rejected, check whether the prompt is already `(config docker) #`.

## Validated findings

- CLI-only account requires Paramiko `invoke_shell()`.
- Fresh SSH session begins at `>`; configuration requires `enable` then `configure terminal`.
- `terminal length 0` is rejected; current code uses `999`.
- Onyx ping is continuous and is stopped with Ctrl+C.
- LLDP discovery can succeed without Layer 3 reachability.
- Onyx accepts an additional IPv4 address on the existing VLAN interface.
- REST must run from the switch-hosted container for recovered reachability.
- Temporary addresses are removed through `finally` cleanup.
- Persistent Docker labels mount read/write and survive helper-container removal.
- FusioN 25G and MuoN A10 10G workflows are hardware-validated under v0.6.
- v1.0-rc1 third-lane FusioN 10G validation is pending.

## v1.0 release gate

Before final v1.0 merge/tag:

- configuration loader enforces `192.168.39.0/24`;
- three independent lanes are covered by tests;
- all tests pass;
- fresh deployment follows `docs/deployment.md`;
- FusioN 25G, FusioN 10G, and MuoN A10 lanes succeed independently;
- duplicate-IP guard is observed;
- temporary addresses are removed;
- independent 60-second re-arm behavior is verified;
- documentation is updated from release-candidate to validated release status.

## Repository rules

- Never commit passwords, runtime config, private keys, `.env`, `.venv`, TAR files, caches, or logs containing sensitive data.
- Run `git diff --check`, tests, secret review, and stale-reference checks before commit.
- Keep historical evidence in `docs/validation-history.md`; do not duplicate project history across every document.
- Do not claim hardware validation until observed and recorded.
