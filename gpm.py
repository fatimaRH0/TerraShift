"""
gpm.py - GPM IMERG precipitation for a point.

Main route: the "Giovanni in the Cloud – Time Series" API of NASA GES DISC
    https://api.giovanni.earthdata.nasa.gov/timeseries
It returns the IMERG values for one point as text (no big global files).
It needs an Earthdata token, which we create automatically from your login.

Fallback: the older GES DISC "Data Rods" service.
IMERG Final is published ~3.5–4 months after the observation.
"""

import re
from datetime import timedelta

import pandas as pd
import requests

GIOVANNI_URL = "https://api.giovanni.earthdata.nasa.gov/timeseries"
SIGNIN_URL = "https://api.giovanni.earthdata.nasa.gov/signin"
TOKEN_URL = "https://urs.earthdata.nasa.gov/api/users/find_or_create_token"
DATARODS_URL = "https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi"

# Giovanni dataset names to try: (name, unit of the values)
GIOVANNI_DATASETS = [
    ("GPM_3IMERGDF_07_precipitation", "mm/day"),     # daily Final
    ("GPM_3IMERGHH_07_precipitation", "mm/hr"),      # half-hourly Final
]
DATARODS_VARIABLES = [
    "GPM:GPM_3IMERGHH.07:precipitation",
    "GPM:GPM_3IMERGHH_07:precipitation",
]


class GpmError(Exception):
    """Problem while downloading GPM data."""


# ---------------------------------------------------------
# Earthdata token
# ---------------------------------------------------------
def get_tokens(user, password):
    """
    Giovanni gives its own token (valid 24 h) through its sign-in link.
    As a backup we also try the general Earthdata token.
    """
    tokens = []
    try:
        r = requests.get(SIGNIN_URL, auth=(user, password), allow_redirects=True, timeout=60)
        if r.status_code == 200 and r.text.strip():
            tokens.append(r.text.strip().replace('"', ""))
    except requests.exceptions.RequestException:
        pass
    try:
        r = requests.post(TOKEN_URL, auth=(user, password), timeout=60)
        if r.status_code == 200:
            tokens.append(r.json()["access_token"])
    except (requests.exceptions.RequestException, KeyError, ValueError):
        pass
    if not tokens:
        raise GpmError("Could not get a token from Giovanni / Earthdata.")
    return tokens


# ---------------------------------------------------------
# Parsing the text answers
# ---------------------------------------------------------
def parse_giovanni(text):
    """
    Answer format:
        prod_name,GPM_3IMERGDF_07_precipitation
        unit,mm/day
        lat,33.95
        lon,-5.55
        Timestamp (UTC),Data
        2025-01-01 00:00,1.25
    Returns (series, metadata).
    """
    meta, times, values, in_data = {}, [], [], False
    for line in text.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            continue
        if parts[0].lower().startswith("timestamp"):
            in_data = True
            continue
        if not in_data:
            meta[parts[0].lower()] = parts[1]
            continue
        try:
            values.append(float(parts[1]))
            times.append(parts[0])
        except ValueError:
            continue
    series = pd.Series(values, index=pd.to_datetime(times, errors="coerce"), dtype=float)
    series = series[series.index.notna()]
    return series[series >= 0], meta


def parse_datarods(text):
    """Lines like '2025-01-01T00:30:00   0.25'."""
    times, values = [], []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 2 or not re.match(r"^\d{4}-\d{2}-\d{2}", parts[0]):
            continue
        try:
            values.append(float(parts[-1]))
        except ValueError:
            continue
        times.append(" ".join(parts[:-1]).replace("T", " ").replace("Z", ""))
    series = pd.Series(values, index=pd.to_datetime(times, errors="coerce"), dtype=float)
    series = series[series.index.notna()]
    return series[series >= 0]


def to_daily(series, unit):
    """Convert to a daily total in mm."""
    if unit == "mm/hr":                       # half-hourly rate -> mm per half hour
        return (series * 0.5).resample("D").sum(min_count=1)
    return series.resample("D").mean()        # already mm/day


# ---------------------------------------------------------
# Giovanni route
# ---------------------------------------------------------
def _giovanni_request(token, dataset, lat, lon, start, end):
    params = {
        "data": dataset,
        "location": f"[{lat},{lon}]",
        "time": f"{start:%Y-%m-%d}T00:00:00/{end:%Y-%m-%d}T23:59:59",
    }
    response = requests.get(GIOVANNI_URL, params=params,
                            headers={"authorizationtoken": token}, timeout=600)
    if response.status_code != 200:
        raise GpmError(f"Giovanni {dataset}: HTTP {response.status_code}: {response.text[:200]}")
    return parse_giovanni(response.text)


def fetch_giovanni(token, dataset, unit, lat, lon, start, end):
    # Half-hourly data is big: ask month by month
    step = timedelta(days=30) if unit == "mm/hr" else timedelta(days=400)
    parts, chunk_start = [], start
    while chunk_start <= end:
        chunk_end = min(chunk_start + step, end)
        series, meta = _giovanni_request(token, dataset, lat, lon, chunk_start, chunk_end)
        if not series.empty:
            parts.append(series)
        chunk_start = chunk_end + timedelta(days=1)
    if not parts:
        raise GpmError(f"Giovanni {dataset}: no values returned.")
    return to_daily(pd.concat(parts).sort_index(), unit)


# ---------------------------------------------------------
# Data Rods route (fallback)
# ---------------------------------------------------------
def fetch_datarods(session, lat, lon, start, end):
    last_error = "no answer"
    for variable in DATARODS_VARIABLES:
        params = {"variable": variable, "location": f"GEOM:POINT({lon}, {lat})",
                  "startDate": f"{start:%Y-%m-%d}T00", "endDate": f"{end:%Y-%m-%d}T23",
                  "type": "asc2"}
        response = session.get(DATARODS_URL, params=params, timeout=600)
        series = parse_datarods(response.text) if response.status_code == 200 else pd.Series(dtype=float)
        if not series.empty:
            return to_daily(series, "mm/hr")
        if "<html" in response.text[:500].lower():
            last_error = (f"{variable}: got a web page instead of data (the GES DISC application "
                          "is probably not authorized in your Earthdata profile)")
        else:
            last_error = f"{variable}: HTTP {response.status_code}"
    raise GpmError(f"Data Rods: {last_error}")


# ---------------------------------------------------------
# Main function
# ---------------------------------------------------------
def fetch_gpm_daily(user, password, session, lat, lon, start, end):
    """Return a daily table with 'rain_gpm_mm' (mm/day). Tries several routes."""
    errors = []
    try:
        for i, token in enumerate(get_tokens(user, password), 1):
            for dataset, unit in GIOVANNI_DATASETS:
                try:
                    print(f"   trying Giovanni {dataset} (token {i}) ...")
                    daily = fetch_giovanni(token, dataset, unit, lat, lon, start, end)
                    print(f"   ✔ {dataset}: {daily.notna().sum()} days")
                    return daily.to_frame("rain_gpm_mm").rename_axis("date")
                except (GpmError, requests.exceptions.RequestException) as error:
                    errors.append(str(error)[:160])
    except GpmError as error:
        errors.append(str(error))

    try:
        print("   trying Data Rods ...")
        daily = fetch_datarods(session, lat, lon, start, end)
        return daily.to_frame("rain_gpm_mm").rename_axis("date")
    except (GpmError, requests.exceptions.RequestException) as error:
        errors.append(str(error)[:200])

    raise GpmError(" | ".join(errors))
