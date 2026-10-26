from unittest.mock import Mock

from mnip_test_automation.config import (
    AppConfig,
    LaneConfig,
    NetworkConfig,
    SwitchConfig,
    WatcherConfig,
)
from mnip_test_automation.watcher import MultiLaneWatcher


def make_three_lane_config():
    return AppConfig(
        switch=SwitchConfig(
            host="192.168.39.20",
            username="admin",
            password="test-password",
        ),
        watcher=WatcherConfig(
            poll_interval_seconds=10,
            rearm_down_seconds=60,
        ),
        network=NetworkConfig(vlan=1, temporary_prefix_length=24),
        lanes=(
            LaneConfig(
                name="fusion-25g-reset",
                enabled=True,
                port="1/1",
                expected_speed="25G",
                device_family="fusion",
                workflow="factory_reset",
            ),
            LaneConfig(
                name="fusion-10g-reset",
                enabled=True,
                port="1/3",
                expected_speed="10G",
                device_family="fusion",
                workflow="factory_reset",
            ),
            LaneConfig(
                name="muon-a10-reset",
                enabled=True,
                port="1/5",
                expected_speed="10G",
                device_family="muon-a10",
                workflow="factory_reset",
            ),
        ),
    )


def test_three_lanes_have_independent_state():
    watcher = MultiLaneWatcher(
        config=make_three_lane_config(),
        switch=Mock(),
        reset_device=Mock(),
    )

    lane_25g, lane_10g, lane_muon = watcher.lanes
    lane_10g.processed = True
    lane_10g.down_since = 100.0

    assert lane_25g.processed is False
    assert lane_25g.down_since is None
    assert lane_muon.processed is False
    assert lane_muon.down_since is None


def test_processing_third_lane_does_not_process_other_lanes():
    switch = Mock()
    switch.port_is_up.return_value = True
    switch.get_lldp_ip.side_effect = [
        "192.168.39.103",
        "192.168.39.101",
        "192.168.39.102",
    ]
    switch.is_reachable.return_value = True
    reset_device = Mock()

    watcher = MultiLaneWatcher(
        config=make_three_lane_config(),
        switch=switch,
        reset_device=reset_device,
    )

    lane_25g, lane_10g, lane_muon = watcher.lanes
    watcher.process_lane(lane_muon, now=100.0)

    assert lane_25g.processed is False
    assert lane_10g.processed is False
    assert lane_muon.processed is True
    reset_device.assert_called_once_with("192.168.39.103")
