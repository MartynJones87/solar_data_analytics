import datetime as dt
import io
import logging

import easyocr

from scraper.android_driver import AndroidDriver
from scraper.config.device_config import DeviceConfig


class DataCollector:
    android_driver: AndroidDriver
    device_config: DeviceConfig
    reader: easyocr.Reader

    def __init__(self, android_driver: AndroidDriver, device_config: DeviceConfig):
        self.android_driver = android_driver
        self.device_config = device_config

    def navigate_to_date(self, target_date: dt.date) -> None:
        logging.info(f"Navigate to: {target_date}")
        current_date = self.android_driver.get_current_date()
        logging.info(f"Current Date: {current_date}")
        while current_date != target_date:
            if current_date > target_date:
                logging.info("Current Date after Target Date, Navigate Backwards")
                current_date = self._navigate_day_backwards(current_date)
            elif current_date < target_date:
                logging.info("Current Date before Target Date, Navigate Forwards")
                current_date = self._navigate_day_forwards(current_date)
        logging.info(f"Reached Target Date: {current_date}")

    def scrape_date(self, date_to_scrape: dt.date) -> list[tuple[dict[str, str | None], io.BytesIO | None]]:
        # Return data structure is a list (of hours), with a tuple of a dictionary of the hours' data and a stream of
        # the screenshot of the tooltip.
        date_data: list[tuple[dict[str, str | None], io.BytesIO | None]] = []

        # Iterate through chart hours, tap, and extract tooltip text + values.
        for hour, coords in self.device_config.chart_hour_touch_coordinates.items():
            retry_count = 0
            max_retries = 3

            while retry_count < max_retries:
                try:
                    # Tooltips are not loaded and hidden by default, so need to tap each hour to load the tooltip,
                    # then extract the text from the tooltip.
                    logging.info("Tapping hour %s at coords %s", hour, coords)
                    self.android_driver.tap(coords)

                    tooltip_hour_element = self.android_driver.get_hour_tooltip_element(hour)

                    hour_readings: dict[str, str | None] = self.android_driver.read_hour_tooltip_data(
                        tooltip_hour_element
                    )

                    hour_data = (
                        {"date": date_to_scrape.strftime("%Y-%m-%d"), **hour_readings},
                        io.BytesIO(tooltip_hour_element.screenshot_as_png),
                    )
                    date_data.append(hour_data)

                    print(f"Hour {hour} readings:", hour_readings)
                    break  # Break out of the retry loop if successful.
                except Exception as e:
                    logging.warning(f"Failed to read tooltip for hour {hour} on attempt {retry_count + 1}: {e}")
                    retry_count += 1
                    if retry_count == max_retries:
                        logging.error(f"Max retries reached for hour {hour}, moving on to next hour.")
                        date_data.append(
                            (
                                {
                                    "date": date_to_scrape.strftime("%Y-%m-%d"),
                                    "hour": hour,
                                    "grid": None,
                                    "solar": None,
                                    "battery": None,
                                    "home": None,
                                },
                                None,
                            )
                        )
        return date_data

    def _navigate_day_backwards(self, current_date: dt.date) -> dt.date:
        self.android_driver.click_previous_day()
        self.android_driver.wait_until_date_changes(current_date)
        return self.android_driver.get_current_date()

    def _navigate_day_forwards(self, current_date: dt.date) -> dt.date:
        self.android_driver.click_next_day()
        self.android_driver.wait_until_date_changes(current_date)
        return self.android_driver.get_current_date()

    def _save_tooltip_screenshot(self, tooltip_hour_element, date_to_scrape, hour) -> None:
        pass
