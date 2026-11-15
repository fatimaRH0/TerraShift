"""
landsat.py - Landsat Collection 2 Level-2 (the USGS "Landsat Science Products")
for one point.

Collection 2 Level-2 gives:
  - Surface Reflectance (SR): we use red + near-infrared to compute NDVI (30 m)
  - Surface Temperature (ST): band lwir11, converted to °C
The scenes are read from the Microsoft Planetary Computer, a free public mirror
of the USGS Collection 2 archive (no account needed). Only the pixel of the
field is read from each image, not the whole image.

Extra packages:  pip install pystac-client planetary-computer rasterio
"""

import os

import pandas as pd

from src import config

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

# Official USGS Collection 2 Level-2 scale factors
SR_SCALE, SR_OFFSET = 0.0000275, -0.2
ST_SCALE, ST_OFFSET = 0.00341802, 149.0


def clear_pixel(qa):
    """QA_PIXEL bits: 0 fill, 1 dilated cloud, 3 cloud, 4 cloud shadow."""
    return (int(qa) & 0b11011) == 0


def to_row(date, platform, red_dn, nir_dn, qa, lwir_dn):
    """Convert raw numbers (DN) into NDVI and °C. Returns None if cloudy / no data."""
    if red_dn == 0 or nir_dn == 0 or not clear_pixel(qa):
        return None
    red = red_dn * SR_SCALE + SR_OFFSET
    nir = nir_dn * SR_SCALE + SR_OFFSET
    ndvi = (nir - red) / (nir + red) if (nir + red) > 0 else float("nan")
    lst_c = (lwir_dn * ST_SCALE + ST_OFFSET - 273.15) if lwir_dn else float("nan")
    return {"date": date, "platform": platform, "ndvi_landsat": ndvi, "lst_landsat_c": lst_c}


def fetch_landsat_point(lat, lon, start, end, max_cloud=60):
    import planetary_computer
    import pystac_client
    import rasterio
    from rasterio.warp import transform

    # Faster remote reading of Cloud-Optimized GeoTIFFs
    os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
    os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif,.TIF")

    catalog = pystac_client.Client.open(STAC_URL, modifier=planetary_computer.sign_inplace)
    search = catalog.search(
        collections=[config.LANDSAT_COLLECTION],
        intersects={"type": "Point", "coordinates": [lon, lat]},
        datetime=f"{start:%Y-%m-%d}/{end:%Y-%m-%d}",
        query={"eo:cloud_cover": {"lt": max_cloud},
               "platform": {"in": ["landsat-8", "landsat-9"]}},
    )
    items = list(search.items())
    print(f"   {len(items)} Landsat scenes found")

    def sample(item, asset):
        with rasterio.open(item.assets[asset].href) as src:
            xs, ys = transform("EPSG:4326", src.crs, [lon], [lat])
            return float(next(src.sample([(xs[0], ys[0])]))[0])

    rows = []
    for i, item in enumerate(items, 1):
        try:
            qa = sample(item, "qa_pixel")
            if not clear_pixel(qa):
                continue
            row = to_row(item.datetime.date(), item.properties.get("platform"),
                         sample(item, "red"), sample(item, "nir08"), qa,
                         sample(item, "lwir11") if "lwir11" in item.assets else 0)
            if row:
                rows.append(row)
        except Exception as error:          # one bad scene should not stop everything
            print(f"   ⚠️  scene {item.id}: {error}")
        if i % 3 == 0:
            print(f"   ... {i}/{len(items)} scenes read")

    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).groupby("date")[["ndvi_landsat", "lst_landsat_c"]].mean()
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    return df.sort_index()


# =========================================================
# Pixel grid over the whole field (for the 3D virtual farm)
# =========================================================
def _open_catalog():
    import planetary_computer
    import pystac_client
    os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
    os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif,.TIF")
    return pystac_client.Client.open(STAC_URL, modifier=planetary_computer.sign_inplace)


def _read_window(href, bounds_lonlat):
    """Read only the pixels covering the field (not the whole 185 km image)."""
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import Window, from_bounds

    with rasterio.open(href) as src:
        left, bottom, right, top = transform_bounds("EPSG:4326", src.crs, *bounds_lonlat)
        w = from_bounds(left, bottom, right, top, src.transform)
        col0, row0 = int(w.col_off) - 1, int(w.row_off) - 1
        width, height = int(w.width) + 3, int(w.height) + 3
        window = Window(col0, row0, width, height)
        data = src.read(1, window=window, boundless=True, fill_value=0)
        return data, src.window_transform(window), src.crs


def read_field_grid(item, bounds_lonlat):
    """
    Return one row per 30 m pixel: lon, lat, ndvi, lst_c, clear (no cloud).
    """
    import numpy as np
    from rasterio.transform import xy
    from rasterio.warp import transform

    red, tr, crs = _read_window(item.assets["red"].href, bounds_lonlat)
    nir, _, _ = _read_window(item.assets["nir08"].href, bounds_lonlat)
    qa, _, _ = _read_window(item.assets["qa_pixel"].href, bounds_lonlat)
    lwir = (_read_window(item.assets["lwir11"].href, bounds_lonlat)[0]
            if "lwir11" in item.assets else np.zeros_like(red))

    rows, cols = np.indices(red.shape)
    xs, ys = xy(tr, rows.ravel(), cols.ravel())
    lons, lats = transform(crs, "EPSG:4326", list(xs), list(ys))

    red_r = red.ravel() * SR_SCALE + SR_OFFSET
    nir_r = nir.ravel() * SR_SCALE + SR_OFFSET
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = (nir_r - red_r) / (nir_r + red_r)
    lst = np.where(lwir.ravel() > 0, lwir.ravel() * ST_SCALE + ST_OFFSET - 273.15, np.nan)
    valid = (red.ravel() > 0) & (nir.ravel() > 0)
    clear = np.array([clear_pixel(q) for q in qa.ravel()]) & valid
    return pd.DataFrame({"lon": lons, "lat": lats, "ndvi": np.where(valid, ndvi, np.nan),
                         "lst_c": lst, "clear": clear})


def best_scene_grid(polygon, start, end, max_cloud=30, tries=6):
    """
    Find the clearest Landsat 8/9 scene over the field between start and end,
    and return (scene date, pixel table inside the field).
    """
    from src.field import bbox, contains

    bounds = bbox(polygon)
    catalog = _open_catalog()
    search = catalog.search(
        collections=[config.LANDSAT_COLLECTION],
        bbox=list(bounds),
        datetime=f"{start:%Y-%m-%d}/{end:%Y-%m-%d}",
        query={"eo:cloud_cover": {"lt": max_cloud}, "platform": {"in": ["landsat-8", "landsat-9"]}},
    )
    items = sorted(search.items(), key=lambda it: it.properties.get("eo:cloud_cover", 100))
    for item in items[:tries]:
        grid = read_field_grid(item, bounds)
        grid = grid[[contains(polygon, x, y) for x, y in zip(grid["lon"], grid["lat"])]]
        if len(grid) and grid["clear"].mean() >= 0.8:
            return item.datetime.date(), grid[grid["clear"]].drop(columns="clear").reset_index(drop=True)
    return None, pd.DataFrame()
