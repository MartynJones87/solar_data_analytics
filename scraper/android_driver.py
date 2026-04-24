import datetime as dt
import io
import logging
from typing import Any

import easyocr
import numpy as np
from appium.options.android import UiAutomator2Options
from appium.webdriver import WebElement
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from PIL import Image
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scraper.config.collector_config import AppiumConfig
from scraper.config.device_config import DeviceConfig
from scraper.utils import get_base_path, parse_date


class AndroidDriver:
    device_config: DeviceConfig
    appium_config: AppiumConfig
    custom_options: dict[str, Any] | None
    options: UiAutomator2Options
    web_driver: WebDriver
    wait: WebDriverWait
    reader: easyocr.Reader

    def __init__(
        self,
        device_config: DeviceConfig,
        appium_config: AppiumConfig,
        custom_options: dict[str, Any] | None = None,
    ):
        self.device_config = device_config
        self.appium_config = appium_config
        self.custom_options = custom_options
        self.options = self._get_options(custom_options)
        # Appium points to http://127.0.0.1:4723/wd/hub by default
        self.web_driver = WebDriver(
            command_executor=f"http://{appium_config.host}:{appium_config.port}",
            options=self.options,
        )
        self.wait = WebDriverWait(self.web_driver, timeout=10)
        # Setup the OCR Reader.
        self.reader = easyocr.Reader(["en"], gpu=False)

    def get_web_driver(self) -> WebDriver:
        return self.web_driver

    def wait_until_app_in_foreground(self) -> None:
        """
        Waits until the app specified in the appium config is in the foreground on the device.
        """
        self.wait.until(
            lambda _: self._is_app_in_foreground(),
            message=f"App {self.appium_config.app_package} did not come to foreground within timeout",
        )

    def take_screenshot(self, debug_output: bool = False) -> Image.Image:
        """
        Takes a screenshot of the current screen on the device and returns it as a PIL Image.

        Args:
            debug_output (bool): If True, saves the screenshot to disk for debugging purposes.

        Returns:
            Image.Image: The screenshot as a PIL Image.
        """
        screenshot_bytes = self.web_driver.get_screenshot_as_png()

        if debug_output:
            # Write png file to disk for debugging.
            base_path = get_base_path()
            screenshot_path = base_path / "screenshot.png"
            with open(screenshot_path, "wb") as f:
                f.write(screenshot_bytes)

        image = Image.open(io.BytesIO(screenshot_bytes))

        return image

    def login_to_app(self) -> None:
        """
        Logs into the app using the credentials specified in the device config.
        """
        if self.is_login_page_active():
            logging.info("Not logged in, logging in now...")

            login_button = self._get_login_button()
            login_button.click()

        logging.info("We're logged in.")

    def load_energy_insights_page(self) -> None:
        """
        Navigates to the Energy Insights page in the app.
        Assumes that we're already logged in and on the home page.
        """
        if self.is_energy_insights_page_active():
            logging.info("Already on Energy Insights page.")
            return

        self.open_hamburger_menu()

        self.click_energy_insights_in_menu()

        self.wait.until(
            lambda _: self.is_energy_insights_page_active(),
            message="Failed to navigate to Energy Insights page",
        )

        logging.info("Energy Insights page is active.")

    def open_hamburger_menu(self) -> None:
        logging.info("Opening hamburger menu...")
        self.web_driver.tap([self.device_config.hamburger_menu_coordinates])

        # Wait for the 'Legal' button to appear (indicating the menu is open).
        logging.info("Waiting for hamburger menu to open...")
        self.wait.until(
            lambda _: self.is_menu_open(),
            message="Failed to open hamburger menu",
        )

        logging.info("Hamburger menu is open")

    def click_energy_insights_in_menu(self) -> None:
        logging.info("In hamburger menu, click on Engergy Insights.")
        self.web_driver.tap([self.device_config.energy_insights_menu_button_coordinates])

    def get_current_date(self) -> dt.date:
        screenshot = self.take_screenshot(True)
        date_img = screenshot.crop(self.device_config.date_bounding_box)
        text = self._ocr_text(date_img)
        return parse_date(text)

    def _get_login_button(self):
        login_selector = (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().text("LOG IN")',
        )
        return self.wait.until(
            EC.presence_of_element_located(login_selector),
            message="Login button not found on Login page",
        )

    def _is_app_in_foreground(self) -> bool:
        """
        Checks if the app specified in the appium config is currently in the foreground on the device.

        Returns:
            bool: True if the app is in the foreground, False otherwise.
        """
        return self.web_driver.current_package == self.appium_config.app_package

    def is_login_page_active(self) -> bool:
        """
        Check if we're on the Login page by looking for a unique element on that page.
        Returns:
            - bool: True if on Login page, False otherwise.
        """
        login_selector = (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().text("LOG IN")',
        )
        return self._is_element_active_on_page(login_selector)

    def is_energy_insights_page_active(self) -> bool:
        """
        Check if we're on the Energy Insights page by looking for a unique element on that page.
        Returns:
            - bool: True if on Energy Insights page, False otherwise.
        """
        insights_selector = (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().text("Energy Insights")',
        )
        return self._is_element_active_on_page(insights_selector)

    def is_menu_open(self) -> bool:
        """
        Check if the hamburger menu is open by looking for a unique element in the menu (e.g. "Energy Insights" text).

        Returns:
            bool: True if the menu is open, False otherwise.
        """
        menu_item_selector = (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().text("Legal")',
        )
        return self._is_element_active_on_page(menu_item_selector)

    def click_next_day(self):
        next_day_arrow_selector = (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("com.horcrux.svg.SvgView").instance(5)',
        )

        next_day_arrow_element = self.wait.until(
            EC.presence_of_element_located(next_day_arrow_selector),
        )

        next_day_arrow_element.click()

    def click_previous_day(self):
        previous_day_arrow_selector = (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("com.horcrux.svg.SvgView").instance(3)',
        )

        previous_day_arrow_element = self.wait.until(
            EC.presence_of_element_located(previous_day_arrow_selector),
        )

        previous_day_arrow_element.click()

    def wait_until_date_changes(self, current_date: dt.date) -> None:
        self.wait.until(
            lambda d: self.get_current_date() != current_date,
            message=f"Date did not update after clicking next arrow. Current date: {current_date}",
        )

    def tap(self, coordinates: tuple[int, int]) -> None:
        self.web_driver.tap([coordinates])

    def get_hour_tooltip_element(self, hour: str) -> WebElement:
        self._wait_until_hour_tooltip_appears(hour)

        tooltip_selector = '//android.view.ViewGroup[@content-desc="Energy insights area chart"]/android.view.ViewGroup'
        tooltip_hour_element = self.web_driver.find_element(
            AppiumBy.XPATH,
            tooltip_selector,
        )

        return tooltip_hour_element

    def read_hour_tooltip_data(self, tooltip_element: WebElement) -> dict[str, str | None]:
        hour_readings: dict[str, str | None] = {
            "hour": None,
            "grid": None,
            "solar": None,
            "battery": None,
            "home": None,
        }

        reading_text_elements = [
            e.text
            for e in tooltip_element.find_elements(AppiumBy.XPATH, ".//android.widget.TextView")
            if e.get_attribute("class") == "android.widget.TextView"
        ]

        label_mappings: dict[str, str] = {
            "Grd": "grid",
            "Sol": "solar",
            "Bat": "battery",
            "Hom": "home",
        }
        # Need to parse these into the hour_readings dict.
        current_label = "hour"
        for text in reading_text_elements:
            if text.endswith(" : "):
                current_label = label_mappings.get(text[:-3], text[:-3].lower())
            elif current_label:
                hour_readings[current_label] = text

        return hour_readings

    def _wait_until_hour_tooltip_appears(self, hour: str) -> None:
        hour_selector = (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{hour}")',
        )

        self.wait.until(EC.presence_of_element_located(hour_selector))

    def _is_element_active_on_page(self, selector: tuple[str, str]) -> bool:
        """
        Check if we're on the page by looking for a unique element on that page.

        Returns True if we're on the page, False otherwise.

        Args:
            - selector (tuple[str, str]): The selector for the unique element on the page.

        Returns:
            - bool: True if on the page, False otherwise.
        """
        visible_elements = self.web_driver.find_elements(*selector)
        on_page = any((el.is_displayed() for el in visible_elements))
        return on_page

    def _get_options(self, custom_options: dict[str, Any] | None = None) -> UiAutomator2Options:
        options = UiAutomator2Options()
        options.platform_name = self.appium_config.platform_name
        options.automation_name = self.appium_config.automation_name
        options.device_name = self.appium_config.device_name
        options.app_package = self.appium_config.app_package
        options.app_activity = self.appium_config.app_activity
        options.no_reset = True

        if custom_options is not None:
            options.load_capabilities(custom_options)

        return options

    def _ocr_text(self, img: Image.Image) -> str:
        result = self.reader.readtext(np.array(img), detail=0)
        return " ".join(result)
