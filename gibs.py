"""
gibs.py - NASA GIBS (Global Imagery Browse Services) map layers.

GIBS serves ready-made satellite IMAGES (tiles) for the whole planet, every day.
No account and no download: the map just shows the pictures.
We read the official layer list (GetCapabilities) once, then find the layers
that match the NASA products of the TerraShift document.
"""

import os
import time
import xml.etree.ElementTree as ET

import requests

from src import config

CAPABILITIES_URL = "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/1.0.0/WMTSCapabilities.xml"
CACHE_FILE = os.path.join(config.DATA_DIR, "gibs_capabilities.xml")
NS = {"w": "http://www.opengis.net/wmts/1.0", "ows": "http://www.opengis.net/ows/1.1"}

# What we want on the map: (key, label, words that must be in the layer id, words to avoid)
WANTED_LAYERS = [
    ("truecolor", "🛰️ MODIS true colour (daily)", ["MODIS_Terra_CorrectedReflectance_TrueColor"], []),
    ("ndvi", "🌿 MODIS NDVI", ["MODIS_Terra", "NDVI"], ["Anomaly"]),
    ("smap", "🌱 SMAP L4 root-zone soil moisture", ["SMAP_L4", "Root_Zone"], ["Uncertainty", "Anomaly"]),
    ("imerg", "🌧️ GPM IMERG precipitation rate", ["IMERG", "Precipitation_Rate"], []),
    ("lst", "🔥 MODIS land surface temperature (day)", ["MODIS_Terra_Land_Surface_Temp_Day"], []),
    ("relief", "⛰️ Shaded relief", ["Shaded_Relief"], []),
]


def load_capabilities(max_age_days=7):
    """Download the GIBS layer list (a few MB) and keep a copy for 7 days."""
    os.makedirs(config.DATA_DIR, exist_ok=True)
    fresh = os.path.exists(CACHE_FILE) and \
        (time.time() - os.path.getmtime(CACHE_FILE)) < max_age_days * 86400
    if not fresh:
        response = requests.get(CAPABILITIES_URL, timeout=120)
        response.raise_for_status()
        with open(CACHE_FILE, "wb") as f:
            f.write(response.content)
    return ET.parse(CACHE_FILE).getroot()


def parse_layers(root):
    """Return {layer_id: {"template", "matrix_set", "default_time"}}."""
    layers = {}
    for layer in root.iter(f"{{{NS['w']}}}Layer"):
        ident = layer.findtext("ows:Identifier", namespaces=NS)
        resource = layer.find("w:ResourceURL", NS)
        matrix_set = layer.findtext("w:TileMatrixSetLink/w:TileMatrixSet", namespaces=NS)
        if not ident or resource is None or not matrix_set:
            continue
        default_time = None
        for dim in layer.findall("w:Dimension", NS):
            if dim.findtext("ows:Identifier", namespaces=NS) == "Time":
                default_time = dim.findtext("w:Default", namespaces=NS)
        legend = None                                   # colour scale image (with units)
        for lg in layer.iter(f"{{{NS['w']}}}LegendURL"):
            attrs = {k.split("}")[-1]: v for k, v in lg.attrib.items()}
            if "horizontal" in attrs.get("role", "") or legend is None:
                legend = attrs.get("href")
        layers[ident] = {"template": resource.get("template"), "matrix_set": matrix_set,
                         "default_time": default_time, "legend": legend,
                         "title": layer.findtext("ows:Title", namespaces=NS) or ident}
    return layers


def max_zoom(matrix_set):
    """'GoogleMapsCompatible_Level9' -> 9"""
    try:
        return int(matrix_set.rsplit("Level", 1)[1])
    except (IndexError, ValueError):
        return 8


def tile_url(info, day=None):
    """Turn the GIBS template into a {z}/{y}/{x} URL for the map library."""
    when = info["default_time"]
    if when and day is not None:
        when = min(str(day), when[:10])         # never ask for a future image
    url = info["template"]
    url = url.replace("{Time}", when or "default")
    url = url.replace("{TileMatrixSet}", info["matrix_set"])
    url = url.replace("{TileMatrix}", "{z}").replace("{TileRow}", "{y}").replace("{TileCol}", "{x}")
    return url


def find_layers(layers):
    """Pick the best GIBS layer for each product we want."""
    found = []
    for key, label, must, avoid in WANTED_LAYERS:
        candidates = [lid for lid in layers
                      if all(m in lid for m in must) and not any(a in lid for a in avoid)]
        if candidates:
            best = min(candidates, key=len)       # the shortest id is the "best available" one
            found.append({"key": key, "label": label, "id": best, **layers[best]})
    return found
