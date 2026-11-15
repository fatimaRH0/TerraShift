"""
location.py - Start the app at the USER'S position instead of fixed coordinates.

Two ways, the best one wins:
  1. Browser GPS / location (asks the user's permission, precise).
  2. Approximate position from the internet address (city level), used until
     the browser answers, or if the user refuses the GPS permission.
If both fail, the default coordinates of src/config.py are used.
"""

import requests


# Free services that give an approximate position from the internet address.
# Several are tried, because any one of them can be blocked or busy.
IP_SERVICES = [
    # (url for "my own address", url for a given address, how to read the answer)
    ("https://ipwho.is/", "https://ipwho.is/{ip}",
     lambda d: (d.get("latitude"), d.get("longitude"), d.get("city", ""))),
    ("https://ipapi.co/json/", "https://ipapi.co/{ip}/json/",
     lambda d: (d.get("latitude"), d.get("longitude"), d.get("city", ""))),
    ("http://ip-api.com/json/", "http://ip-api.com/json/{ip}",
     lambda d: (d.get("lat"), d.get("lon"), d.get("city", ""))),
    ("https://get.geojs.io/v1/ip/geo.json", "https://get.geojs.io/v1/ip/geo/{ip}.json",
     lambda d: (d.get("latitude"), d.get("longitude"), d.get("city", ""))),
]


def ip_location(client_ip=None):
    """Approximate (city-level) position from the internet address. Returns (lat, lon, city) or None."""
    local = client_ip in (None, "", "127.0.0.1", "::1", "localhost") or str(client_ip).startswith(("192.168.", "10."))
    for own_url, ip_url, read in IP_SERVICES:
        url = own_url if local else ip_url.format(ip=client_ip)
        try:
            data = requests.get(url, timeout=4, headers={"User-Agent": "TerraShift"}).json()
            lat, lon, city = read(data)
            if lat is not None and lon is not None:
                return float(lat), float(lon), city
        except (requests.exceptions.RequestException, ValueError, TypeError):
            continue
    return None


def browser_location():
    """
    Ask the browser for the GPS position (the user sees a permission prompt).
    Returns (lat, lon), "denied", or None while waiting for the answer.
    """
    try:
        from streamlit_js_eval import get_geolocation
    except ImportError:
        return "denied"
    loc = get_geolocation()
    if not loc:
        return None
    if "coords" in loc:
        return float(loc["coords"]["latitude"]), float(loc["coords"]["longitude"])
    return "denied"


# ---------------------------------------------------------
# Find a place by its NAME (village, town, region) - free services, no key.
# ---------------------------------------------------------
HEADERS = {"User-Agent": "TerraShift/1.0 (NASA Space Apps student project)"}


def search_place(text, limit=6):
    """Return a list of {"name", "lat", "lon"} for a place name, best match first."""
    text = text.strip()
    if len(text) < 2:
        return []
    # 1. OpenStreetMap Nominatim: knows small villages and douars
    try:
        rows = requests.get("https://nominatim.openstreetmap.org/search",
                            params={"q": text, "format": "json", "limit": limit, "accept-language": "en"},
                            headers=HEADERS, timeout=6).json()
        found = [{"name": r["display_name"], "lat": float(r["lat"]), "lon": float(r["lon"])} for r in rows]
        if found:
            return found
    except (requests.exceptions.RequestException, ValueError, KeyError):
        pass
    # 2. Open-Meteo geocoding: towns and cities
    try:
        rows = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                            params={"name": text, "count": limit, "language": "en"},
                            headers=HEADERS, timeout=6).json().get("results", [])
        return [{"name": ", ".join(x for x in (r.get("name"), r.get("admin1"), r.get("country")) if x),
                 "lat": float(r["latitude"]), "lon": float(r["longitude"])} for r in rows]
    except (requests.exceptions.RequestException, ValueError, KeyError):
        return []


def place_name(lat, lon):
    """Short name of the place at these coordinates (e.g. 'Sidi Kaouki, Essaouira'), or None."""
    try:
        r = requests.get("https://nominatim.openstreetmap.org/reverse",
                         params={"lat": lat, "lon": lon, "format": "json", "zoom": 12, "accept-language": "en"},
                         headers=HEADERS, timeout=6).json()
        a = r.get("address", {})
        local = a.get("village") or a.get("town") or a.get("city") or a.get("municipality") or a.get("county")
        region = a.get("state") or a.get("region")
        return ", ".join(x for x in (local, region) if x) or r.get("display_name")
    except (requests.exceptions.RequestException, ValueError):
        return None
