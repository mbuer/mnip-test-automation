from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path
import os

import yaml


DEFAULT_CONFIG_PATH = Path("/mnip-config/config.yaml")
LOCAL_CONFIG_PATH = Path("config/config.yaml")

REQUIRED_VLAN_SUBNET = IPv4Network("192.168.39.0/24")


@dataclass(frozen=True)
class SwitchConfig:
    host: str
    username: str
    password: str


@dataclass(frozen=True)
class WatcherConfig:
    poll_interval_seconds: int
    rearm_down_seconds: int


@dataclass(frozen=True)
class NetworkConfig:
    vlan: int
    temporary_prefix_length: int


@dataclass(frozen=True)
class LaneConfig:
    name: str
    enabled: bool
    port: str
    expected_speed: str
    device_family: str
    workflow: str


@dataclass(frozen=True)
class AppConfig:
    switch: SwitchConfig
    watcher: WatcherConfig
    network: NetworkConfig
    lanes: tuple[LaneConfig, ...]


def select_config_path() -> Path:
    configured_path = os.getenv("MNIP_CONFIG_PATH")

    if configured_path:
        return Path(configured_path)

    if DEFAULT_CONFIG_PATH.exists():
        return DEFAULT_CONFIG_PATH

    return LOCAL_CONFIG_PATH


def load_config(path: Path | None = None) -> AppConfig:
    config_path = path or select_config_path()

    with config_path.open(encoding="utf-8") as config_file:
        raw = yaml.safe_load(config_file)

    if not isinstance(raw, dict):
        raise ValueError("Configuration root must be a mapping")

    lane_configs = tuple(
        LaneConfig(
            name=str(lane["name"]),
            enabled=bool(lane.get("enabled", True)),
            port=str(lane["port"]),
            expected_speed=str(lane["expected_speed"]),
            device_family=str(lane["device_family"]),
            workflow=str(lane["workflow"]),
        )
        for lane in raw.get("lanes", [])
    )

    enabled_lanes = tuple(lane for lane in lane_configs if lane.enabled)

    if not enabled_lanes:
        raise ValueError("At least one lane must be enabled")

    lane_names = [lane.name for lane in enabled_lanes]
    if len(lane_names) != len(set(lane_names)):
        raise ValueError("Enabled lane names must be unique")

    lane_ports = [lane.port for lane in enabled_lanes]
    if len(lane_ports) != len(set(lane_ports)):
        raise ValueError("Enabled lane ports must be unique")

    switch_host = IPv4Address(str(raw["switch"]["host"]))

    if switch_host not in REQUIRED_VLAN_SUBNET:
        raise ValueError(
            "Switch VLAN IP must be within 192.168.39.0/24"
        )

    if switch_host in {
        REQUIRED_VLAN_SUBNET.network_address,
        REQUIRED_VLAN_SUBNET.broadcast_address,
    }:
        raise ValueError(
            "Switch VLAN IP must be a usable host address"
        )

    return AppConfig(
        switch=SwitchConfig(
            host=str(switch_host),
            username=str(raw["switch"]["username"]),
            password=str(raw["switch"]["password"]),
        ),
        watcher=WatcherConfig(
            poll_interval_seconds=int(
                raw.get("watcher", {}).get("poll_interval_seconds", 10)
            ),
            rearm_down_seconds=int(
                raw.get("watcher", {}).get("rearm_down_seconds", 60)
            ),
        ),
        network=NetworkConfig(
            vlan=int(raw.get("network", {}).get("vlan", 1)),
            temporary_prefix_length=int(
                raw.get("network", {}).get("temporary_prefix_length", 24)
            ),
        ),
        lanes=enabled_lanes,
    )
