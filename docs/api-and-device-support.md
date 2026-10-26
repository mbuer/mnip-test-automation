# API and Device Support

## Exact reset request

```http
PUT /emsfp/node/v1/self/system
Content-Type: application/json
```

```json
{"config_reset": "system"}
```

The API accepts narrow PUT changes. The application intentionally sends only `config_reset` and does not send unrelated system fields.

`tests/test_device.py` verifies the exact request contract.

## Supported lanes

### FusioN 25G

- Expected link speed: 25G
- Hardware-validated under v0.6
- v1.0 example port: `1/1`

### FusioN 10G

- Expected link speed: 10G
- Implemented as the third v1.0 lane
- Hardware validation required before final v1.0 release
- v1.0 example port: `1/3`

### MuoN A10

- Expected link speed: 10G
- Uses the same exact reset path and narrow payload
- Hardware-validated repeatedly under v0.6
- v1.0 example port: `1/5`

Example ports are not product defaults.

## Request acceptance versus workflow success

HTTP success proves request acceptance, not completed recovery. A full workflow result should eventually include:

- request accepted;
- link/reboot observed;
- LLDP returns;
- device readiness confirmed;
- temporary switch address removed;
- final outcome recorded.

Current code validates request status and uses observable reboot behavior during lab validation. Post-reset readiness remains future work.

## Future device operations

- product and firmware identification;
- baseline configuration;
- four-receiver SDP provisioning;
- ST 2110 receiver checks;
- video-output validation;
- long-duration health monitoring.
