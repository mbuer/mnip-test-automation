# Deployment

Deploy `mnip-test-automation:v1.0-rc1` from Windows PowerShell to an NVIDIA/Mellanox SN2410 running Onyx.

## Validated platform and prerequisite

Validated platform:

```text
NVIDIA/Mellanox SN2410
Onyx X86_64 3.10.4100
```

v1.0 requires `user-env` support on `docker start`. From the Onyx **`(config) #`** prompt, verify support after loading the image:

```text
docker start mnip-test-automation v1.0-rc1 mnip-config-helper now user-env ?
```

The help output must mention user-defined environment variables. Press `Ctrl+C` after checking. Upgrade Onyx before deployment if `user-env` is rejected.

## Onyx prompt rule

Unless a step explicitly says otherwise, run project commands at:

```text
(config) #
```

Reach it with:

```text
enable
configure terminal
```

Container removal is the exception:

```text
(config) # docker
(config docker) # no start <container-name>
(config docker) # exit
```

If a command beginning with `docker` is rejected at `(config docker) #`, run `exit` and retry from `(config) #`.

## Station assumptions

- Onboarding ports are already access ports in VLAN 1.
- Switch VLAN IP is a usable address in `192.168.39.0/24`.
- Port speed is prepared by the operator; the watcher does not configure or validate speed.
- These are examples only:
  - switch VLAN IP: `192.168.39.10`
  - FusioN 25G port: `1/1`
  - FusioN 10G port: `1/3`
  - MuoN A10 10G port: `1/5`

# Fresh deployment

## 1. Copy the TAR from Windows Downloads

```powershell
Set-Location "$HOME\Downloads"
scp .\mnip-test-automation-v1.0-rc1.tar admin@<SWITCH_IP>:/var/opt/tms/images/
ssh admin@<SWITCH_IP>
```

Enter Onyx configuration mode:

```text
enable
configure terminal
```

Confirm the prompt ends with `(config) #`.

## 2. Load and verify the image

At **`(config) #`**:

```text
docker load mnip-test-automation-v1.0-rc1.tar
show docker images
```

Expected image:

```text
mnip-test-automation:v1.0-rc1
```

Run the `user-env` compatibility check shown above before continuing.

## 3. Create persistent configuration storage

At **`(config) #`**:

```text
show docker labels
docker label mnip-config
```

Create the label only for a fresh deployment. During upgrades, keep the existing label because it contains runtime configuration and credentials.

## 4. Configure the watcher

At **`(config) #`**:

```text
docker start mnip-test-automation v1.0-rc1 mnip-config-helper now label mnip-config user-env MNIP_MODE=hold
show docker container mnip-config-helper
docker exec mnip-config-helper mnip-configure
```

Expected helper-container status: `running`.

Enter:

- actual switch VLAN IP within `192.168.39.0/24`;
- switch username and password;
- actual FusioN 25G port;
- actual FusioN 10G port;
- actual MuoN A10 10G port.

The helper clearly labels example values. The three ports must be different.

Remove the helper:

```text
(config) # docker
(config docker) # no start mnip-config-helper
(config docker) # exit
```

## 5. Start and verify the watcher

Keep all devices disconnected initially. At **`(config) #`**:

```text
docker start mnip-test-automation v1.0-rc1 mnip-watcher-v10 now label mnip-config
show docker container mnip-watcher-v10
```

Expected status: `running`.

# Validation

Validate one lane at a time while the other two devices remain disconnected.

For each of the following lanes:

1. FusioN 25G
2. FusioN 10G
3. MuoN A10 10G

Perform this sequence:

1. Connect the intended device.
2. Allow at least 20 seconds for link and LLDP polling.
3. Confirm factory reset.
4. Confirm `mnip-watcher-v10` remains running.
5. At **`(config) #`**, verify no temporary address remains:

```text
show ip interface brief
```

6. Disconnect the device for at least 60 seconds before reusing the lane.

## Duplicate-IP guard

In a controlled test only, connect two devices that advertise the same management IP. The watcher must report a shared-VLAN conflict and skip factory reset for the conflicting lane. Restore unique addresses before normal operation.

# Operations

## Change configured ports

Stop the watcher, run the helper again with the same `mnip-config` label, then restart the watcher:

```text
(config) # docker
(config docker) # no start mnip-watcher-v10
(config docker) # exit
(config) # docker start mnip-test-automation v1.0-rc1 mnip-config-helper now label mnip-config user-env MNIP_MODE=hold
(config) # docker exec mnip-config-helper mnip-configure
(config) # docker
(config docker) # no start mnip-config-helper
(config docker) # exit
(config) # docker start mnip-test-automation v1.0-rc1 mnip-watcher-v10 now label mnip-config
```

## Upgrade without deleting credentials

1. Remove watcher/helper containers.
2. Keep the `mnip-config` label.
3. At **`(config) #`**, remove the old image only after no container references it.
4. Load the new image.
5. Start the watcher with `label mnip-config`.
6. Revalidate one lane before returning the station to service.

## Rollback

1. Remove containers that reference the release candidate.
2. Keep `mnip-config`.
3. Load or retain the previous known-good image.
4. Start the previous watcher with `label mnip-config`.
5. Revalidate one lane.

## Uninstall

After removing all referencing containers, run at **`(config) #`**:

```text
docker remove image mnip-test-automation v1.0-rc1
image delete mnip-test-automation-v1.0-rc1.tar
```

Delete stored credentials and runtime configuration only when intentionally decommissioning the station:

```text
docker no label mnip-config
```

# Known-good checklist

- Onyx reports `X86_64 3.10.4100` or another deliberately approved release.
- `user-env` help is available.
- Image is listed as `mnip-test-automation:v1.0-rc1`.
- `mnip-config` label exists.
- Helper writes the persistent configuration.
- Watcher status is `running`.
- All three lanes reset independently.
- Duplicate-IP conflict is blocked.
- Temporary VLAN addresses are removed.
- Each lane re-arms independently after 60 seconds continuously down.
