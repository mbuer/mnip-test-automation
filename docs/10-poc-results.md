# Proof Of Concept Results

## Date

2026-10-04

## Objective

Validate an end-to-end onboarding trigger using:

- NVIDIA SN2410
- Docker
- LLDP
- MN-IP REST API

## Findings

### Docker

Verified:

- Docker images built on Linux VM
- Docker images exported using docker save
- Images copied via SCP
- Images loaded on SN2410
- Containers executed successfully

### LLDP Discovery

Verified command:

show lldp interfaces ethernet 1/25 remote

Management address returned:

192.168.39.25

### REST API

Verified endpoint:

PUT /emsfp/node/v1/self/system

Factory reset:

{
  "config_reset": "system"
}

Response:

{
  "code": 200,
  "info": "system rebooting"
}

### End-to-End Workflow

SN2410 LLDP

↓

Management IP extracted

↓

REST API Factory Reset

↓

Device reboot

Successful.

## Conclusion

Technical feasibility has been proven.

The architecture is suitable for future onboarding, provisioning, validation and reporting workflows.

