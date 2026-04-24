import logging
import sys
import time

import typer

from scraper.android_driver import AndroidDriver
from scraper.config.collector_config import load_collector_config
from scraper.config.device_config import load_device_config
from scraper.data_collector import DataCollector
from scraper.data_manager import DataManager

# Configure logging to stdout so logging.info() writes to console
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


app = typer.Typer()


@app.command()
def collect_data():
    logging.info("Starting data collection...")
    cfg = load_collector_config("config/collector_config.yaml")
    dev_cfg = load_device_config("config/device_config.yaml").devices[cfg.device_name]

    android_driver = AndroidDriver(
        device_config=dev_cfg,
        appium_config=cfg.appium,
    )
    data_manager = DataManager(cfg)
    data_collector = DataCollector(android_driver, dev_cfg)

    logging.info("Waiting for app to be in foreground...")
    android_driver.wait_until_app_in_foreground()
    logging.info("App is in foreground, starting data collection loop...")

    # Small buffer for UI rendering
    time.sleep(5)

    android_driver.login_to_app()

    android_driver.load_energy_insights_page()

    dates_to_scrape = data_manager.find_dates_to_scrape()
    logging.info(f"Dates to Scrape: {dates_to_scrape}")

    while dates_to_scrape:
        # Get the latest date to scrape. Because by default, the Energy Insights
        # page starts on the current date, it makes most sense to move to the latest
        # date, scrape that and then navigate backwards to get any other dates.
        max_date_to_scrape = max(dates_to_scrape)
        data_collector.navigate_to_date(max_date_to_scrape)

        hours_data = data_collector.scrape_date(max_date_to_scrape)
        data_manager.save_date_data(max_date_to_scrape, hours_data)
        logging.info(f"Removing scraped date from list: {max_date_to_scrape}")
        dates_to_scrape.remove(max_date_to_scrape)

        logging.info(f"Remaining Dates to Scrape: {dates_to_scrape}")

    # data_manager.consolidate_into_parquet()
    data_manager.consolidate_into_csv()


@app.command()
def consolidate_json():
    logging.info("Starting data consolidation...")
    cfg = load_collector_config("config/collector_config.yaml")

    data_manager = DataManager(cfg)
    # data_manager.consolidate_into_parquet()
    data_manager.consolidate_into_csv()


@app.command()
def consolidate_duckdb():
    logging.info("Starting data consolidation into DuckDB...")
    cfg = load_collector_config("config/collector_config.yaml")

    data_manager = DataManager(cfg)
    data_manager.consolidate_into_duckdb()


if __name__ == "__main__":
    app()
