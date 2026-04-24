import datetime as dt
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AppiumConfig:
    host: str
    port: int
    platform_name: str
    automation_name: str
    device_name: str
    app_package: str
    app_activity: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppiumConfig":
        return cls(
            host=data["host"],
            port=int(data["port"]),
            platform_name=data["platform_name"],
            automation_name=data["automation_name"],
            device_name=data["device_name"],
            app_package=data["app_package"],
            app_activity=data["app_activity"],
        )


@dataclass
class CollectorConfig:
    start_date: date
    data_folder: Path
    device_name: str
    appium: AppiumConfig

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CollectorConfig":
        raw_start_date = data.get("start_date")
        if raw_start_date is None:
            raise ValueError("Missing required collector config property 'start_date'")

        if isinstance(raw_start_date, date):
            parsed_start_date = raw_start_date
        elif isinstance(raw_start_date, str):
            parsed_start_date = date.fromisoformat(raw_start_date)
        else:
            raise ValueError("start_date must be a date string in ISO format (YYYY-MM-DD)")

        raw_data_folder = data.get("data_folder")
        if raw_data_folder is None:
            raise ValueError("Missing required collector config property 'data_folder'")

        raw_appium = data.get("appium")
        if raw_appium is None:
            raise ValueError("Missing required collector config property 'appium'")

        return cls(
            start_date=parsed_start_date,
            data_folder=Path(raw_data_folder),
            device_name=str(data.get("device_name")),
            appium=AppiumConfig.from_dict(raw_appium),
        )

    def get_date_range(self) -> tuple[dt.date, dt.date]:
        # Can't extract today as the day isn't over yet, so end on yesterday.
        end_date = dt.datetime.now().date() - dt.timedelta(days=1)

        return (self.start_date, end_date)


def load_collector_config(path: Path | str) -> CollectorConfig:
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Collector config file not found: {path_obj}")

    with path_obj.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError("Collector config YAML must be a mapping/object")

    return CollectorConfig.from_dict(raw)


__all__ = ["AppiumConfig", "CollectorConfig", "load_collector_config"]
