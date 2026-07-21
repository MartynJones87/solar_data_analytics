import datetime as dt
import io
import json
import logging
from pathlib import Path

import duckdb

# import pyarrow as pa
# import pyarrow.parquet as pq
from scraper.config.collector_config import CollectorConfig
from scraper.utils import get_base_path


class DataManager:
    collector_config: CollectorConfig
    solar_data_folder: Path

    def __init__(self, collector_config: CollectorConfig):
        self.collector_config = collector_config
        data_folder_path = self._get_data_folder_path()

        self.solar_data_folder = data_folder_path / "solar_data"
        self.solar_data_folder.mkdir(exist_ok=True, parents=True)

    def find_dates_to_scrape(self) -> list[dt.date]:
        dates_to_scrape = []

        start_date, end_date = self.collector_config.get_date_range()

        # For each day from START_DATE to END_DATE inclusive, check if a folder exists for that day within the solar_data folder:
        for single_date in (start_date + dt.timedelta(n) for n in range((end_date - start_date).days + 1)):
            years_folder = self.solar_data_folder / str(single_date.year)
            if not years_folder.exists():
                years_folder.mkdir()
                logging.info(f"Created folder for year {single_date.year}: {years_folder}")

            month_folder = years_folder / f"{single_date.month:02d}"
            if not month_folder.exists():
                month_folder.mkdir()
                logging.info(f"Created folder for month {single_date.month:02d}: {month_folder}")

            day_folder = month_folder / f"{single_date.day:02d}"
            if not day_folder.exists():
                day_folder.mkdir()
                logging.info(f"Created folder for day {single_date.day:02d}: {day_folder}")

            # Now we have a folder for this date at solar_data/YYYY/MM/DD. We can check if the data for this date has
            # already been scraped by checking if there is a JSON file in this folder. If there is, we can skip scraping
            # this date. If there isn't, we can add this date to the list of dates to scrape.
            json_file = day_folder / f"{single_date.strftime('%Y-%m-%d')}_data.json"
            if not json_file.exists():
                logging.info(f"No data file for date {single_date}, adding to scrape list.")
                dates_to_scrape.append(single_date)

        return dates_to_scrape

    def save_date_data(self, date: dt.date, hours_data: list[tuple[dict[str, str | None], io.BytesIO | None]]) -> None:
        # Save the hour_reading dict[str, str] to a JSON file for this date.

        json_data = [d[0] for d in hours_data]
        day_folder = self.solar_data_folder / f"{date.year}/{date.month:02d}/{date.day:02d}"
        day_folder.mkdir(parents=True, exist_ok=True)
        with open(day_folder / f"{date.strftime('%Y-%m-%d')}_data.json", "x") as f:
            json.dump(json_data, f, indent=4)

        for hour_data, png_stream in hours_data:
            if png_stream:
                hour = hour_data["hour"]
                if hour is None:
                    raise ValueError("Hour cannot be None")
                self._save_tooltip_screenshot(day_folder, date, hour, png_stream)

    # def consolidate_into_parquet(self) -> None:
    #     parquet_path = self.solar_data_folder / "solar_data.snappy.parquet"

    #     json_files = sorted(self.solar_data_folder.rglob("*_data.json"))
    #     if not json_files:
    #         logging.info("No solar JSON data files found; skipping Parquet consolidation.")
    #         return

    #     rows: list[dict[str, object | None]] = []

    #     for file_path in json_files:
    #         try:
    #             with file_path.open("r", encoding="utf-8") as f:
    #                 payload = json.load(f)
    #         except json.JSONDecodeError as e:
    #             logging.warning("Skipping malformed JSON %s: %s", file_path, e)
    #             continue

    #         if not isinstance(payload, list):
    #             logging.warning("Skipping JSON file with unexpected top-level type (not list): %s", file_path)
    #             continue

    #         for entry in payload:
    #             if not isinstance(entry, dict):
    #                 logging.warning("Skipping non-object entry in %s", file_path)
    #                 continue

    #             row: dict[str, object | None] = {}

    #             # date -> date
    #             date_raw = entry.get("date")
    #             if isinstance(date_raw, str) and date_raw:
    #                 try:
    #                     row["date"] = dt.date.fromisoformat(date_raw)
    #                 except ValueError:
    #                     logging.warning("Invalid date value %s in %s", date_raw, file_path)
    #                     row["date"] = None
    #             else:
    #                 row["date"] = None

    #             # hour -> timestamp (1970-01-01 HH:MM)
    #             hour_raw = entry.get("hour")
    #             if isinstance(hour_raw, str) and hour_raw:
    #                 try:
    #                     parsed_time = dt.datetime.strptime(hour_raw, "%H:%M").time()
    #                     row["hour"] = dt.datetime.combine(dt.date(1970, 1, 1), parsed_time)
    #                 except ValueError:
    #                     logging.warning("Invalid hour value %s in %s", hour_raw, file_path)
    #                     row["hour"] = None
    #             else:
    #                 row["hour"] = None

    #             def parsed_float(value: object | None) -> float | None:
    #                 if value is None:
    #                     return None
    #                 if isinstance(value, (float, int)):
    #                     return float(value)
    #                 if isinstance(value, str) and value.strip() != "":
    #                     try:
    #                         return float(value)
    #                     except ValueError:
    #                         return None
    #                 return None

    #             row["grid"] = parsed_float(entry.get("grid"))
    #             row["solar"] = parsed_float(entry.get("solar"))
    #             row["battery"] = parsed_float(entry.get("battery"))
    #             row["home"] = parsed_float(entry.get("home"))

    #             rows.append(row)

    #     if not rows:
    #         logging.info("No valid rows to write to Parquet after scanning JSON files.")
    #         return

    #     schema = pa.schema(
    #         [
    #             pa.field("date", pa.date32()),
    #             pa.field("hour", pa.timestamp("s")),
    #             pa.field("grid", pa.float64()),
    #             pa.field("solar", pa.float64()),
    #             pa.field("battery", pa.float64()),
    #             pa.field("home", pa.float64()),
    #         ]
    #     )

    #     table = pa.Table.from_pylist(rows, schema=schema)

    #     pq.write_table(table, parquet_path, compression="snappy")

    #     logging.info("Wrote parquet (%s rows) to %s", table.num_rows, parquet_path)

    def consolidate_into_csv(self) -> None:
        csv_path = self.solar_data_folder / "solar_data.csv"

        json_files = sorted(self.solar_data_folder.rglob("*_data.json"))
        if not json_files:
            logging.info("No solar JSON data files found; skipping CSV consolidation.")
            return

        rows: list[dict[str, object | None]] = []

        for file_path in json_files:
            try:
                with file_path.open("r", encoding="utf-8") as f:
                    payload = json.load(f)
            except json.JSONDecodeError as e:
                logging.warning("Skipping malformed JSON %s: %s", file_path, e)
                continue

            if not isinstance(payload, list):
                logging.warning("Skipping JSON file with unexpected top-level type (not list): %s", file_path)
                continue

            for entry in payload:
                if not isinstance(entry, dict):
                    logging.warning("Skipping non-object entry in %s", file_path)
                    continue

                row: dict[str, object | None] = {}

                # date -> date
                date_raw = entry.get("date")
                if isinstance(date_raw, str) and date_raw:
                    try:
                        row["date"] = dt.date.fromisoformat(date_raw)
                    except ValueError:
                        logging.warning("Invalid date value %s in %s", date_raw, file_path)
                        row["date"] = None
                else:
                    row["date"] = None

                # hour -> timestamp (1970-01-01 HH:MM)
                hour_raw = entry.get("hour")
                if isinstance(hour_raw, str) and hour_raw:
                    try:
                        parsed_time = dt.datetime.strptime(hour_raw, "%H:%M").time()
                        row["hour"] = dt.datetime.combine(dt.date(1970, 1, 1), parsed_time)
                    except ValueError:
                        logging.warning("Invalid hour value %s in %s", hour_raw, file_path)
                        row["hour"] = None
                else:
                    row["hour"] = None

                def parsed_float(value: object | None) -> float | None:
                    if value is None:
                        return None
                    if isinstance(value, (float, int)):
                        return float(value)
                    if isinstance(value, str) and value.strip() != "":
                        try:
                            return float(value)
                        except ValueError:
                            return None
                    return None

                row["grid"] = parsed_float(entry.get("grid"))
                row["solar"] = parsed_float(entry.get("solar"))
                row["battery"] = parsed_float(entry.get("battery"))
                row["home"] = parsed_float(entry.get("home"))

                rows.append(row)

        if not rows:
            logging.info("No valid rows to write to Parquet after scanning JSON files.")
            return

        # Write the contents of rows to a CSV file with a header row. The columns should be date, hour, grid, solar, battery, home. The date should be in ISO format (YYYY-MM-DD) and the hour should be in HH:MM format.
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            f.write("date,hour,grid,solar,battery,home\n")
            for row in rows:
                date_str = row["date"].isoformat() if row["date"] else ""
                hour_str = row["hour"].strftime("%H:%M") if row["hour"] else ""
                grid_str = str(row["grid"]) if row["grid"] is not None else ""
                solar_str = str(row["solar"]) if row["solar"] is not None else ""
                battery_str = str(row["battery"]) if row["battery"] is not None else ""
                home_str = str(row["home"]) if row["home"] is not None else ""

                f.write(f"{date_str},{hour_str},{grid_str},{solar_str},{battery_str},{home_str}\n")

        logging.info("Wrote CSV (%s rows) to %s", len(rows), csv_path)

    def consolidate_into_duckdb(self) -> None:
        data_folder_path = get_base_path() / self.collector_config.data_folder
        # Connect to (or create) a local DuckDB file
        with duckdb.connect(f"{data_folder_path}/solar_data.duckdb") as con:
            # Drop the raw_solar_data table if it already exists to ensure we start fresh each time we run this consolidation step.
            con.execute("DROP TABLE IF EXISTS raw_solar_data")
            # Load Inventory Data (JSON)
            con.execute(f"""
                CREATE TABLE IF NOT EXISTS raw_solar_data AS 
                SELECT * FROM read_json_auto('{data_folder_path}/solar_data/**/*.json')
            """)

            print("Successfully loaded raw data into DuckDB!")
            con.close()

    def _get_data_folder_path(self) -> Path:
        base_path = get_base_path()
        data_folder_path = base_path / self.collector_config.data_folder
        return data_folder_path

    def _save_tooltip_screenshot(
        self,
        day_folder: Path,
        date: dt.date,
        hour: str,
        png_stream: io.BytesIO,
    ) -> None:
        screenshot_file_path = day_folder / f"tooltip_{date.strftime('%Y-%m-%d')}_{hour.replace(':', '')}.png"
        png_stream.seek(0)
        with open(screenshot_file_path, "xb") as f:
            f.write(png_stream.read())
