from unittest.mock import patch

import yaml

from mnip_test_automation import configure


def test_helper_writes_three_lane_configuration(tmp_path):
    config_path = tmp_path / "config.yaml"

    answers = iter([
        "192.168.39.20",
        "admin",
        "1/1",
        "1/3",
        "1/5",
    ])

    with (
        patch.object(configure, "CONFIG_PATH", config_path),
        patch("builtins.input", side_effect=lambda _: next(answers)),
        patch(
            "mnip_test_automation.configure.getpass",
            return_value="test-password",
        ),
    ):
        configure.main()

    written = yaml.safe_load(config_path.read_text())

    assert written["switch"] == {
        "host": "192.168.39.20",
        "username": "admin",
        "password": "test-password",
    }

    assert written["network"] == {
        "vlan": 1,
        "temporary_prefix_length": 24,
    }

    assert written["lanes"] == [
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
    ]
