# Roadmap

## Completed foundation

- Onyx-hosted Docker runtime
- LLDP discovery
- temporary reachability recovery
- exact narrow factory-reset API
- persistent watcher and 60-second re-arm protection
- persistent external configuration
- interactive configuration helper
- independent multi-lane state
- duplicate management-IP guard
- FusioN 25G and MuoN A10 10G hardware validation

## v1.0 release candidate

- add FusioN 10G third lane;
- use generic, clearly labeled IP and port examples;
- enforce switch VLAN IP in `192.168.39.0/24`;
- test three independent lanes;
- perform fresh three-lane deployment and hardware validation;
- publish streamlined production documentation for the controlled test-station environment.

LED success indication is deliberately deferred.

## Post-v1.0 hardening

- prompt-aware Onyx command completion;
- explicit cleanup verification;
- temporary-address conflict detection;
- durable lane state across restart;
- structured operational logs and results;
- post-reset readiness checks;
- pinned SSH host keys and stronger secret handling.

## Functional expansion

- baseline configuration;
- four-receiver SDP provisioning;
- ST 2110 flow validation;
- video-output confirmation;
- overnight and multi-day test plans;
- additional Riedel devices and switch adapters where justified.
