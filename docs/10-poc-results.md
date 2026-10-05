# Proof-of-Concept Results

## Validation date

October 4, 2026

## Objective

Determine whether a portable Docker application could use an SN2410's LLDP information to discover an MN-IP device and trigger a factory reset through the device REST API.

## Environment

- Linux Utility VM with Docker
- NVIDIA/Mellanox SN2410 running Onyx
- Riedel MN-IP FusioN device connected to Ethernet 1/25
- Python 3.11 slim container
- Paramiko, Requests, and PyYAML

Sensitive credentials are intentionally not recorded.

## Procedure and findings

### 1. Build and VM execution

The image built successfully on the Utility VM. The application connected to the switch and initially exposed two Onyx-specific constraints:

- The account accepted CLI interaction, not remote UNIX shell commands.
- The working Paramiko method required an interactive shell rather than `exec_command()`.

### 2. LLDP discovery

The application issued:

```text
show lldp interfaces ethernet 1/25 remote
```

The returned data contained remote system identity information and an IPv4 management address. The application successfully extracted that address.

### 3. Factory-reset action

The application sent:

```http
PUT /emsfp/node/v1/self/system
```

with:

```json
{
  "config_reset": "system"
}
```

The observed response was HTTP 200:

```json
{
  "code": 200,
  "info": "system rebooting",
  "debug": null
}
```

The device rebooted as expected.

### 4. Switch-hosted execution

The image was exported from the Utility VM, transferred to the switch, loaded into Onyx Docker, and started. The same workflow executed successfully from the SN2410. The completed container appeared as `Exited (0)`.

The operation succeeded, but feedback was not immediately visible through the Onyx Docker status view. This identified observability as a required feature rather than an optional refinement.

## Conclusion

The PoC validated all critical assumptions for the initial architecture:

- Onyx LLDP data is available to automation.
- The advertised management address can remove the need for a hard-coded device IP.
- An interactive SSH client can operate the Onyx CLI.
- The MN-IP factory-reset endpoint works for the tested device and software.
- A standard Docker image can run on both the Utility VM and SN2410.

## What the PoC did not prove

- Reliable unattended operation over long periods
- Safe repeated processing of multiple devices
- Post-reset readiness validation
- Configuration or SDP provisioning
- ST 2110 stream or video validation
- Durable logs and reports
- Support for other switch or device families

These items remain roadmap work.
