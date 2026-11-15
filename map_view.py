"""
map_view.py - Build the interactive map (folium) for the dashboard.
"""

import math

import folium
from folium.plugins import Draw

from src.gibs import tile_url, max_zoom

# Approximate grid size of each data source, to SHOW the user what
# "one pixel" covers around the field (important limit in the document).
FOOTPRINTS = [
    ("NASA POWER cell (~50 km)", 50_000, "#888780"),
    ("GPM IMERG cell (~10 km)", 10_000, "#378ADD"),
    ("SMAP L4 cell (~9 km)", 9_000, "#3B6D11"),
    ("MODIS pixel (250 m)", 250, "#BA7517"),
]


def square(lat, lon, size_m):
    """Corners of a square of size_m metres centred on the point."""
    half = size_m / 2
    dlat = half / 111_320
    dlon = half / (111_320 * math.cos(math.radians(lat)))
    return [[lat - dlat, lon - dlon], [lat + dlat, lon + dlon]]


def build_map(lat, lon, gibs_layers, day=None, zoom=12, compare=None, field_popup=None, field_color="green",
              shown=None, opacity=0.7, show_grid=False, polygon=None):
    """
    compare = {"layer": <gibs layer>, "day_a": date, "day_b": date}  -> swipe between two dates
    field_popup = HTML shown when the field marker is clicked
    field_color = marker colour (green = ok, orange = alert)
    """
    m = folium.Map(location=[lat, lon], zoom_start=zoom, control_scale=True, tiles=None)

    # Base maps
    # (the LAST base map added is the one shown first)
    folium.TileLayer("OpenStreetMap", name="Streets (OSM)").add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery", name="Satellite (Esri)").add_to(m)

    # NASA GIBS layers (off by default, switch them on in the layer menu)
    for layer in gibs_layers:
        folium.TileLayer(
            tiles=tile_url(layer, day), attr="NASA GIBS", name=layer["label"],
            overlay=True, show=bool(shown and layer["key"] in shown), opacity=opacity,
            max_native_zoom=max_zoom(layer["matrix_set"]), max_zoom=19,
        ).add_to(m)

    # Grid footprints around the field
    for name, size, color in FOOTPRINTS:
        group = folium.FeatureGroup(name=f"▢ {name}", show=show_grid)
        folium.Rectangle(square(lat, lon, size), color=color, weight=2, fill=False,
                         tooltip=name).add_to(group)
        group.add_to(m)

    if polygon:
        folium.Polygon([[p[1], p[0]] for p in polygon], color="#FFFFFF", weight=3, fill=False,
                       tooltip="Your parcel").add_to(m)
    folium.Marker([lat, lon], tooltip="Your field (click for its values)",
                  popup=folium.Popup(field_popup, max_width=320) if field_popup else None,
                  icon=folium.Icon(color=field_color, icon="leaf")).add_to(m)

    # Compare two dates of the same NASA layer with a sliding bar
    if compare:
        from folium.plugins import SideBySideLayers
        layer = compare["layer"]
        left = folium.TileLayer(tiles=tile_url(layer, compare["day_a"]), attr="NASA GIBS",
                                name=f"{layer['label']} – {compare['day_a']}", overlay=True, opacity=0.8,
                                max_native_zoom=max_zoom(layer["matrix_set"]), max_zoom=19)
        right = folium.TileLayer(tiles=tile_url(layer, compare["day_b"]), attr="NASA GIBS",
                                 name=f"{layer['label']} – {compare['day_b']}", overlay=True, opacity=0.8,
                                 max_native_zoom=max_zoom(layer["matrix_set"]), max_zoom=19)
        left.add_to(m)
        right.add_to(m)
        SideBySideLayers(layer_left=left, layer_right=right).add_to(m)

    Draw(export=False, draw_options={"polyline": False, "circle": False, "marker": False,
                                     "circlemarker": False}).add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)       # click the ☰ icon to open
    return m


def polygon_info(geojson):
    """Area (hectares) and centre of a drawn polygon / rectangle."""
    coords = geojson["geometry"]["coordinates"][0]           # [[lon, lat], ...]
    if len(coords) > 1 and coords[0] == coords[-1]:
        coords = coords[:-1]                                   # last point repeats the first
    lat0 = sum(c[1] for c in coords) / len(coords)
    lon0 = sum(c[0] for c in coords) / len(coords)
    k = 111_320
    pts = [((c[0] - lon0) * k * math.cos(math.radians(lat0)), (c[1] - lat0) * k) for c in coords]
    area = abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))) / 2
    return {"area_ha": area / 10_000, "lat": lat0, "lon": lon0}
