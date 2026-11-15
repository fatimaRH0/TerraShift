"""
satellite.py - Turn the raw satellite CSVs into clean tables with friendly
column names and units, and load them for the dashboard.

Saved files (in data/):
  <field>_smap.csv      sm_surface, sm_rootzone (m³/m³), rain_smap_mm (mm/day)
  <field>_modis.csv     ndvi, evi
  <field>_ecostress.csv lst_c (°C), hour_local, period (day / night)
  <field>_landsat.csv   ndvi_landsat, lst_landsat_c (°C)  (Landsat Collection 2)
  <field>_srtm.csv      elevation_m
  <field>_gpm.csv       rain_gpm_mm (mm/day)
"""

import os

import pandas as pd

from src import config

SOURCES = ["smap", "gpm", "modis", "landsat", "ecostress", "srtm"]


def _keep(series, low, high):
    return series.where((series >= low) & (series <= high))


def clean_source(source, raw):
    """raw = table returned by appeears.read_results (columns = AppEEARS layers)."""
    def col(name):
        matches = [c for c in raw.columns if c == name or c.endswith(name)]
        return raw[matches[0]] if matches else pd.Series(index=raw.index, dtype=float)

    df = pd.DataFrame(index=raw.index)
    if source == "smap":
        df["sm_surface"] = _keep(col("sm_surface"), 0, 1)
        df["sm_rootzone"] = _keep(col("sm_rootzone"), 0, 1)
        # kg/m²/s  ->  mm/day
        df["rain_smap_mm"] = _keep(col("precipitation_total_surface_flux"), 0, 1) * 86400
    elif source == "modis":
        df["ndvi"] = _keep(col("NDVI"), -0.2, 1)        # MODIS valid range
        df["evi"] = _keep(col("EVI"), -0.2, 1)
    elif source == "ecostress":
        df["lst_c"] = _keep(col("LST"), 200, 350) - 273.15      # Kelvin -> °C
        # ECOSTRESS is on the space station: it passes at any hour, day or night.
        # Local solar hour ≈ UTC hour + longitude / 15
        hour = (df.index.hour + df.index.minute / 60 + config.LONGITUDE / 15) % 24
        df["hour_local"] = hour.round(1)
        df["period"] = ["day" if 9 <= h <= 17 else "night/evening" for h in hour]
    elif source == "srtm":
        df["elevation_m"] = _keep(col("SRTMGL1_DEM"), -500, 9000)
    return df.dropna(how="all")


def file_path(field_name, source):
    return os.path.join(config.DATA_DIR, f"{field_name}_{source}.csv")


def save_source(field_name, source, df):
    path = file_path(field_name, source)
    if df.empty:
        print(f"   ⚠️  {source}: no valid values, nothing saved")
        return None
    df.to_csv(path)
    print(f"   ✅ {source}: {len(df)} rows -> {path}")
    return path


def load_satellite(field_name):
    """Return {source: DataFrame} for every source already downloaded."""
    data = {}
    for source in SOURCES:
        path = file_path(field_name, source)
        if os.path.exists(path):
            df = pd.read_csv(path, index_col="date")
            df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
            if not df.empty:
                data[source] = df
    return data


def _distance_km(lat1, lon1, lat2, lon2):
    import math
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def place_key(lat, lon):
    """Name used for the files of a place downloaded from the app (data belongs to a place)."""
    return f"place_{lat:.4f}_{lon:.4f}".replace("-", "m")


def save_place(name, lat, lon):
    import json
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(os.path.join(config.DATA_DIR, f"{name}_place.json"), "w") as f:
        json.dump({"lat": lat, "lon": lon}, f)


def known_fields():
    """Every field that has satellite data, with its coordinates: {name: (lat, lon)}."""
    import glob
    import json
    fields = {config.FIELD_NAME: (config.LATITUDE, config.LONGITUDE),
              "test_field": (config.LATITUDE, config.LONGITUDE)}   # data downloaded under the old default name
    for path in glob.glob(os.path.join(config.DATA_DIR, "*_appeears_task.json")):
        name = os.path.basename(path)[: -len("_appeears_task.json")]
        try:
            with open(path) as f:
                lat, lon = json.load(f)["request_id"].split(",")[:2]
            fields[name] = (float(lat), float(lon))
        except (OSError, ValueError, KeyError):
            continue
    for path in glob.glob(os.path.join(config.DATA_DIR, "*_place.json")):
        name = os.path.basename(path)[: -len("_place.json")]
        try:
            with open(path) as f:
                p = json.load(f)
            fields[name] = (float(p["lat"]), float(p["lon"]))
        except (OSError, ValueError, KeyError):
            continue
    return fields


def load_satellite_for(field_name, lat, lon, max_km=2.0):
    """
    Satellite data belongs to a PLACE, not to a name: use the downloaded data closest to
    (lat, lon), only if it is less than max_km away. Returns (data, name of the data set).
    """
    best, best_km = None, max_km
    for name, (flat, flon) in known_fields().items():
        km = _distance_km(lat, lon, flat, flon)
        if km <= best_km and load_satellite(name):
            best, best_km = name, km
    return (load_satellite(best), best) if best else ({}, None)
