from getpass import getpass
from pathlib import Path

import yaml


CONFIG_PATH = Path("/mnip-config/config.yaml")

DEFAULT_SWITCH_IP = "192.168.39.10"
DEFAULT_FUSION_PORT = "1/25"
DEFAULT_MUON_PORT = "1/13"

FIXED_VLAN = 1
FIXED_PREFIX_LENGTH = 24
FIXED_POLL_INTERVAL = 10
FIXED_REARM_SECONDS = 60
FIXED_FUSION_SPEED = "25G"
FIXED_MUON_SPEED = "10G"
FIXED_WORKFLOW = "factory_reset"


def prompt_with_default(label: str, default: str) -> str:
    value = input(f"{label} [{default}]: ").strip()
    return value or default


def main() -> None:
    print()
    print("MN-IP Test Automation configuration")
    print("===================================")
    print()
    print("Fixed settings:")
    print(f"- Shared access VLAN: VLAN {FIXED_VLAN}")
    print(f"- Temporary recovery prefix: /{FIXED_PREFIX_LENGTH}")
    print(f"- Poll interval: {FIXED_POLL_INTERVAL} seconds")
    print(
        "- Re-arm after continuous link-down: "
        f"{FIXED_REARM_SECONDS} seconds"
    )
    print(f"- FusioN expected port speed: {FIXED_FUSION_SPEED}")
    print(f"- MuoN A10 expected port speed: {FIXED_MUON_SPEED}")
    print("- Device workflow: factory reset")
    print("- REST path: /emsfp/node/v1/self/system")
    print('- REST payload: {"config_reset": "system"}')
    print()
    print("All configured switchports must already be access ports")
    print(f"in the same VLAN, currently fixed to VLAN {FIXED_VLAN}.")
    print()
    print("Devices connected simultaneously must not use duplicate")
    print("management IP addresses on the shared VLAN.")
    print()

    switch_ip = prompt_with_default(
        "Switch/VLAN IP",
        DEFAULT_SWITCH_IP,
    )
    username = input("Switch username: ").strip()
    password = getpass("Switch password: ")

    fusion_port = prompt_with_default(
        "FusioN switchport",
        DEFAULT_FUSION_PORT,
    )
    muon_port = prompt_with_default(
        "MuoN A10 switchport",
        DEFAULT_MUON_PORT,
    )

    if fusion_port == muon_port:
        raise ValueError(
            "FusioN and MuoN A10 must use different switchports"
        )

    config = {
        "switch": {
            "host": switch_ip,
            "username": username,
            "password": password,
        },
        "watcher": {
            "poll_interval_seconds": FIXED_POLL_INTERVAL,
            "rearm_down_seconds": FIXED_REARM_SECONDS,
        },
        "network": {
            "vlan": FIXED_VLAN,
            "temporary_prefix_length": FIXED_PREFIX_LENGTH,
        },
        "lanes": [
            {
                "name": "fusion-reset",
                "enabled": True,
                "port": fusion_port,
                "expected_speed": FIXED_FUSION_SPEED,
                "device_family": "fusion",
                "workflow": FIXED_WORKFLOW,
            },
            {
                "name": "muon-a10-reset",
                "enabled": True,
                "port": muon_port,
                "expected_speed": FIXED_MUON_SPEED,
                "device_family": "muon-a10",
                "workflow": FIXED_WORKFLOW,
            },
        ],
    }

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        yaml.safe_dump(config, sort_keys=False),
        encoding="utf-8",
    )

    print()
    print(f"Configuration written to {CONFIG_PATH}")
    print("Restart the watcher container to apply the configuration.")


if __name__ == "__main__":
    main()
