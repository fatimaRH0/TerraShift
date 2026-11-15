"""
pc_nasa.py - NASA products read WITHOUT any account, from the Microsoft Planetary Computer
(a free public copy of the NASA LP DAAC archives). Only the pixel of the field is read.

  - MODIS MOD13Q1 / MYD13Q1 v6.1 : NDVI and EVI, 250 m, every 16 days (NASA Terra / Aqua)
  - NASADEM                      : elevation, 30 m (NASA's reprocessed SRTM)
"""

import os
from datetime import date

import pandas as pd

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"


def _catalog():
    import planetary_computer
    import pystac_client
    os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
    os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif,.TIF")
    return pystac_client.Client.open(STAC_URL, modifier=planetary_computer.sign_inplace)


def _sample(href, lat, lon):
    import rasterio
    from rasterio.warp import transform
    with rasterio.open(href) as src:
        xs, ys = transform("EPSG:4326", src.crs, [lon], [lat])
        return float(next(src.sample([(xs[0], ys[0])]))[0])


def fetch_modis_point(lat, lon, start, end):
    items = list(_catalog().search(collections=["modis-13Q1-061"],
                                   intersects={"type": "Point", "coordinates": [lon, lat]},
                                   datetime=f"{start:%Y-%m-%d}/{end:%Y-%m-%d}").items())
    print(f"   {len(items)} MODIS images found")
    rows = []
    for i, item in enumerate(items, 1):
        try:
            ndvi = _sample(item.assets["250m_16_days_NDVI"].href, lat, lon)
            evi = _sample(item.assets["250m_16_days_EVI"].href, lat, lon)
            when = item.properties.get("start_datetime") or item.datetime
            if ndvi > -3000:                                  # -3000 = no data
                ts = pd.Timestamp(when)
                if ts.tzinfo is not None:
                    ts = ts.tz_convert(None)
                rows.append({"date": ts.normalize(), "ndvi": ndvi * 0.0001,
                             "evi": evi * 0.0001 if evi > -3000 else None})
        except Exception as error:
            print(f"   ⚠️  MODIS image {item.id}: {error}")
        if i % 3 == 0:
            print(f"   ... {i}/{len(items)} MODIS images read")
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).groupby("date")[["ndvi", "evi"]].mean()      # Terra + Aqua same day
    df = df.where((df >= -0.2) & (df <= 1))
    df.index.name = "date"
    return df.sort_index().dropna(how="all")


def fetch_nasadem_point(lat, lon):
    items = list(_catalog().search(collections=["nasadem"],
                                   intersects={"type": "Point", "coordinates": [lon, lat]}).items())
    if not items:
        return pd.DataFrame()
    elev = _sample(items[0].assets["elevation"].href, lat, lon)
    if not -500 <= elev <= 9000:
        return pd.DataFrame()
    df = pd.DataFrame({"elevation_m": [elev]}, index=pd.to_datetime([date(2000, 2, 11)]))  # SRTM flight
    df.index.name = "date"
    return df
