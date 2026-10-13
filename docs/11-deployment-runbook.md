# v0.6 Deployment Runbook

This runbook deploys `mnip-test-automation:v0.6` from a Windows workstation to an NVIDIA/Mellanox SN2410 running Onyx.

It is written for direct copy and paste. Replace values in angle brackets before executing a command.

## What v0.6 deploys

- Persistent multi-lane watcher
- FusioN factory-reset lane, default port `1/25`, expected 25G
- MuoN A10 factory-reset lane, default port `1/13`, expected 10G
- LLDP management-address discovery
- Temporary `/24` reachability recovery on shared VLAN 1
- Exact reset request:

```http
PUT /emsfp/node/v1/self/system
```

```json
{"config_reset": "system"}
```

- 10-second polling
- 60-second continuous link-down re-arm protection
- Shared-VLAN duplicate management-IP guard
- Persistent configuration stored in an Onyx Docker storage label

## Important assumptions

- Both onboarding ports are already configured as access ports in VLAN 1.
- The FusioN port is already configured for 25G.
- The MuoN A10 port is already configured for 10G.
- v0.6 reports expected speeds but does not change or validate switchport speed.
- Simultaneously connected devices must not use the same management IP. The watcher detects identical LLDP management addresses across configured lanes and skips the reset.
- Use `now` during validation. Do not configure automatic startup until restart behavior and operational ownership are agreed.

## Required Onyx CLI mode

Unless a step explicitly says otherwise, all Onyx commands in this guide must be entered at:

```text
MN-VirtU-48-S-FR [standalone: master] (config) #
```

To reach that prompt:

```text
enable
configure terminal
```

If the prompt is `(config docker) #`, return to `(config) #` first:

```text
exit
```

Do not prefix commands with `docker` while already inside `(config docker) #`.

---

## 1. Download the release archive

Download the release TAR to the Windows user Downloads folder.

Expected filename:

```text
mnip-test-automation-v0.6.tar
```

Optional PowerShell verification:

```powershell
Set-Location "$HOME\Downloads"
Get-Item .\mnip-test-automation-v0.6.tar | Select-Object Name,Length,LastWriteTime
```

The validated archive is approximately 58 MB. A materially larger archive may indicate that local virtual environments or generated files were included in the Docker build context.

## 2. Copy the TAR to the switch

Run from Windows PowerShell:

```powershell
Set-Location "$HOME\Downloads"
scp .\mnip-test-automation-v0.6.tar admin@<SWITCH_IP>:/var/opt/tms/images/
```

Example lab destination:

```powershell
scp .\mnip-test-automation-v0.6.tar admin@192.168.39.10:/var/opt/tms/images/
```

Enter the switch password when prompted.

## 3. Connect to Onyx

From Windows PowerShell:

```powershell
ssh admin@<SWITCH_IP>
```

Enter privileged configuration mode:

```text
enable
configure terminal
```

Confirm the prompt ends with:

```text
(config) #
```

## 4. Stop and remove an existing watcher

Skip this section for a first deployment.

At the `(config) #` prompt, inspect containers:

```text
show docker ps
```

If `mnip-watcher-v06` exists, enter Docker configuration mode and remove it:

```text
docker
no start mnip-watcher-v06
exit
```

Confirm the prompt is back at `(config) #`:

```text
show docker ps
```

## 5. Replace an existing v0.6 image

Skip this section when v0.6 is not already loaded.

At the `(config) #` prompt:

```text
docker remove image mnip-test-automation v0.6
```

If removal fails, a running or exited container still references the image. Remove that container first using `docker` -> `no start <container>` -> `exit`.

## 6. Load the image

At the `(config) #` prompt:

```text
docker load mnip-test-automation-v0.6.tar
```

Expected result:

```text
Loaded image: mnip-test-automation:v0.6
```

Verify:

```text
show docker images
```

## 7. Create fresh persistent configuration storage

Check existing labels:

```text
show docker labels
```

For a fresh deployment, create the label:

```text
docker label mnip-config
```

The label is mounted read/write inside the container at:

```text
/mnip-config
```

Do not delete an existing `mnip-config` label during a normal upgrade. The label contains the runtime configuration and switch credentials.

## 8. Start the configuration helper

At the `(config) #` prompt:

```text
docker start mnip-test-automation v0.6 mnip-config-helper now label mnip-config user-env MNIP_MODE=hold
```

Verify:

```text
show docker container mnip-config-helper
```

Expected:

```text
status : running
```

## 9. Run the interactive configuration helper

At the `(config) #` prompt:

```text
docker exec mnip-config-helper mnip-configure
```

The helper displays the fixed settings before prompting:

