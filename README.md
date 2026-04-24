# Solar Data Analytics

A comprehensive dashboard project for analyzing domestic solar panel and battery storage data. The system scrapes raw data from the Duracell Energy Android app, processes it through a dbt-powered data warehouse using DuckDB, and presents analytics via a Streamlit dashboard.

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────-┐
│  Duracell       │     │   Scraper       │     │   Data Warehouse │
│  Energy App     │────▶│   (Python CLI)  │────▶│   (dbt/DuckDB)  │
│  (Android)      │     │                 │     │                  │
└─────────────────┘     └─────────────────┘     └────────┬────────-┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   Dashboard     │
                                                │   (Streamlit)   │
                                                └─────────────────┘
```

## Project Structure

```
solar_data_analytics/
├── main.py                    # CLI entry point for scraper commands
├── streamlit.py               # Streamlit dashboard entry point
├── pyproject.toml             # Python project dependencies
├── config/                    # Configuration files
│   ├── collector_config.yaml  # Scraper configuration
│   └── device_config.yaml     # Android device configuration
├── scraper/                   # Data collection from Duracell Energy app
│   ├── android_driver.py      # Appium WebDriver wrapper
│   ├── data_collector.py      # Data extraction logic
│   ├── data_manager.py        # Data storage and consolidation
│   ├── utils.py               # Utility functions
│   └── config/                # Configuration loaders
├── data_warehouse/            # dbt project for data transformation
│   ├── dbt_project.yml        # dbt project configuration
│   ├── models/                # dbt models (staging, intermediate, marts)
│   ├── seeds/                 # Static reference data
│   ├── macros/                # dbt macros
│   └── snapshots/             # dbt snapshots
├── dashboard/                 # Streamlit dashboard
│   ├── pages/                 # Dashboard pages
│   └── utils/                 # Database utilities
└── data/                      # Data storage
    ├── solar_data.duckdb      # DuckDB database
    └── solar_data/            # Raw scraped JSON data
```

---

## 1. Scraper

The scraper is a Python CLI application that uses [Appium](https://appium.io/) to automate an Android device running the [Duracell Energy](https://duracellenergy.com/en/products/duracell-energy-app/) app. It extracts hourly solar generation, battery storage, grid usage, and home consumption data.

### Prerequisites

- **Node.js & npm** - Required for Appium
- **Appium** - Mobile automation framework
  ```bash
  npm install -g appium
  ```
- **Appium UiAutomator2 Driver** - Android automation driver
  ```bash
  appium install driver uiautomator2
  ```
- **Android SDK** - For device debugging and USB drivers
- **Python 3.11+** - Project runtime

### Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows
   source .venv/bin/activate   # Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -e .
   ```

### Configuration

#### collector_config.yaml

```yaml
start_date: "2026-01-17"       # First date to scrape
data_folder: "data"            # Output data folder
device_name: "Nokia T20"       # Device from device_config.yaml
appium:
  host: "localhost"
  port: 4723
  platform_name: "Android"
  automation_name: "UiAutomator2"
  device_name: "AndroidDevice"
  app_package: "com.duracell"
  app_activity: "com.duracell/.MainActivity"
```

#### device_config.yaml

Defines device-specific settings including screen coordinates for UI interaction:

```yaml
devices:
  - name: "Nokia T20"
    screen_size: [1200, 2000]
    hamburger_menu_coordinates: [1130, 100]
    energy_insights_menu_button_coordinates: [65, 460]
    date_bounding_box: [470, 550, 730, 634]
    chart_hour_touch_coordinates:
      "00:00": [175, 1230]
      "01:00": [215, 1230]
      # ... (24 hour coordinates)
```

### Usage

The scraper provides three CLI commands via Typer:

#### Collect Data

Scrapes data from the Duracell Energy app for dates not yet collected:

```bash
python main.py collect-data
```

This command:
1. Connects to the Android device via Appium
2. Launches the Duracell Energy app
3. Navigates to the Energy Insights page
4. Iterates through each date in the configured date range
5. For each date, taps on each hour in the chart to extract tooltip data
6. Saves hourly data (grid, solar, battery, home usage) to JSON files

#### Consolidate to CSV

Merges collected JSON data into a single CSV file:

```bash
python main.py consolidate-json
```

#### Consolidate to DuckDB

Loads scraped data directly into DuckDB:

