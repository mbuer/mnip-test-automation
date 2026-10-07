# MN-IP API Notes

## Status

This document records behavior validated against the tested FusioN software. It is not a substitute for the official API documentation for a specific release.

## Validated factory-reset action

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

The reset was validated from an Onyx-hosted container after temporary reachability was established to devices using lab addresses in two different private subnets.

## Request acceptance versus workflow success

HTTP 200 proves that the tested API accepted the request. It does not prove that:

- the reset completed;
- the device returned to its factory address;
- required services became ready;
- the device is healthy; or
- the broader onboarding workflow passed.

Future workflow states must rediscover the device after reboot and verify readiness explicitly.

## Address handling

Do not hard-code a current device address. Use LLDP discovery, then perform a separate reachability assessment.

The current prototype may temporarily configure an address on the switch VLAN to reach an otherwise isolated device. This is a switch/workflow responsibility, not part of the MN-IP device adapter. The device adapter should receive a reachable endpoint and return normalized action results.

## Safety requirements

Factory reset is destructive. Before production use:

- associate the action with an explicit, visibly labeled lane;
- verify the discovered neighbor matches eligibility policy;
- guard against duplicate action while the same device remains connected;
- classify timeout, rejected response, reboot, readiness, and cleanup failures separately;
- record identity and action metadata without secrets;
- bound retries; and
- require operator intervention when temporary network cleanup cannot be verified.

## Future device-adapter responsibilities

- product, hardware, and firmware identification;
- factory reset and controlled reboot;
- post-reboot readiness and health;
- baseline configuration deployment;
- SDP receiver provisioning;
- ST 2110 receiver status;
- normalized errors and evidence for workflow/reporting layers.
