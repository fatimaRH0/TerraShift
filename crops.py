"""
crops.py - Crop water needs from NASA POWER data (functions 6 and 8 of the document).

Method (FAO-56, simplified and explained):
  1. ET0  = how much water a reference grass "drinks" per day (mm/day).
            Hargreaves formula: needs only temperature + the sun's position.
  2. Kc   = crop coefficient: how thirsty the crop is compared with grass.
            It changes with the growth stage (small seedling -> full canopy -> ripening).
  3. ETc  = Kc x ET0 = water used by the crop per day.
  4. Effective rain = part of the rain the crop can actually use (here 80 %).
  5. Irrigation need = ETc - effective rain over the season (if positive).
We repeat this for every past year to see normal years AND dry years.

⚠️ Crop values are INDICATIVE (FAO-56 tables, adapted to a Mediterranean climate).
Local varieties, soil and practices change the real numbers.
"""

import numpy as np
import pandas as pd

EFFECTIVE_RAIN_SHARE = 0.8

# name: family, sowing (month, day), stage lengths in days (initial, development,
#       mid-season, late), Kc (initial, mid, end), legume = fixes nitrogen
CROPS = {
    "Wheat":     {"family": "Cereal",    "sowing": (11, 15), "stages": (30, 100, 50, 30), "kc": (0.70, 1.15, 0.25), "legume": False},
    "Barley":    {"family": "Cereal",    "sowing": (11, 15), "stages": (25, 90, 45, 30),  "kc": (0.30, 1.15, 0.25), "legume": False},
    "Chickpea":  {"family": "Legume",    "sowing": (1, 15),  "stages": (25, 35, 50, 25),  "kc": (0.40, 1.00, 0.35), "legume": True},
    "Faba bean": {"family": "Legume",    "sowing": (11, 20), "stages": (20, 40, 60, 25),  "kc": (0.50, 1.15, 0.30), "legume": True},
    "Lentil":    {"family": "Legume",    "sowing": (12, 1),  "stages": (20, 30, 60, 40),  "kc": (0.40, 1.10, 0.30), "legume": True},
    "Potato":    {"family": "Tuber",     "sowing": (2, 1),   "stages": (25, 30, 45, 30),  "kc": (0.50, 1.15, 0.75), "legume": False},
    "Tomato":    {"family": "Vegetable", "sowing": (3, 15),  "stages": (30, 40, 45, 30),  "kc": (0.60, 1.15, 0.80), "legume": False},
    "Maize":     {"family": "Cereal",    "sowing": (4, 1),   "stages": (30, 40, 50, 30),  "kc": (0.30, 1.20, 0.60), "legume": False},
    "Oat":       {"family": "Cereal",    "sowing": (11, 15), "stages": (20, 30, 60, 40),  "kc": (0.30, 1.15, 0.25), "legume": False},
    "Sorghum":   {"family": "Cereal",    "sowing": (5, 1),   "stages": (20, 35, 40, 30),  "kc": (0.30, 1.00, 0.55), "legume": False},
    "Pea":       {"family": "Legume",    "sowing": (11, 15), "stages": (15, 25, 35, 15),  "kc": (0.50, 1.15, 0.30), "legume": True},
    "Peanut":    {"family": "Legume",    "sowing": (4, 15),  "stages": (25, 35, 45, 25),  "kc": (0.40, 1.15, 0.60), "legume": True},
    "Pepper":    {"family": "Vegetable", "sowing": (3, 15),  "stages": (30, 35, 40, 20),  "kc": (0.60, 1.05, 0.90), "legume": False},
    "Onion":     {"family": "Allium",    "sowing": (11, 1),  "stages": (15, 25, 70, 40),  "kc": (0.70, 1.05, 0.75), "legume": False},
    "Carrot":    {"family": "Root crop", "sowing": (9, 15),  "stages": (20, 30, 50, 20),  "kc": (0.70, 1.05, 0.95), "legume": False},
    "Sugar beet": {"family": "Root crop", "sowing": (10, 15), "stages": (25, 35, 50, 50), "kc": (0.35, 1.20, 0.70), "legume": False},
    "Sunflower": {"family": "Oilseed",   "sowing": (3, 1),   "stages": (25, 35, 45, 25),  "kc": (0.35, 1.10, 0.35), "legume": False},
    "Rapeseed":  {"family": "Brassica",  "sowing": (10, 25), "stages": (30, 40, 60, 40),  "kc": (0.35, 1.10, 0.35), "legume": False},
    "Melon":     {"family": "Cucurbit",  "sowing": (3, 15),  "stages": (25, 35, 40, 20),  "kc": (0.50, 0.85, 0.60), "legume": False},
    "Watermelon": {"family": "Cucurbit", "sowing": (3, 15),  "stages": (20, 30, 30, 30),  "kc": (0.40, 1.00, 0.75), "legume": False},
    "Fallow":    {"family": "Fallow",    "sowing": (11, 15), "stages": (60, 60, 60, 60),  "kc": (0.00, 0.00, 0.00), "legume": False},
}