```bash
python main.py consolidate-duckdb
```

### Data Output

Scraped data is stored in `data/solar_data/YYYY/MM/DD/` as JSON files:

```json
{
  "date": "2026-01-17",
  "hour": "14:00",
  "grid": "0.54",
  "solar": "1.23",
  "battery": "0.32",
  "home": "0.37"
}
```

---

## 2. Data Warehouse

The data warehouse uses [dbt](https://docs.getdbt.com/) (data build tool) with DuckDB as the backend database. It implements a medallion architecture to transform raw scraped data into analytics-ready tables.

### Architecture

The dbt project follows a three-layer medallion architecture:

```
┌─────────────┐      ┌──────────────┐      ┌────────────┐
│   Staging   │────▶│ Intermediate  │────▶│   Marts    │
│   (Views)   │      │   (Views)    │      │  (Tables)  │
└─────────────┘      └──────────────┘      └────────────┘
```

### Models

#### Staging Layer (`models/staging/`)

Raw data from the scraper is exposed as staging views:

- `stg_scraper_solar` - Selects and casts raw solar data columns

#### Intermediate Layer (`models/intermediate/`)

Business logic and data cleaning:

- **Generation**
  - `int_generation_solar_cleaned` - Cleans and enriches solar data with calculated fields
  
- **Finance**
  - `int_finance_cost_savings` - Calculates cost savings using tariff data
  
- **Admin**
  - `int_admin_tariffs` - Tariff rate reference data
  - `int_admin_exclusions` - Date ranges to exclude from calculations

#### Marts Layer (`models/marts/`)

Final analytics tables for the dashboard:

- **Savings**
  - `daily_savings` - Daily cost savings breakdown
  - `monthly_savings` - Monthly aggregated savings
  - `total_savings` - Cumulative totals
  - `payback_forecast_current` - Payback period projection
  - `payback_forecast_development` - Development scenario projection

- **Generation**
  - Solar generation analytics (location varies)

- **Admin**
  - Administrative views (location varies)

### Seeds

Static reference data loaded into the warehouse:

- `raw_tariffs.csv` - Electricity tariff rates (peak/off-peak/export)
- `raw_exclusions.csv` - Date ranges to exclude from analysis

### Usage

Run all dbt models:

```bash
cd data_warehouse
dbt build
```

Other useful commands:

```bash
dbt run          # Execute models
dbt test         # Run tests
dbt docs generate  # Generate documentation
dbt debug        # Verify dbt configuration
```

### Configuration

The dbt project is configured in `dbt_project.yml`:

```yaml
name: 'solar_data_warehouse'
version: '1.0.0'
profile: 'solar_data_warehouse'

models:
  staging:
    +materialized: view
  intermediate:
    +materialized: view
  marts:
    +materialized: table
```

---

## 3. Dashboard

The dashboard is a [Streamlit](https://streamlit.io/) application that visualizes the analytics results from the data warehouse.

### Pages

#### Savings Page (`01_savings_page.py`)

- **Total Savings** - Cumulative savings, export income, and total savings
- **Payback Forecast** - Progress toward system payback, estimated completion date
- **Daily Cost Savings** - Bar chart of daily savings (consumption savings + export income)
- **Monthly Cost Savings** - Tabular view of monthly aggregations

#### Solar Generation Page (`02_solar_generation_page.py`)

- Solar generation analytics (may be disabled in navigation)

#### Debug Page (`03_debug_page.py`)

- Debugging and diagnostic information

### Usage

Start the dashboard:

```bash
python streamlit.py
```

The dashboard will open at `http://localhost:8501`.

### Database Connection

The dashboard connects to the DuckDB database at `data/solar_data.duckdb` in read-only mode. Query functions in `dashboard/utils/database.py` retrieve data from the marts layer.

### Energy Rates

Hardcoded rates (defined in `streamlit.py`):

| Rate Type | Value (£/kWh) |
|-----------|---------------|
| Peak | 0.289 |
| Off-Peak | 0.079 |
| Export | 0.151 |

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Scraper | Python, Appium, EasyOCR, Typer |
| Database | DuckDB |
| Analytics | dbt-core, dbt-duckdb |
| Dashboard | Streamlit, Pandas |
| Code Quality | Ruff, SQLFluff |

## License

This project is for personal use. The Duracell Energy app data scraping is not affiliated with Duracell.