"""
appeears.py - Client for NASA AppEEARS (point samples).

AppEEARS extracts satellite values at a point (our field) and returns CSV files.
We use it for SMAP, MODIS, ECOSTRESS and SRTM with one API.
API documentation: https://appeears.earthdatacloud.nasa.gov/api/

How it works:
  1. login            -> get a token
  2. submit_task      -> ask AppEEARS to extract the data (runs on NASA servers)
  3. wait_for_task    -> check every 30 s until it is "done" (minutes to ~1 hour)
  4. download_results -> download the CSV files
"""

import os
import time

import pandas as pd
import requests

API = "https://appeears.earthdatacloud.nasa.gov/api"


class AppeearsError(Exception):
    """Any problem while talking to AppEEARS."""


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------
def login(user, password):
    response = requests.post(f"{API}/login", auth=(user, password), timeout=60)
    if response.status_code in (400, 401, 403):
        raise AppeearsError("Login refused: check your Earthdata username/password.")
    response.raise_for_status()
    return response.json()["token"]


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------
# Products and layers (automatic discovery)
# ---------------------------------------------------------
def list_products():
    response = requests.get(f"{API}/product", timeout=120)
    response.raise_for_status()
    return response.json()


def _version_key(product_and_version):
    version = product_and_version.split(".", 1)[1]
    return int(version) if version.isdigit() else 0


def latest_version(products, short_name):
    """Return e.g. 'MOD13Q1.061' for short_name 'MOD13Q1' (newest version)."""
    matches = [p["ProductAndVersion"] for p in products
               if p["ProductAndVersion"].split(".")[0] == short_name]
    if not matches:
        raise AppeearsError(f"Product {short_name} not found in AppEEARS.")
    return max(matches, key=_version_key)


def choose_version(products, short_name, version=None):
    """Use the version asked for (e.g. '007'); if AppEEARS does not have it, use the newest."""
    if version:
        wanted = f"{short_name}.{version}"
        if any(p["ProductAndVersion"] == wanted for p in products):
            return wanted
        print(f"   ⚠️  {wanted} is not in AppEEARS, using the newest version instead.")
    return latest_version(products, short_name)


def list_layers(product_and_version):
    response = requests.get(f"{API}/product/{product_and_version}", timeout=60)
    response.raise_for_status()
    return response.json()          # {layer_name: {details...}, ...}


def pick_layers(available, wanted):
    """Match the layer names we want with the real names in AppEEARS."""
    found = []
    for name in wanted:
        if name in available:
            found.append(name)
            continue
        candidates = [layer for layer in available if layer.endswith(name)]
        if candidates:
            found.append(min(candidates, key=len))
        else:
            print(f"   ⚠️  Layer '{name}' not found. Available: {list(available)[:15]} ...")
    return found


# ---------------------------------------------------------
# Tasks
# ---------------------------------------------------------
def submit_task(token, name, lat, lon, start, end, layers):
    """layers = [{"product": "MOD13Q1.061", "layer": "_250m_16_days_NDVI"}, ...]"""
    task = {
        "task_type": "point",
        "task_name": name,
        "params": {
            "dates": [{"startDate": start.strftime("%m-%d-%Y"),
                       "endDate": end.strftime("%m-%d-%Y")}],
            "layers": layers,
            "coordinates": [{"id": "field", "category": "field",
                             "latitude": lat, "longitude": lon}],
        },
    }
    response = requests.post(f"{API}/task", json=task, headers=_headers(token), timeout=120)
    if response.status_code >= 400:
        raise AppeearsError(f"Task refused ({response.status_code}): {response.text[:500]}")
    return response.json()["task_id"]


def task_status(token, task_id):
    response = requests.get(f"{API}/task/{task_id}", headers=_headers(token), timeout=60)
    response.raise_for_status()
    return response.json().get("status", "unknown")


def wait_for_task(token, task_id, poll_seconds=30, max_hours=3, max_network_errors=20):
    """
    Check the task every 30 s until it is "done".
    Short internet cuts are tolerated: the task keeps running on NASA servers,
    so we just wait and try again (up to 20 times in a row = ~10 min).
    """
    start = time.time()
    network_errors = 0
    while True:
        minutes = (time.time() - start) / 60
        try:
            status = task_status(token, task_id)
            network_errors = 0
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            network_errors += 1
            print(f"   📡 Connection lost ({network_errors}/{max_network_errors}), retrying ...")
            if network_errors >= max_network_errors:
                raise AppeearsError("Internet connection lost. Run the script again later: "
                                    "it will resume the same request.")
            time.sleep(poll_seconds)
            continue

        print(f"   ⏳ AppEEARS status: {status}  ({minutes:.0f} min)")
        if status == "done":
            return
        if status in ("error", "expired", "deleted"):
            raise AppeearsError(f"Task ended with status '{status}'.")
        if minutes > max_hours * 60:
            raise AppeearsError("Still running. Run the script again later to resume.")
        time.sleep(poll_seconds)


def download_results(token, task_id, out_dir):
    """Download the '...-results.csv' files of a finished task."""
    os.makedirs(out_dir, exist_ok=True)
    response = requests.get(f"{API}/bundle/{task_id}", headers=_headers(token), timeout=60)
    response.raise_for_status()
    paths = []
    for f in response.json()["files"]:
        if not f["file_name"].endswith("results.csv"):
            continue
        path = os.path.join(out_dir, os.path.basename(f["file_name"]))
        r = requests.get(f"{API}/bundle/{task_id}/{f['file_id']}", headers=_headers(token),
                         allow_redirects=True, stream=True, timeout=300)
        r.raise_for_status()
        with open(path, "wb") as out:
            for chunk in r.iter_content(chunk_size=1 << 16):
                out.write(chunk)
        paths.append(path)
        print(f"   💾 {path}")
    return paths


# ---------------------------------------------------------
# Reading the CSV results
# ---------------------------------------------------------
def read_results(path, layers, keep_time=False):
    """
    Return a table with one column per layer.
    By default, several observations on the same day (e.g. SMAP every 3 hours)
    are averaged into one daily value. With keep_time=True every observation
    is kept with its time (useful for ECOSTRESS, which passes day AND night).
    """
    raw = pd.read_csv(path)
    when = pd.to_datetime(raw["Date"].astype(str).str.replace(" UTC", ""), utc=True).dt.tz_localize(None)
    out = pd.DataFrame()
    for layer in layers:
        cols = [c for c in raw.columns if c == layer or c.endswith("_" + layer)]
        if cols:
            out[layer] = pd.to_numeric(raw[min(cols, key=len)], errors="coerce")
    if keep_time:
        out["date"] = when
        return out.set_index("date").sort_index()
    out["date"] = when.dt.normalize()
    return out.groupby("date").mean()
