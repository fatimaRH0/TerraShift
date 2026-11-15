"""
indicators.py - Compute simple indicators and alerts from the data.
These functions RETURN results instead of printing them,
so they can be reused later in the web dashboard (Step 3).
"""

from src import config


def compute_indicators(df, days=30):
    """Summarise the last `days` days and compare them to the whole period."""
    recent = df.tail(days)
    return {
        "rain_recent": recent["PRECTOTCORR"].sum(),
        "rain_normal": df["PRECTOTCORR"].mean() * days,   # what is "normal"
        "root_moisture": recent["GWETROOT"].mean(),
        "surface_moisture": recent["GWETTOP"].mean(),
        "max_temp": recent["T2M_MAX"].max(),
        "mean_temp": recent["T2M"].mean(),
        "days": days,
    }


def default_thresholds():
    return {"dry_soil": config.DRY_SOIL_THRESHOLD, "low_rain": config.LOW_RAIN_RATIO,
            "heat": config.HEAT_THRESHOLD}


def compute_alerts(ind, thresholds=None):
    """Return alert messages. Thresholds can be changed by the user (sidebar)."""
    t = thresholds or default_thresholds()
    alerts = []
    if ind["root_moisture"] < t["dry_soil"]:
        alerts.append(f"Low soil moisture: root-zone wetness {ind['root_moisture']:.2f} "
                      f"is below your threshold {t['dry_soil']:.2f}")
    if ind["rain_recent"] < t["low_rain"] * ind["rain_normal"]:
        alerts.append(f"Low rainfall: {ind['rain_recent']:.0f} mm, less than "
                      f"{t['low_rain']:.0%} of the usual {ind['rain_normal']:.0f} mm")
    if ind["max_temp"] > t["heat"]:
        alerts.append(f"Heat stress: maximum temperature {ind['max_temp']:.1f} °C "
                      f"is above your threshold {t['heat']:.0f} °C")
    return alerts
