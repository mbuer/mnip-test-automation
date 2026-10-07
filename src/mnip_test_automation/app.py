import re
import time
import requests
import paramiko
import yaml
import subprocess
from ipaddress import IPv4Address

cfg = yaml.safe_load(open("config.yaml"))

SWITCH = cfg["switch"]["host"]
USER = cfg["switch"]["username"]
PASS = cfg["switch"]["password"]

PORT = "1/25"

def reachable(ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        SWITCH,
        username=USER,
        password=PASS,
        look_for_keys=False,
        allow_agent=False,
    )

    channel = ssh.invoke_shell()
    time.sleep(2)

    channel.send(f"ping {ip}\n")
    time.sleep(3)
    channel.send("\x03")
    time.sleep(1)

    output = channel.recv(65535).decode()
    print(output)
    ssh.close()

    print(output)

    return "packet loss" in output and "100% packet loss" not in output


def derive_temporary_ip(device_ip):
    ip = IPv4Address(device_ip)

    octets = str(ip).split(".")
    host = int(octets[3])

    if host == 254:
        host -= 1
    else:
        host += 1

    octets[3] = str(host)

    return ".".join(octets)

def port_is_up():
    output = run_switch_commands([
        f"show interfaces ethernet {PORT}"
    ])

    return re.search(
        r"Operational state\s*:\s*Up",
        output
    ) is not None


def get_lldp_ip():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        SWITCH,
        username=USER,
        password=PASS,
        look_for_keys=False,
        allow_agent=False,
    )

    channel = ssh.invoke_shell()

    time.sleep(2)

    channel.send("terminal length 999\n")
    time.sleep(1)

    channel.send(
        f"show lldp interfaces ethernet {PORT} remote\n"
    )

    time.sleep(3)

    output = channel.recv(65535).decode()

    print(output)
    ssh.close()

    print(output)

    match = re.search(
        r"IPv4\s+(\d+\.\d+\.\d+\.\d+)",
        output
    )

    if match:
        return match.group(1)

    return None





def run_switch_commands(commands):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        SWITCH,
        username=USER,
        password=PASS,
        look_for_keys=False,
        allow_agent=False,
    )

    channel = ssh.invoke_shell()

    time.sleep(2)

    for cmd in commands:
        print(f"CMD> {cmd}")
        channel.send(cmd + "\n")
        time.sleep(1)

    output = channel.recv(65535).decode()

    print(output)
    ssh.close()

    return output


def add_temporary_vlan_ip(temp_ip):
    run_switch_commands([
        "enable",
        "configure terminal",
        "interface vlan 1",
        f"ip address {temp_ip}/24",
    ])


def remove_temporary_vlan_ip(temp_ip):
    run_switch_commands([
        "enable",
        "configure terminal",
        "interface vlan 1",
        f"no ip address {temp_ip}/24",
    ])

def factory_reset(ip):
    url = "http" + "://" + ip + "/emsfp/node/v1/self/system"

    payload = {
        "config_reset": "system"
    }

    response = requests.put(
        url,
        json=payload,
        timeout=10
    )

    print(f"HTTP {response.status_code}")
    print(response.text)


processed = False
down_since = None

while True:
    if not port_is_up():
        if down_since is None:
            down_since = time.monotonic()
            print("Port is down. Starting removal timer.")

        down_seconds = time.monotonic() - down_since

        if processed and down_seconds >= 60:
            print("Port remained down for 60 seconds. Re-arming port.")
            processed = False

        time.sleep(10)
        continue

    down_since = None

    if processed:
        print("Port already processed. Waiting for disconnect.")
        time.sleep(10)
        continue

    ip = get_lldp_ip()

    if not ip:
        print("Port is up. Waiting for LLDP neighbor...")
        time.sleep(10)
        continue

    print(f"Found device: {ip}")
    cleanup_ip = None

    try:
        if not reachable(ip):
            print("Device not reachable")

            cleanup_ip = derive_temporary_ip(ip)
            print(f"Adding temporary IP: {cleanup_ip}")

            add_temporary_vlan_ip(cleanup_ip)
            time.sleep(2)

            if not reachable(ip):
                print("Recovery failed")
                time.sleep(10)
                continue

            print("Recovery successful")

        factory_reset(ip)
        processed = True
        print("Reset complete. Waiting for physical disconnect.")

    except Exception as exc:
        print(f"Workflow failed: {exc}")
        time.sleep(10)

    finally:
        if cleanup_ip:
            print(f"Removing temporary IP: {cleanup_ip}")
            remove_temporary_vlan_ip(cleanup_ip)

    time.sleep(10)

