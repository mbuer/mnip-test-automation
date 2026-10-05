import re
import time
import requests
import paramiko
import yaml

cfg = yaml.safe_load(open("config.yaml"))

SWITCH = cfg["switch"]["host"]
USER = cfg["switch"]["username"]
PASS = cfg["switch"]["password"]

PORT = "1/25"


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

    channel.send("terminal length 0\n")
    time.sleep(1)

    channel.send(
        f"show lldp interfaces ethernet {PORT} remote\n"
    )

    time.sleep(3)

    output = channel.recv(65535).decode()

    ssh.close()

    print(output)

    match = re.search(
        r"IPv4\s+(\d+\.\d+\.\d+\.\d+)",
        output
    )

    if match:
        return match.group(1)

    return None


def factory_reset(ip):
    url = f"http://{ip}/emsfp/node/v1/self/system"

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


while True:
    ip = get_lldp_ip()

    if ip:
        print(f"Found device: {ip}")

        factory_reset(ip)

        break

    print("Waiting for LLDP neighbor...")

    time.sleep(5)
