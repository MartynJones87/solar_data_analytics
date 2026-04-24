from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


def _ensure_tuple(value: Any, length: int, field_name: str) -> tuple[int, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{field_name} must be a list/tuple of {length} integers")
    if len(value) != length:
        raise ValueError(f"{field_name} must have exactly {length} items")
    try:
        converted = tuple(int(x) for x in value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} items must be integers") from exc
    return converted


def to_2d(value: Any, field_name: str) -> tuple[int, int]:
    t = _ensure_tuple(value, 2, field_name)
    assert len(t) == 2
    return (t[0], t[1])


def to_4d(value: Any, field_name: str) -> tuple[int, int, int, int]:
    t = _ensure_tuple(value, 4, field_name)
    assert len(t) == 4
    return (t[0], t[1], t[2], t[3])


@dataclass
class DeviceConfig:
    name: str
    screen_size: tuple[int, int]
    hamburger_menu_coordinates: tuple[int, int]
    energy_insights_menu_button_coordinates: tuple[int, int]
    date_bounding_box: tuple[int, int, int, int]
    chart_hour_touch_coordinates: dict[str, tuple[int, int]]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceConfig":
        if not isinstance(data, dict):
            raise ValueError("device entry must be a mapping")

        return cls(
            name=str(data["name"]),
            screen_size=to_2d(data["screen_size"], "screen_size"),
            hamburger_menu_coordinates=to_2d(data["hamburger_menu_coordinates"], "hamburger_menu_coordinates"),
            energy_insights_menu_button_coordinates=to_2d(
                data["energy_insights_menu_button_coordinates"], "energy_insights_menu_button_coordinates"
            ),
            date_bounding_box=to_4d(data["date_bounding_box"], "date_bounding_box"),
            chart_hour_touch_coordinates={
                str(k): to_2d(v, f"chart_hour_touch_coordinates[{k}]")
                for k, v in data.get("chart_hour_touch_coordinates", {}).items()
            },
        )


@dataclass
class DeviceConfigFile:
    devices: dict[str, DeviceConfig]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceConfigFile":
        if not isinstance(data, dict):
            raise ValueError("device config must be a mapping")
        devices_raw = data.get("devices")
        if devices_raw is None:
            raise ValueError("Missing required property 'devices'")
        if not isinstance(devices_raw, list):
            raise ValueError("devices must be a list")

        device_map: dict[str, DeviceConfig] = {}
        for entry in devices_raw:
            device = DeviceConfig.from_dict(entry)
            if device.name in device_map:
                raise ValueError(f"Duplicate device name '{device.name}' in device config")
            device_map[device.name] = device

        return cls(devices=device_map)


def load_device_config(path: Path | str) -> DeviceConfigFile:
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Device config file not found: {path_obj}")

    with path_obj.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError("Device config YAML must be a mapping/object")

    return DeviceConfigFile.from_dict(raw)
