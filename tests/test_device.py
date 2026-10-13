from unittest.mock import Mock, patch

from mnip_test_automation.device import (
    RESET_PATH,
    RESET_PAYLOAD,
    factory_reset,
)


@patch("mnip_test_automation.device.requests.put")
def test_factory_reset_uses_exact_narrow_request(mock_put):
    response = Mock()
    mock_put.return_value = response

    result = factory_reset("10.10.10.10")

    mock_put.assert_called_once_with(
        "http://10.10.10.10" + RESET_PATH,
        json={"config_reset": "system"},
        timeout=10,
    )

    response.raise_for_status.assert_called_once_with()
    assert result is response
    assert RESET_PAYLOAD == {"config_reset": "system"}
