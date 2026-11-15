"""
nasa_power.py - Download NASA POWER data and keep a local copy (cache).
"""

import os
import re
from datetime import date, timedelta

import pandas as pd
import requests

from src import config


class NasaConnectionError(Exception):
    """Raised when the NASA server cannot be reached."""


def fetch_nasa_data(lat, lon, start, end):
    """Send a request to NASA POWER and return the JSON response."""
    params = {
        "parameters": ",".join(config.PARAMETERS),
        "community": "AG",              # AG = Agriculture
        "latitude": lat,
        "longitude": lon,
        "start": start.strftime("%Y%m%d"),
        "end": end.strftime("%Y%m%d"),
        "format": "JSON",
    }
    try:
        response = requests.get(config.API_URL, params=params, timeout=60)
    except requests.exceptions.ConnectionError as error:
        raise NasaConnectionError(
            "Could not connect to power.larc.nasa.gov. "
            "Check your internet, try another network, or change DNS to 8.8.8.8"
        ) from error

    response.raise_for_status()          # stop if the server returned an error
    return response.json()


def json_to_dataframe(json_data):
    """
    NASA response shape:
      {"properties": {"parameter": {"T2M": {"20250101": 12.3, ...}, ...}}}
    We turn it into a table: one row per day, one column per variable.
    """
    values = json_data["properties"]["parameter"]
    df = pd.DataFrame(values)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df.index.name = "date"

    # NASA uses -999 for missing values -> replace with NaN (empty)
    df = df.astype(float).replace(-999.0, float("nan"))

    # Drop trailing days that are completely empty (NASA lags a few days)
    return df.dropna(how="all")


def cache_path(field_name, start, end):
    """Build the CSV file name used to store the data locally."""
    name = f"{field_name}_{start:%Y%m%d}_{end:%Y%m%d}.csv"
    return os.path.join(config.DATA_DIR, name)


def remove_old_copies(field_name, keep):
    """Delete older downloads of the same field and period length (they are replaced by `keep`)."""
    import glob
    pattern = re.compile(re.escape(field_name) + r"_\d{8}_\d{8}\.csv$")
    days = _span_days(keep)
    for path in glob.glob(os.path.join(config.DATA_DIR, f"{field_name}_*.csv")):
        if path != keep and pattern.search(os.path.basename(path)) and _span_days(path) == days:
            os.remove(path)


def _span_days(path):
    start, end = re.findall(r"(\d{8})", os.path.basename(path))[-2:]
    return (pd.Timestamp(end) - pd.Timestamp(start)).days


def get_field_data(lat, lon, field_name, num_days=config.NUM_DAYS, use_cache=True):
    """
    Main function of this module.
    Returns a DataFrame with the daily data for a field.
    If the data was already downloaded today, it is read from the CSV file
    instead of asking NASA again (faster, and works offline).
    """
    os.makedirs(config.DATA_DIR, exist_ok=True)

    end = date.today() - timedelta(days=config.NASA_DELAY_DAYS)
    start = end - timedelta(days=num_days)
    # The saved copy belongs to a PLACE: the same field name at another location must never
    # reuse it. The name is also cleaned so any text typed by a user is a valid file name.
    safe = re.sub(r"[^\w\- ]", "_", str(field_name)).strip() or "field"
    field_name = f"{safe}_{lat:.3f}_{lon:.3f}".replace("-", "m") if "-" not in safe else \
        f"{safe}_" + f"{lat:.3f}_{lon:.3f}".replace("-", "m")
    csv_file = cache_path(field_name, start, end)

    if use_cache and os.path.exists(csv_file):
        print(f"📂 Loading cached data: {csv_file}")
        return pd.read_csv(csv_file, index_col="date", parse_dates=True)

    print("⏳ Fetching data from NASA POWER ...")
    df = json_to_dataframe(fetch_nasa_data(lat, lon, start, end))
    df.to_csv(csv_file)
    remove_old_copies(field_name, csv_file)
    print(f"💾 Saved {len(df)} days to: {csv_file}")
    return df
