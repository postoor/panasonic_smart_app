"""Tests for Panasonic clothes dryer sensor decoding."""

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock


PACKAGE_PARENT = Path(__file__).parents[1] / "custom_components"
if str(PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT))

from panasonic_smart_app import sensor  # noqa: E402
from panasonic_smart_app.const import (  # noqa: E402
    DEVICE_TYPE_CLOTHES_DRYER,
    DEVICE_STATUS_CODES,
)


# Command list for the dryer (ModelType "CN-HP"), as returned by the real API.
DRYER_COMMANDS = [
    {
        "CommandType": "0x55",
        "Parameters": [["棉麻行程", 0], ["大件行程", 13], ["快烘行程", 76]],
    },
    {
        "CommandType": "0x50",
        "Parameters": [
            ["不顯示", 0],
            ["待機中", 1],
            ["動作中", 2],
            ["預約中", 3],
            ["終了", 5],
            ["異常", 8],
        ],
    },
    {"CommandType": "0x05", "Parameters": [["Min", 0], ["Max", 599]]},
]


def make_sensor(sensor_cls, status):
    """Build a dryer sensor backed by a fake coordinator / client."""
    device = {
        "NickName": "烘隆隆",
        "Model": "NH-VS100HP",
        "ModelType": "CN-HP",
        "DeviceType": "6",
        "Auth": "AUTH",
    }
    coordinator = MagicMock()
    coordinator.data = [{**device, "status": status}]
    client = MagicMock()
    client.get_commands.return_value = [
        {"ModelType": "CN-HP", "JSON": [{"list": DRYER_COMMANDS}]}
    ]
    return sensor_cls(coordinator, 0, client, device)


class DryerSensorTest(unittest.TestCase):
    def test_device_status_codes_registered(self) -> None:
        self.assertIn(DEVICE_TYPE_CLOTHES_DRYER, DEVICE_STATUS_CODES)
        self.assertEqual(
            DEVICE_STATUS_CODES[DEVICE_TYPE_CLOTHES_DRYER],
            ["0x05", "0x15", "0x50", "0x55"],
        )

    def test_countdown_reports_remaining_minutes(self) -> None:
        s = make_sensor(sensor.PanasonicDryerCountdownSensor, {"0x05": "3"})
        self.assertEqual(s.state, "3")

    def test_countdown_unavailable_without_value(self) -> None:
        s = make_sensor(sensor.PanasonicDryerCountdownSensor, {})
        self.assertEqual(s.state, sensor.STATE_UNAVAILABLE)

    def test_status_maps_running(self) -> None:
        s = make_sensor(sensor.PanasonicDryerStatusSensor, {"0x50": "2"})
        self.assertEqual(s.state, "動作中")

    def test_status_maps_idle_zero(self) -> None:
        s = make_sensor(sensor.PanasonicDryerStatusSensor, {"0x50": "0"})
        self.assertEqual(s.state, "不顯示")

    def test_status_unknown_code_is_unavailable(self) -> None:
        s = make_sensor(sensor.PanasonicDryerStatusSensor, {"0x50": "99"})
        self.assertEqual(s.state, sensor.STATE_UNAVAILABLE)

    def test_cycle_maps_program(self) -> None:
        s = make_sensor(sensor.PanasonicDryerCycleSensor, {"0x55": "0"})
        self.assertEqual(s.state, "棉麻行程")

    def test_cycle_unknown_code_is_unavailable(self) -> None:
        s = make_sensor(sensor.PanasonicDryerCycleSensor, {"0x55": "999"})
        self.assertEqual(s.state, sensor.STATE_UNAVAILABLE)


if __name__ == "__main__":
    unittest.main()
