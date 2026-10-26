from pathlib import Path

import pytest
import yaml

from mnip_test_automation.config import load_config


def base_config():
    return {
        "switch": {
            "host": "192.168.39.20",
            "username": "admin",
            "password": "test-password",
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
                "name": "fusion-25g-reset",
                "enabled": True,
                "port": "1/1",
                "expected_speed": "25G",
                "device_family": "fusion",
                "workflow": "factory_reset",
            },
            {
                "name": "fusion-10g-reset",
                "enabled": True,
                "port": "1/3",
                "expected_speed": "10G",
                "device_family": "fusion",
                "workflow": "factory_reset",
            },
            {
                "name": "muon-a10-reset",
                "enabled": True,
                "port": "1/5",
                "expected_speed": "10G",
                "device_family": "muon-a10",
                "workflow": "factory_reset",
            },
        ],
    }


def write_config(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False))
    return path


def test_loader_accepts_three_lanes_and_required_subnet(tmp_path):
    config = load_config(write_config(tmp_path, base_config()))
    assert [lane.name for lane in config.lanes] == [
        "fusion-25g-reset",
        "fusion-10g-reset",
        "muon-a10-reset",
    ]
    assert [lane.port for lane in config.lanes] == ["1/1", "1/3", "1/5"]


def test_loader_rejects_switch_ip_outside_required_subnet(tmp_path):
    raw = base_config()
    raw["switch"]["host"] = "192.168.40.10"

    with pytest.raises(ValueError, match="192.168.39.0/24"):
        load_config(write_config(tmp_path, raw))


def test_loader_rejects_network_and_broadcast_addresses(tmp_path):
    for host in ("192.168.39.0", "192.168.39.255"):
        raw = base_config()
        raw["switch"]["host"] = host

        with pytest.raises(ValueError, match="usable host"):
            load_config(write_config(tmp_path, raw))


def test_loader_rejects_duplicate_three_lane_ports(tmp_path):
    raw = base_config()
    raw["lanes"][2]["port"] = "1/3"

    with pytest.raises(ValueError, match="ports must be unique"):
        load_config(write_config(tmp_path, raw))
