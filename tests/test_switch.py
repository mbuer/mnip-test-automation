from unittest.mock import Mock

import pytest

from mnip_test_automation.config import NetworkConfig, SwitchConfig
from mnip_test_automation.switch import OnyxSwitch


@pytest.fixture
def onyx_switch():
    return OnyxSwitch(
        SwitchConfig(
            host="192.0.2.10",
            username="test-user",
            password="test-password",
        ),
        NetworkConfig(
            vlan=1,
            temporary_prefix_length=24,
        ),
    )


def test_derive_temporary_ip_uses_plus_one(onyx_switch):
    assert (
        onyx_switch.derive_temporary_ip("10.10.10.10")
        == "10.10.10.11"
    )


def test_derive_temporary_ip_uses_minus_one_for_254(onyx_switch):
    assert (
        onyx_switch.derive_temporary_ip("10.10.10.254")
        == "10.10.10.253"
    )


def test_port_is_up_uses_selected_lane_port(onyx_switch):
    onyx_switch.run_commands = Mock(
        return_value="Operational state : Up"
    )

    assert onyx_switch.port_is_up("1/13") is True

    onyx_switch.run_commands.assert_called_once_with([
        "show interfaces ethernet 1/13"
    ])


def test_get_lldp_ip_uses_selected_lane_port(onyx_switch):
    onyx_switch.run_commands = Mock(
        return_value="IPv4            172.20.50.100"
    )

    assert onyx_switch.get_lldp_ip("1/13") == "172.20.50.100"

    onyx_switch.run_commands.assert_called_once_with([
        "terminal length 999",
        "show lldp interfaces ethernet 1/13 remote",
    ])
