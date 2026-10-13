import requests


RESET_PATH = "/emsfp/node/v1/self/system"
RESET_PAYLOAD = {
    "config_reset": "system",
}


def factory_reset(ip: str, timeout_seconds: int = 10) -> requests.Response:
    url = "http" + "://" + ip + RESET_PATH

    response = requests.put(
        url,
        json=RESET_PAYLOAD,
        timeout=timeout_seconds,
    )

    response.raise_for_status()
    return response