```text
Shared access VLAN: VLAN 1
Temporary recovery prefix: /24
Poll interval: 10 seconds
Re-arm after continuous link-down: 60 seconds
FusioN expected port speed: 25G
MuoN A10 expected port speed: 10G
Device workflow: factory reset
REST path: /emsfp/node/v1/self/system
REST payload: {"config_reset": "system"}
```

The helper then prompts for:

```text
Switch/VLAN IP [192.168.39.10]:
Switch username:
Switch password:
FusioN switchport [1/25]:
MuoN A10 switchport [1/13]:
```

Press Enter to accept a displayed default. The two lane ports must be different.

Expected completion:

```text
Configuration written to /mnip-config/config.yaml
Restart the watcher container to apply the configuration.
```

## 10. Remove the helper container

At the `(config) #` prompt:

```text
docker
no start mnip-config-helper
exit
```

The helper container is removed. The configuration remains in the `mnip-config` label.

## 11. Start the watcher

Keep devices disconnected during initial startup.

At the `(config) #` prompt:

```text
docker start mnip-test-automation v0.6 mnip-watcher-v06 now label mnip-config
```

Verify:

```text
show docker container mnip-watcher-v06
```

Expected:

```text
status : running
```

## 12. Validate one lane at a time

### 12.1 FusioN lane

1. Keep the MuoN A10 disconnected.
2. Connect the FusioN to the configured FusioN port.
3. Allow at least 20 seconds for link and LLDP polling.
4. Confirm the device factory-resets.
5. Confirm the watcher remains running.
6. Confirm no temporary address remains:

```text
show ip interface brief
```

### 12.2 MuoN A10 lane

1. Disconnect the FusioN or ensure both devices use unique management IPs.
2. Connect the MuoN A10 to the configured MuoN port.
3. Allow at least 20 seconds for link and LLDP polling.
4. Confirm the device factory-resets.
5. Confirm the watcher remains running.
6. Confirm no temporary address remains:

```text
show ip interface brief
```

MuoN A10 hardware validation must be recorded separately from FusioN validation. The shared endpoint and payload are implemented, but documentation should only claim MuoN validation after the actual hardware cycle succeeds.

## 13. Verify lane discovery manually

FusioN default lane:

```text
show interfaces ethernet 1/25
show lldp interfaces ethernet 1/25 remote
```

MuoN A10 default lane:

```text
show interfaces ethernet 1/13
show lldp interfaces ethernet 1/13 remote
```

Useful expected fields include `Operational state`, `Actual speed`, remote system name, remote system description, and the IPv4 management address.

## 14. Change the configured switchports later

Stop the watcher:

```text
docker
no start mnip-watcher-v06
exit
```

Start the helper:

```text
docker start mnip-test-automation v0.6 mnip-config-helper now label mnip-config user-env MNIP_MODE=hold
```

Run the configuration helper:

```text
docker exec mnip-config-helper mnip-configure
```

Remove the helper:

```text
docker
no start mnip-config-helper
exit
```

Restart the watcher:

```text
docker start mnip-test-automation v0.6 mnip-watcher-v06 now label mnip-config
```

## 15. Stop the watcher

At the `(config) #` prompt:

```text
docker
no start mnip-watcher-v06
exit
```

The persistent configuration label remains.

## 16. Remove the loaded image

First remove all containers that reference v0.6. Then, at the `(config) #` prompt:

```text
docker remove image mnip-test-automation v0.6
```

## 17. Remove the stored TAR

At the `(config) #` prompt:

```text
image delete mnip-test-automation-v0.6.tar
```

Removing the loaded image does not remove the stored TAR, and deleting the TAR does not remove the loaded image.

## 18. Remove persistent configuration

Only do this when intentionally wiping the runtime configuration.

First remove all containers using the label. Then at the `(config) #` prompt:

```text
docker no label mnip-config
```

This deletes the persistent configuration, including stored switch credentials.

## Quick verification checklist

- Image appears in `show docker images`
- `mnip-config` appears in `show docker labels`
- Configuration helper displays fixed settings
- Helper writes `/mnip-config/config.yaml`
- Watcher status is `running`
- FusioN lane resets only once per connection cycle
- MuoN A10 lane resets only once per connection cycle
- Duplicate LLDP management IPs cause the watcher to skip reset
- Temporary VLAN address is removed after each workflow
- Lane re-arms only after 60 seconds continuously down

## Common CLI-mode errors

### `docker` is unrecognized

The prompt is probably `(config docker) #`. Run:

```text
exit
```

Then retry from `(config) #`.

### `configure terminal` is unrecognized in automated SSH

A fresh Onyx SSH session starts at `>`. The application must send:

```text
enable
configure terminal
```

### Image cannot be removed

A container still references the image. Run:

```text
show docker ps
```

Remove the referencing container using `docker` -> `no start <container>` -> `exit`.

### Watcher exits immediately

Check that the watcher was started with:

```text
label mnip-config
```

If the label is new or empty, run the helper workflow first.
