from getpass import getpass
from pathlib import Path

import yaml


CONFIG_PATH = Path("/mnip-config/config.yaml")


def main() -> None:
    host = input("Switch host/IP: ").strip()
    username = input("Switch username: ").strip()
    password = getpass("Switch password: ")

    config = {
        "switch": {
            "host": host,
            "username": username,
            "password": password,
        },
        "watcher": {
            "poll_interval_seconds": 10,
            "rearm_down_seconds": 60,
        },
        "network": {
            "vlan": 1,
            "temporary_prefix_length": 24,
        },
        "lanes": [
            {
                "name": "fusion-reset",
                "enabled": True,
                "port": "1/25",
                "expected_speed": "25G",
                "device_family": "fusion",
                "workflow": "factory_reset",
            },
            {
                "name": "muon-a10-reset",
                "enabled": True,
                "port": "1/13",
                "expected_speed": "10G",
                "device_family": "muon-a10",
                "workflow": "factory_reset",
            },
        ],
    }

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        yaml.safe_dump(config, sort_keys=False),
        encoding="utf-8",
    )

    print(f"Configuration written to {CONFIG_PATH}")


if __name__ == "__main__":
    main()
