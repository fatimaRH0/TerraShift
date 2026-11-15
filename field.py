"""
field.py - The field shape (polygon) and its division into virtual zones.
Polygons are lists of [longitude, latitude] points.
"""

import math


def square_polygon(lat, lon, size_m=400):
    """Default field: a square of size_m metres around the point."""
    half = size_m / 2
    dlat = half / 111_320
    dlon = half / (111_320 * math.cos(math.radians(lat)))
    return [[lon - dlon, lat - dlat], [lon + dlon, lat - dlat],
            [lon + dlon, lat + dlat], [lon - dlon, lat + dlat]]


def bbox(polygon):
    lons = [p[0] for p in polygon]
    lats = [p[1] for p in polygon]
    return min(lons), min(lats), max(lons), max(lats)


def contains(polygon, lon, lat):
    """Is the point inside the polygon? (ray-casting algorithm)"""
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def size_km(polygon):
    lon0, lat0, lon1, lat1 = bbox(polygon)
    width = (lon1 - lon0) * 111.32 * math.cos(math.radians((lat0 + lat1) / 2))
    height = (lat1 - lat0) * 111.32
    return width, height


def grid_zones(polygon, rows=3, cols=3):
    """Split the field's bounding box into rows x cols virtual zones."""
    lon0, lat0, lon1, lat1 = bbox(polygon)
    dlon, dlat = (lon1 - lon0) / cols, (lat1 - lat0) / rows
    zones = []
    for r in range(rows):
        for c in range(cols):
            x0, y0 = lon0 + c * dlon, lat1 - (r + 1) * dlat
            zones.append({
                "zone": f"{chr(65 + r)}{c + 1}",              # A1, A2 ... (A = north)
                "polygon": [[x0, y0], [x0 + dlon, y0], [x0 + dlon, y0 + dlat], [x0, y0 + dlat]],
                "bounds": (x0, y0, x0 + dlon, y0 + dlat),
            })
    return zones
