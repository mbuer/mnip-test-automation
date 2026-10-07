# NVIDIA Onyx Integration

## Validated environment

The validated platform is an NVIDIA/Mellanox SN2410 running Onyx. Docker images are built on a Linux Utility VM, exported as standard archives, transferred to the switch, loaded through the Onyx CLI, and executed by the Onyx Docker service.

## CLI account behavior

The tested account exposes the Onyx CLI, not a UNIX shell. Remote commands such as:

```bash
ssh user@switch "show version concise"
```

are rejected with:

```text
UNIX shell commands cannot be executed using this account.
```

Use Paramiko `invoke_shell()` rather than `exec_command()`.

## Privilege progression

A new automated SSH session starts at:

```text
MN-VirtU-48-S-FR [standalone: master] >
```

Configuration commands are not accepted at this level. The validated sequence is:

```text
enable
configure terminal
interface vlan 1
```

After `enable`, the prompt changes to `#`; after `configure terminal`, it changes to `(config) #`.

Do not assume an interactive session's current privilege carries over to a new Paramiko connection. Each helper that opens a new session must establish the required mode.

## Prompt and paging behavior

- `terminal length 0` was rejected because the tested release accepted values from 5 to 999.
- `terminal length 999` avoided the observed LLDP pager interruption.
- This is not a substitute for prompt and pager handling.
- Commands should be read until the expected prompt returns or an explicit timeout expires.
- CLI responses must be checked for `% Unrecognized command`, `% Incomplete command`, authentication errors, and other failure markers.

## LLDP

Validated command:

```text
show lldp interfaces ethernet 1/25 remote
```

LLDP continued to return a remote management address even when that address was unreachable from the switch's configured subnet. LLDP is therefore the discovery source, not the reachability test.

The watcher must handle:

- `No lldp remote information.` while the link or device is still initializing;
- delayed LLDP after link-up;
- paging or incomplete output;
- missing, multiple, invalid, or ambiguous addresses; and
- neighbor identity changes.

## Link state

Validated command:

```text
show interfaces ethernet 1/25
```

The relevant line was:

```text
Operational state : Up
```

The prototype polls this state and uses a timer while it is Down. A return to Up resets the removal timer.

## Ping behavior

On the tested Onyx CLI:

```text
ping 10.10.10.10
```

runs continuously until interrupted. The automation sends Ctrl+C after a bounded observation interval and parses the statistics.

The attempted syntax:

```text
ping 10.10.10.10 count 2
```

was not supported; `count` was treated as a hostname. Avoid portable-looking CLI assumptions without testing them on the deployed release.

## Additional IPv4 address on VLAN 1

Onyx accepted multiple IPv4 addresses on the same VLAN interface:

```text
enable
configure terminal
interface vlan 1
ip address 10.10.10.11/24
```

The existing primary `192.168.39.10/24` remained present. Cleanup used:

```text
no ip address 10.10.10.11/24
```

This restored connectivity to an adjacent device without replacing the switch's primary VLAN address.

## Docker lifecycle

Validated load and start flow:

```text
docker
load mnip-test-automation-v0.4.tar
start mnip-test-automation v0.4 mnip-watcher-v04 now
```

The start command requires:

1. image name;
2. image version;
3. unique container name; and
4. start mode.

`now` starts the container for the current runtime only. A persistent boot mode such as `now-and-init` was intentionally deferred until the watcher behavior was validated.

### Removal

Container configuration is removed in Docker configuration mode with the supported `no start <container>` flow.

Loaded image removal uses:

```text
docker remove image mnip-test-automation v0.4
```

Stored TAR archives are separate and are removed with:

```text
image delete mnip-test-automation-v0.4.tar
```

Do not change filesystem permissions or expect SFTP access to `/var/opt/tms/images/` merely to delete archives.

## Container networking and execution location

The successful arbitrary-subnet workflow required the REST action to execute inside the switch-hosted container. Configuring an additional address on the switch did not give the Utility VM a route to the device.

The container image requires no Internet access at runtime. Python, Paramiko, Requests, PyYAML, and their dependencies are installed during the Utility VM build and included in the image archive.

## Image size and build context

A build accidentally included `.venv` and generated TAR files, producing a 141 MB export. Adding `.dockerignore` reduced the next image archive to 58 MB.

Recommended exclusions include:

```text
.venv/
__pycache__/
*.pyc
*.pyo
*.tar
.git/
local backups
```

## Observability

`PYTHONUNBUFFERED=1` ensures prompt Python output, but Onyx status output does not by itself provide a convenient application log view. Until a supported log path is implemented, operators may need to infer progress from link state, LLDP, temporary VLAN addresses, device reboot, and container status.

The target solution should use an Onyx-supported logging facility, remote syslog, structured result endpoint, or another validated persistent path.
