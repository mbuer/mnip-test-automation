import time
from collections.abc import Callable

from mnip_test_automation.config import AppConfig
from mnip_test_automation.device import factory_reset
from mnip_test_automation.models import LaneState
from mnip_test_automation.switch import OnyxSwitch


class MultiLaneWatcher:
    def __init__(
        self,
        config: AppConfig,
        switch: OnyxSwitch,
        reset_device: Callable = factory_reset,
    ):
        self.config = config
        self.switch = switch
        self.reset_device = reset_device
        self.lanes = [
            LaneState(config=lane)
            for lane in config.lanes
        ]

    def find_ip_conflict(
        self,
        current_lane: LaneState,
        discovered_ip: str,
    ) -> LaneState | None:
        for other_lane in self.lanes:
            if other_lane is current_lane:
                continue

            other_port = other_lane.config.port

            if not self.switch.port_is_up(other_port):
                continue

            other_ip = self.switch.get_lldp_ip(other_port)

            if other_ip == discovered_ip:
                return other_lane

        return None

    def process_lane(
        self,
        lane: LaneState,
        now: float | None = None,
    ) -> None:
        current_time = time.monotonic() if now is None else now
        port = lane.config.port
        name = lane.config.name

        if not self.switch.port_is_up(port):
            if lane.down_since is None:
                lane.down_since = current_time
                print(f"[{name}] Port is down. Starting removal timer.")

            down_seconds = current_time - lane.down_since

            if (
                lane.processed
                and down_seconds >= self.config.watcher.rearm_down_seconds
            ):
                lane.processed = False
                print(
                    f"[{name}] Port remained down for "
                    f"{self.config.watcher.rearm_down_seconds} seconds. "
                    "Lane re-armed."
                )

            return

        lane.down_since = None

        if lane.processed:
            print(f"[{name}] Already processed. Waiting for disconnect.")
            return

        ip = self.switch.get_lldp_ip(port)

        if not ip:
            print(f"[{name}] Port is up. Waiting for LLDP neighbor.")
            return

        print(
            f"[{name}] Found {lane.config.device_family} "
            f"device at {ip}."
        )

        conflicting_lane = self.find_ip_conflict(lane, ip)

        if conflicting_lane:
            print(
                f"[{name}] Shared-VLAN IP conflict: "
                f"{ip} is also advertised on "
                f"{conflicting_lane.config.name} "
                f"({conflicting_lane.config.port}). "
                "Skipping factory reset."
            )
            return

        cleanup_ip = None

        try:
            if not self.switch.is_reachable(ip):
                cleanup_ip = self.switch.derive_temporary_ip(ip)

                print(
                    f"[{name}] Device unreachable. "
                    f"Adding temporary IP {cleanup_ip}."
                )

                self.switch.add_temporary_vlan_ip(cleanup_ip)
                time.sleep(2)

                if not self.switch.is_reachable(ip):
                    raise RuntimeError(
                        "Device remained unreachable after recovery"
                    )

                print(f"[{name}] Reachability recovery successful.")

            self.reset_device(ip)
            lane.processed = True

            print(
                f"[{name}] Factory reset accepted. "
                "Waiting for sustained physical disconnect."
            )

        finally:
            if cleanup_ip:
                print(f"[{name}] Removing temporary IP {cleanup_ip}.")
                self.switch.remove_temporary_vlan_ip(cleanup_ip)

    def run_forever(self) -> None:
        poll_interval = self.config.watcher.poll_interval_seconds

        print(
            f"Starting watcher for {len(self.lanes)} enabled lane(s)."
        )

        for lane in self.lanes:
            print(
                f"- {lane.config.name}: port {lane.config.port}, "
                f"family {lane.config.device_family}, "
                f"expected speed {lane.config.expected_speed}"
            )

        while True:
            for lane in self.lanes:
                try:
                    self.process_lane(lane)
                except Exception as exc:
                    print(
                        f"[{lane.config.name}] Workflow failed: {exc}"
                    )

            time.sleep(poll_interval)
