"""
terrain.py - Slope of the field from elevation data (function 4: relief and runoff).

Elevation comes from free open elevation tiles ("Terrarium", AWS Open Data), built
mainly from NASA SRTM. We download one 256 x 256 tile around the field, decode the
heights, and compute the slope of each pixel (~15 m at zoom 13 in Morocco).
Slope matters because steep, bare soil loses water by runoff and soil by erosion.
"""

import io
import math

import numpy as np
import requests

TILE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"


def _tile_xy(lat, lon, z):
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def elevation_tile(lat, lon, z=13):
    """Return (elevation grid in metres, pixel size in metres, pixel row/col of the point)."""
    from PIL import Image
    x, y = _tile_xy(lat, lon, z)
    url = TILE_URL.format(z=z, x=int(x), y=int(y))
    img = Image.open(io.BytesIO(requests.get(url, timeout=30).content)).convert("RGB")
    a = np.asarray(img, dtype=float)
    elev = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768      # Terrarium encoding
    pixel_m = 156543.03 * math.cos(math.radians(lat)) / 2 ** z
    row, col = int((y - int(y)) * 256), int((x - int(x)) * 256)
    return elev, pixel_m, (row, col)


def slope_degrees(elev, pixel_m):
    dzdy, dzdx = np.gradient(elev, pixel_m)
    return np.degrees(np.arctan(np.hypot(dzdx, dzdy)))


def slope_class(percent):
    if percent < 2:
        return "Flat", "Water stays in place; little erosion. Watch for waterlogging after heavy rain."
    if percent < 5:
        return "Gentle", "Low runoff. Plough and sow across the slope."
    if percent < 15:
        return "Moderate", ("Real runoff and erosion risk when the soil is bare: keep residues or a "
                            "cover crop in the rainy months, work along contour lines.")
    return "Steep", ("High erosion risk: avoid leaving the soil bare, prefer permanent cover "
                     "(forage, trees) or terraces.")


def field_slope(lat, lon, radius_px=13):
    """Slope statistics in a ~400 m window around the field."""
    elev, pixel_m, (r, c) = elevation_tile(lat, lon)
    slope = slope_degrees(elev, pixel_m)
    r0, r1 = max(r - radius_px, 1), min(r + radius_px, 254)
    c0, c1 = max(c - radius_px, 1), min(c + radius_px, 254)
    win_slope, win_elev = slope[r0:r1, c0:c1], elev[r0:r1, c0:c1]
    mean_pct = float(np.tan(np.radians(win_slope.mean())) * 100)
    label, advice = slope_class(mean_pct)
    return {"mean_slope_pct": mean_pct,
            "max_slope_pct": float(np.tan(np.radians(win_slope.max())) * 100),
            "elevation_min": float(win_elev.min()), "elevation_max": float(win_elev.max()),
            "class": label, "advice": advice, "pixel_m": pixel_m,
            "slope_grid": np.tan(np.radians(win_slope)) * 100, "elev_grid": win_elev}
