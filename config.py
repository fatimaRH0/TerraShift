"""
config.py - All project settings in one place.
Change values here instead of editing the other files.
"""

# ---- Field location ----
FIELD_NAME = "My field"
LATITUDE = 33.90     # example: farmland near Meknes
LONGITUDE = -5.55

# ---- Time period ----
NUM_DAYS = 365       # how many days of history to download
NASA_DELAY_DAYS = 3  # NASA POWER publishes data with a few days of delay

# ---- Folders ----
DATA_DIR = "data"

# ---- NASA POWER API ----
API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

# T2M         : mean temperature at 2 m (°C)
# T2M_MAX     : maximum temperature (°C)
# PRECTOTCORR : precipitation (mm/day)
# RH2M        : relative air humidity (%)
# GWETTOP     : surface soil wetness (0 = dry, 1 = saturated)
# GWETROOT    : root-zone soil wetness (0 = dry, 1 = saturated)
PARAMETERS = ["T2M", "T2M_MAX", "PRECTOTCORR", "RH2M", "GWETTOP", "GWETROOT"]

# ---- Alert thresholds ----
DRY_SOIL_THRESHOLD = 0.3     # root-zone wetness below this = drought risk
LOW_RAIN_RATIO = 0.5         # rain below 50% of normal = rainfall deficit
HEAT_THRESHOLD = 38          # max temperature above this = heat stress


# =========================================================
# Satellite products (from the TerraShift functional document)
# Downloaded with:  python download_satellite.py
# =========================================================

# Earthdata login: you can set these environment variables,
# otherwise the script asks for them when it runs.
EARTHDATA_USER_ENV = "EARTHDATA_USERNAME"
EARTHDATA_PASS_ENV = "EARTHDATA_PASSWORD"

# Products downloaded through NASA AppEEARS (point samples).
# "product" = short name; the newest version is found automatically.
# "layers"  = layer names we want (matched against the real AppEEARS names).
APPEEARS_PRODUCTS = {
    "smap": {
        "product": "SPL4SMGP",
        "version": "007",          # version linked in the document (nsidc.org/data/spl4smgp/versions/7)
        "layers": ["sm_surface", "sm_rootzone", "precipitation_total_surface_flux"],
        "label": "SMAP L4 – soil moisture (~9 km, 3-hourly)",
    },
    "modis": {
        "product": "MOD13Q1",
        "layers": ["_250m_16_days_NDVI", "_250m_16_days_EVI"],
        "label": "MODIS MOD13Q1 – NDVI / EVI (250 m, 16 days)",
    },
    "ecostress": {
        "product": "ECO_L2T_LSTE",
        "layers": ["LST"],
        "label": "ECOSTRESS L2 LSTE – surface temperature (70 m, irregular)",
    },
    "srtm": {
        "product": "SRTMGL1_NC",
        "layers": ["SRTMGL1_DEM"],
        "label": "SRTM – elevation (30 m)",
    },
}

# Landsat Collection 2 Level-2 (USGS science products: surface reflectance
# + surface temperature), read from the free Microsoft Planetary Computer mirror.
LANDSAT_COLLECTION = "landsat-c2-l2"
LANDSAT_MAX_CLOUD = 60       # skip scenes with more than 60% clouds
LANDSAT_LABEL = "Landsat Collection 2 Level-2 – reflectance → NDVI + surface temperature (30 m)"

# GPM IMERG precipitation (GES DISC "data rods" time-series service)
GPM_LABEL = "GPM IMERG Final – precipitation (~10 km)"


# Official pages linked in the TerraShift functional document
SOURCE_LINKS = {
    "power": "https://power.larc.nasa.gov/docs/services/api/temporal/daily/",
    "smap": "https://nsidc.org/data/spl4smgp/versions/7",
    "gpm": "https://gpm.nasa.gov/data/directory",
    "modis": "https://modis.gsfc.nasa.gov/data/dataprod/mod13.php",
    "ecostress": "https://ecostress.jpl.nasa.gov/data/",
    "landsat": "https://www.usgs.gov/landsat-missions/landsat-science-products",
    "srtm": "https://www.earthdata.nasa.gov/s3fs-public/2025-05/SRTM_Quick_Guide.pdf",
    "grace": "https://earth.gsfc.nasa.gov/hydro/missions/gravity-recovery-and-climate-experiment-follow-mission-grace-fo",
}