# ---------------------------------------------------------
# 1) Reference evapotranspiration ET0 (Hargreaves, FAO-56 eq. 52)
# ---------------------------------------------------------
def extraterrestrial_radiation(day_of_year, latitude):
    """Sun energy at the top of the atmosphere (FAO-56 eq. 21), in mm/day of evaporation."""
    j = np.asarray(day_of_year, dtype=float)
    phi = np.radians(latitude)
    dr = 1 + 0.033 * np.cos(2 * np.pi * j / 365)
    delta = 0.409 * np.sin(2 * np.pi * j / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(phi) * np.tan(delta), -1, 1))
    ra = (24 * 60 / np.pi) * 0.0820 * dr * (ws * np.sin(phi) * np.sin(delta)
                                            + np.cos(phi) * np.cos(delta) * np.sin(ws))
    return 0.408 * ra                                   # MJ/m²/day -> mm/day


def et0_hargreaves(df, latitude):
    tmax, tmean = df["T2M_MAX"], df["T2M"]
    # NASA POWER T2M_MIN is not downloaded: estimate it from mean and max
    tmin = df["T2M_MIN"] if "T2M_MIN" in df else 2 * tmean - tmax
    ra = extraterrestrial_radiation(df.index.dayofyear, latitude)
    et0 = 0.0023 * (tmean + 17.8) * np.sqrt((tmax - tmin).clip(lower=0)) * ra
    return pd.Series(et0, index=df.index).clip(lower=0)


# ---------------------------------------------------------
# 2) Crop coefficient curve
# ---------------------------------------------------------
def kc_curve(crop):
    """Daily Kc values for the whole season (FAO-56 figure 25)."""
    ini, dev, mid, late = CROPS[crop]["stages"]
    kc_ini, kc_mid, kc_end = CROPS[crop]["kc"]
    return np.concatenate([
        np.full(ini, kc_ini),
        np.linspace(kc_ini, kc_mid, dev),
        np.full(mid, kc_mid),
        np.linspace(kc_mid, kc_end, late),
    ])


def season_length(crop):
    return sum(CROPS[crop]["stages"])


# ---------------------------------------------------------
# 3-5) Water balance for every past season
# ---------------------------------------------------------
def seasons_table(df, crop, latitude):
    """One row per past season: ETc, effective rain, irrigation need, rain coverage."""
    et0 = et0_hargreaves(df, latitude)
    rain = df["PRECTOTCORR"]
    kc = kc_curve(crop)
    month, day = CROPS[crop]["sowing"]
    rows = []
    for year in range(df.index.min().year, df.index.max().year + 1):
        start = pd.Timestamp(year=year, month=month, day=day)
        days = pd.date_range(start, periods=len(kc))
        if days[0] < df.index.min() or days[-1] > df.index.max():
            continue                                   # season not fully covered by data
        etc = (kc * et0.loc[days].values).sum()
        eff_rain = EFFECTIVE_RAIN_SHARE * rain.loc[days].sum()
        rows.append({"season": f"{days[0]:%Y}-{days[-1]:%y}", "sowing": days[0], "harvest": days[-1],
                     "etc_mm": etc, "rain_mm": rain.loc[days].sum(), "eff_rain_mm": eff_rain,
                     "irrigation_mm": max(0.0, etc - eff_rain),
                     "coverage": min(1.0, eff_rain / etc) if etc > 0 else 1.0})
    return pd.DataFrame(rows)


def crop_summary(df, latitude, crops=None):
    """Median (normal year) and 80th percentile (dry year, 1 year in 5) for each crop."""
    rows = []
    for crop in crops or CROPS:
        t = seasons_table(df, crop, latitude)
        if t.empty:
            continue
        month, day = CROPS[crop]["sowing"]
        rows.append({
            "Crop": crop, "Family": CROPS[crop]["family"],
            "Sowing": pd.Timestamp(2000, month, day).strftime("%d %b"),
            "Days": season_length(crop),
            "Crop water use (mm)": t["etc_mm"].median(),
            "Effective rain (mm)": t["eff_rain_mm"].median(),
            "Irrigation – normal year (mm)": t["irrigation_mm"].median(),
            "Irrigation – dry year (mm)": t["irrigation_mm"].quantile(0.8),
            "Rain covers (%)": 100 * t["coverage"].median(),
            "Seasons analysed": len(t),
        })
    return pd.DataFrame(rows)
