# NVIDIA Onyx Integration

## Validated environment

The Phase 1 proof of concept used an NVIDIA/Mellanox SN2410 running Onyx. A Python Docker image built on the Utility VM was exported, transferred, loaded through the Onyx Docker CLI, and executed on the switch.

## SSH and CLI behavior

The tested account presented the Onyx CLI rather than a UNIX shell. A remote invocation such as the following was therefore not usable:

```bash
ssh user@switch "show version concise"
```

Onyx returned:

```text
UNIX shell commands cannot be executed using this account.
```

The working Python pattern was:

1. Create a Paramiko `SSHClient`.
2. Connect with the available authentication method.
3. Call `invoke_shell()`.
4. Wait for the CLI prompt.
5. Send the Onyx command followed by a newline.
6. Read until the prompt returns or a timeout expires.

The PoC used fixed sleeps. Replace that behavior with prompt-aware reads before relying on the service unattended.

## LLDP command

Validated command:

```text
show lldp interfaces ethernet 1/25 remote
```

The output included remote system details and a management-address table. The PoC extracted the IPv4 row. A production parser should handle no neighbor, incomplete output, paging, multiple addresses, command errors, and unexpected formatting.

## Terminal paging

`terminal length 0` was rejected by the tested Onyx version because the accepted range began at 5. A large supported value such as `terminal length 999` may reduce paging, but prompt and pager handling should still be implemented.

## Docker workflow

The validated lifecycle was:

```text
Build on Utility VM
  -> docker save
  -> transfer archive to switch
  -> load image in Onyx Docker mode
  -> start named container
  -> inspect status with show docker ps / show docker containers
```

A successful one-shot run appeared as `Exited (0)`. The stopped container retained its name, so attempting to start a new container with the same name failed. Deployment tooling must remove or uniquely name completed containers.

## Observability

The switch-hosted PoC performed the reset successfully, but the workflow did not provide convenient application output to the operator. Future deployment must define one or more supported feedback paths:

- Onyx-supported logging facility
- Mounted persistent location where supported
- Remote syslog
- Structured result sent to a central service
- A deliberately retained container with accessible logs, if Onyx supports that operation

Do not use arbitrary sleep delays merely to keep a container visible as the final observability strategy.

## Onyx-provided environment

Onyx injected environment variables describing platform and VRF context into the container. These values can be useful for diagnostics, but application behavior should not depend on undocumented variables without validation and documentation.
