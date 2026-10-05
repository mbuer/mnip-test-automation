# MN-IP API Notes

## Status of this document

This file records behavior validated during the Phase 1 proof of concept. It is not a replacement for the official API documentation for a specific software release.

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

Successful acceptance of the request does not by itself prove that the device completed reset and became ready. A complete workflow must monitor reachability and application readiness after the reboot.

## Safety requirements

Factory reset is destructive. Before broadening deployment:

- Associate the action with an explicit port/workflow configuration.
- Verify that the LLDP neighbor is eligible for the selected workflow.
- Log the discovered identity and action request without logging secrets.
- Prevent repeated resets while the same device remains connected.
- Define action, reboot, and readiness timeouts.
- Preserve a clear failure result when the response is missing or unexpected.

## Future device-adapter responsibilities

- Product and firmware identification
- Factory reset and reboot
- Readiness and health checks
- Configuration deployment
- SDP receiver provisioning
- Status retrieval for ST 2110 reception
- Normalized errors for workflow and reporting layers

## Configuration guidance

Do not hard-code device addresses. The intended model is to discover the current management address through LLDP. Authentication data must be injected at runtime through an approved mechanism and must not be committed.
