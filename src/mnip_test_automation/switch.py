import re
import time
from ipaddress import IPv4Address

import paramiko

from mnip_test_automation.config import NetworkConfig, SwitchConfig


class OnyxSwitch:
    def __init__(
        self,
        switch_config: SwitchConfig,
        network_config: NetworkConfig,
    ):
        self.switch_config = switch_config
        self.network_config = network_config

    def _connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(
            self.switch_config.host,
            username=self.switch_config.username,
            password=self.switch_config.password,
            look_for_keys=False,
            allow_agent=False,
        )

        return ssh

    def run_commands(
        self,
        commands: list[str],
        command_delay_seconds: float = 1,
    ) -> str:
        ssh = self._connect()

        try:
            channel = ssh.invoke_shell()
            time.sleep(2)

            for command in commands:
                print(f"CMD> {command}")
                channel.send(command + "\n")
                time.sleep(command_delay_seconds)

            output = channel.recv(65535).decode()
            print(output)
            return output

        finally:
            ssh.close()

    def port_is_up(self, port: str) -> bool:
        output = self.run_commands([
            f"show interfaces ethernet {port}"
        ])

        return re.search(
            r"Operational state\s*:\s*Up",
            output,
        ) is not None

    def get_lldp_ip(self, port: str) -> str | None:
        output = self.run_commands([
            "terminal length 999",
            f"show lldp interfaces ethernet {port} remote",
        ])

        match = re.search(
            r"IPv4\s+(\d+\.\d+\.\d+\.\d+)",
            output,
        )

        return match.group(1) if match else None

    def is_reachable(self, ip: str) -> bool:
        ssh = self._connect()

        try:
            channel = ssh.invoke_shell()
            time.sleep(2)

            channel.send(f"ping {ip}\n")
            time.sleep(3)
            channel.send("\x03")
            time.sleep(1)

            output = channel.recv(65535).decode()
            print(output)

            return (
                "packet loss" in output
                and "100% packet loss" not in output
            )

        finally:
            ssh.close()

    def derive_temporary_ip(self, device_ip: str) -> str:
        address = IPv4Address(device_ip)
        octets = str(address).split(".")
        host = int(octets[3])

        if host == 254:
            host -= 1
        else:
            host += 1

        octets[3] = str(host)
        return ".".join(octets)

    def add_temporary_vlan_ip(self, temporary_ip: str) -> None:
        vlan = self.network_config.vlan
        prefix = self.network_config.temporary_prefix_length

        self.run_commands([
            "enable",
            "configure terminal",
            f"interface vlan {vlan}",
            f"ip address {temporary_ip}/{prefix}",
        ])

    def remove_temporary_vlan_ip(self, temporary_ip: str) -> None:
        vlan = self.network_config.vlan
        prefix = self.network_config.temporary_prefix_length

        self.run_commands([
            "enable",
            "configure terminal",
            f"interface vlan {vlan}",
            f"no ip address {temporary_ip}/{prefix}",
        ])
