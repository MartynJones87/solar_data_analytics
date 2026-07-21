import datetime as dt
from pathlib import Path


def get_base_path() -> Path:
    """
    Get the base path of the project, which is the parent directory of the 'scraper' directory.

    Returns:
        Path: The base path of the project.
    """
    current_file_path = Path(__file__).resolve()
    base_path = current_file_path.parent.parent
    return base_path


def parse_date(text: str) -> dt.date:
    """
    Convert OCR text into a datetime object.
    Expected format:
    '07 | 02 2026' -> datetime.date(2026, 2, 7)
    '07 02 2026' -> datetime.date(2026, 2, 7)
    """
    expected_date_formats = [
        "%d | %m %Y",
        "%d| %m %Y",
        "%d|%m %Y",
        "%d |%m %Y",
        "%d/%m %Y",
        "%d %m %Y",
    ]
    for fmt in expected_date_formats:
        try:
            return dt.datetime.strptime(text, fmt).date()
        except Exception:
            pass
    raise ValueError(f"Date text '{text}' is not in an expected format.")
