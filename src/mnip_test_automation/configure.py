from getpass import getpass
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path

import yaml


CONFIG_PATH = Path("/mnip-config/config.yaml")

REQUIRED_VLAN_SUBNET = IPv4Network("192.168.39.0/24")
EXAMPLE_SWITCH_IP = "192.168.39.10"
EXAMPLE_FUSION_25G_PORT = "1/1"
EXAMPLE_FUSION_10G_PORT = "1/3"
EXAMPLE_MUON_A10_PORT = "1/5"

FIXED_VLAN = 1
FIXED_PREFIX_LENGTH = 24
FIXED_POLL_INTERVAL = 10
FIXED_REARM_SECONDS = 60
FIXED_WORKFLOW = "factory_reset"


def prompt_with_example(label: str, example: str) -> str:
    while True:
        value = input(f"{label} [example: {example}]: ").strip()

        if value:
            return value

        print("Enter the actual value. The displayed value is an example only.")


def prompt_switch_ip() -> str:
    while True:
        value = prompt_with_example(
            "Switch VLAN IP within 192.168.39.0/24",
            EXAMPLE_SWITCH_IP,
        )

        try:
            address = IPv4Address(value)
        except ValueError:
            print("Enter a valid IPv4 address.")
            continue

        if address not in REQUIRED_VLAN_SUBNET:
            print(
                "The switch VLAN IP must be within "
                "192.168.39.0/24."
            )
            continue

        if address in {
            REQUIRED_VLAN_SUBNET.network_address,
            REQUIRED_VLAN_SUBNET.broadcast_address,
        }:
            print("Enter a usable host address within the subnet.")
            continue

        return str(address)


def main() -> None:
    print()
    print("MN-IP Test Automation v1.0 configuration")
    print("=========================================")
    print()
    print("Network requirement:")
    print("- All onboarding ports must already be access ports in VLAN 1.")
    print("- The switch VLAN IP must be within 192.168.39.0/24.")
    print("- 192.168.39.10 is an example only.")
    print()
    print("Fixed settings:")
    print(f"- Shared access VLAN: VLAN {FIXED_VLAN}")
    print(f"- Temporary recovery prefix: /{FIXED_PREFIX_LENGTH}")
    print(f"- Poll interval: {FIXED_POLL_INTERVAL} seconds")
    print(
        "- Re-arm after continuous link-down: "
        f"{FIXED_REARM_SECONDS} seconds"
    )
    print("- FusioN 25G lane expected speed: 25G")
    print("- FusioN 10G lane expected speed: 10G")
    print("- MuoN A10 lane expected speed: 10G")
    print("- Device workflow: factory reset")
    print("- REST path: /emsfp/node/v1/self/system")
    print('- REST payload: {"config_reset": "system"}')
    print()
    print("Example switchports:")
    print(f"- FusioN 25G: {EXAMPLE_FUSION_25G_PORT}")
    print(f"- FusioN 10G: {EXAMPLE_FUSION_10G_PORT}")
    print(f"- MuoN A10 10G: {EXAMPLE_MUON_A10_PORT}")
    print()
    print("The displayed IP and switchports are examples only.")
    print("Enter the actual values for the target switch.")
    print()

    switch_ip = prompt_switch_ip()
    username = input("Switch username: ").strip()

    if not username:
        raise ValueError("Switch username must not be empty")

    password = getpass("Switch password: ")

    if not password:
        raise ValueError("Switch password must not be empty")

    fusion_25g_port = prompt_with_example(
        "FusioN 25G switchport",
        EXAMPLE_FUSION_25G_PORT,
    )
    fusion_10g_port = prompt_with_example(
        "FusioN 10G switchport",
        EXAMPLE_FUSION_10G_PORT,
    )
    muon_a10_port = prompt_with_example(
        "MuoN A10 10G switchport",
        EXAMPLE_MUON_A10_PORT,
    )

    ports = [
        fusion_25g_port,
        fusion_10g_port,
        muon_a10_port,
    ]

    if len(ports) != len(set(ports)):
        raise ValueError(
            "FusioN 25G, FusioN 10G, and MuoN A10 "
            "must use different switchports"
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
                "name": "fusion-25g-reset",
                "enabled": True,
                "port": fusion_25g_port,
                "expected_speed": "25G",
                "device_family": "fusion",
                "workflow": FIXED_WORKFLOW,
            },
            {
                "name": "fusion-10g-reset",
                "enabled": True,
                "port": fusion_10g_port,
                "expected_speed": "10G",
                "device_family": "fusion",
                "workflow": FIXED_WORKFLOW,
            },
            {
                "name": "muon-a10-reset",
                "enabled": True,
                "port": muon_a10_port,
                "expected_speed": "10G",
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
