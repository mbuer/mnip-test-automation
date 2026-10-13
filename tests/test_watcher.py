from unittest.mock import Mock

from mnip_test_automation.config import (
    AppConfig,
    LaneConfig,
    NetworkConfig,
    SwitchConfig,
    WatcherConfig,
)
from mnip_test_automation.watcher import MultiLaneWatcher


def make_config():
    return AppConfig(
        switch=SwitchConfig(
            host="192.0.2.10",
            username="test-user",
            password="test-password",
        ),
        watcher=WatcherConfig(
            poll_interval_seconds=10,
            rearm_down_seconds=60,
        ),
        network=NetworkConfig(
            vlan=1,
            temporary_prefix_length=24,
        ),
        lanes=(
            LaneConfig(
                name="fusion-reset",
                enabled=True,
                port="1/25",
                expected_speed="25G",
                device_family="fusion",
                workflow="factory_reset",
            ),
            LaneConfig(
                name="muon-a10-reset",
                enabled=True,
                port="1/13",
                expected_speed="10G",
                device_family="muon-a10",
                workflow="factory_reset",
            ),
        ),
    )


def test_lanes_have_independent_runtime_state():
    watcher = MultiLaneWatcher(
        config=make_config(),
        switch=Mock(),
        reset_device=Mock(),
    )

    fusion_lane, muon_lane = watcher.lanes

    fusion_lane.processed = True
    fusion_lane.down_since = 100.0

    assert muon_lane.processed is False
    assert muon_lane.down_since is None


def test_processing_muon_does_not_mark_fusion_processed():
    switch = Mock()
    switch.port_is_up.return_value = True
    switch.get_lldp_ip.return_value = "172.20.50.100"
    switch.is_reachable.return_value = True

    reset_device = Mock()

    watcher = MultiLaneWatcher(
        config=make_config(),
        switch=switch,
        reset_device=reset_device,
    )

    fusion_lane, muon_lane = watcher.lanes

    watcher.process_lane(muon_lane, now=100.0)

    assert fusion_lane.processed is False
    assert muon_lane.processed is True

    switch.port_is_up.assert_called_once_with("1/13")
    switch.get_lldp_ip.assert_called_once_with("1/13")
    reset_device.assert_called_once_with("172.20.50.100")


def test_short_link_drop_does_not_rearm_processed_lane():
    switch = Mock()
    switch.port_is_up.return_value = False

    watcher = MultiLaneWatcher(
        config=make_config(),
        switch=switch,
        reset_device=Mock(),
    )

    lane = watcher.lanes[0]
    lane.processed = True
    lane.down_since = 100.0

    watcher.process_lane(lane, now=150.0)

    assert lane.processed is True


def test_sustained_link_drop_rearms_only_selected_lane():
    switch = Mock()
    switch.port_is_up.return_value = False

    watcher = MultiLaneWatcher(
        config=make_config(),
        switch=switch,
        reset_device=Mock(),
    )

    fusion_lane, muon_lane = watcher.lanes

    fusion_lane.processed = True
    fusion_lane.down_since = 100.0

    muon_lane.processed = True
    muon_lane.down_since = 130.0

    watcher.process_lane(fusion_lane, now=160.0)

    assert fusion_lane.processed is False
    assert muon_lane.processed is True
