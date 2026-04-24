from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd

from scraper.utils import get_base_path

DATABASE_FILE = get_base_path() / "data" / "solar_data.duckdb"


def connect_to_duckdb(db_path: str | Path = DATABASE_FILE) -> duckdb.DuckDBPyConnection:
    """
    Connect to a DuckDB database.

    Args:
        db_path (str): The path to the DuckDB database file.

    Returns:
        duckdb.DuckDBPyConnection: A connection object to the DuckDB database.
    """
    try:
        conn = duckdb.connect(db_path, read_only=True)
        return conn
    except Exception as e:
        print(f"Error connecting to DuckDB: {e}")
        raise


def get_data_date(
    conn: duckdb.DuckDBPyConnection = connect_to_duckdb(),
) -> datetime:
    """
    Retrieve the latest data date from the DuckDB database.

    Args:
        conn (duckdb.DuckDBPyConnection): A connection object to the DuckDB database.

    Returns:
        datetime.datetime: The latest data date in the database.
    """
    try:
        query = """
        SELECT 
            data_date
        FROM 
            data_date;
        """
        result: pd.DataFrame = conn.execute(query).df()
        return result["data_date"][0]
    except Exception as e:
        print(f"Error retrieving data date: {e}")
        raise


def get_daily_savings(
    conn: duckdb.DuckDBPyConnection = connect_to_duckdb(),
) -> pd.DataFrame:
    """
    Retrieve daily savings data from the DuckDB database.

    Args:
        conn (duckdb.DuckDBPyConnection): A connection object to the DuckDB database.

    Returns:
        pd.DataFrame: A DataFrame containing the daily savings data.
    """
    try:
        query = """
        SELECT 
            s.reading_date,
            s.grid,
            s.solar,
            s.battery,
            s.home,
            s.kw_saved,
            s.kw_exported,
            s.saving,
            s.export_income,
            s.total_saving
        FROM 
            daily_savings AS s
        ORDER BY 
            s.reading_date DESC;
        """
        result: pd.DataFrame = conn.execute(query).df()
        return result
    except Exception as e:
        print(f"Error retrieving daily savings: {e}")
        raise


def get_monthly_savings(
    conn: duckdb.DuckDBPyConnection = connect_to_duckdb(),
) -> pd.DataFrame:
    """
    Retrieve monthly savings data from the DuckDB database.

    Args:
        conn (duckdb.DuckDBPyConnection): A connection object to the DuckDB database.

    Returns:
        pd.DataFrame: A DataFrame containing the monthly savings data.
    """
    try:
        query = """
        SELECT 
            s.reading_month,
            s.grid,
            s.solar,
            s.battery,
            s.home,
            s.kw_saved,
            s.kw_exported,
            s.saving,
            s.export_income,
            s.total_saving
        FROM 
            monthly_savings AS s
        ORDER BY 
            s.reading_month DESC;
        """
        result: pd.DataFrame = conn.execute(query).df()
        return result
    except Exception as e:
        print(f"Error retrieving monthly savings: {e}")
        raise


def get_total_savings(
    conn: duckdb.DuckDBPyConnection = connect_to_duckdb(),
) -> pd.DataFrame:
    """
    Retrieve total savings data from the DuckDB database.

    Args:
        conn (duckdb.DuckDBPyConnection): A connection object to the DuckDB database.

    Returns:
        pd.DataFrame: A DataFrame containing the total savings data.
    """
    try:
        query = """
        SELECT 
            s.grid,
            s.solar,
            s.battery,
            s.home,
            s.kw_saved,
            s.kw_exported,
            s.saving,
            s.export_income,
            s.total_saving
        FROM 
            total_savings AS s;
        """
        result: pd.DataFrame = conn.execute(query).df()
        return result
    except Exception as e:
        print(f"Error retrieving total savings: {e}")
        raise


def get_payback_forecast(
    conn: duckdb.DuckDBPyConnection = connect_to_duckdb(),
) -> pd.DataFrame:
    """
    Retrieve payback forecast data from the DuckDB database.

    Args:
        conn (duckdb.DuckDBPyConnection): A connection object to the DuckDB database.

    Returns:
        pd.DataFrame: A DataFrame containing the payback forecast data.
    """
    try:
        query = """
        SELECT 
            p.data_date,
            p.payback_percentage,
            p.day_number,
            p.days_to_payback,
            p.average_daily_saving,
            p.forecast_payback_date
        FROM 
            payback_forecast_current AS p;
        """
        result: pd.DataFrame = conn.execute(query).df()
        return result
    except Exception as e:
        print(f"Error retrieving payback forecast: {e}")
        raise


def get_payback_forecast_development(
    conn: duckdb.DuckDBPyConnection = connect_to_duckdb(),
) -> pd.DataFrame:
    """
    Retrieve payback forecast development data from the DuckDB database.

    Args:
        conn (duckdb.DuckDBPyConnection): A connection object to the DuckDB database.

    Returns:
        pd.DataFrame: A DataFrame containing the payback forecast data.
    """
    try:
        query = """
        SELECT 
            p.reading_date,
            p.payback_percentage,
            p.day_number,
            p.days_to_payback,
            p.average_daily_saving,
            p.forecast_payback_date
        FROM 
            payback_forecast_development AS p;
        """
        result: pd.DataFrame = conn.execute(query).df()
        return result
    except Exception as e:
        print(f"Error retrieving payback forecast: {e}")
        raise
