"""
verdict.py - Turn the indicators into a plain-language verdict for the farmer.
Each reason says what the number is and where it comes from.
"""


def build_verdict(ind=None, risk=None, root_vs_normal=None, ndvi=None, rank=None, n_years=None):
    reasons = []          # (level, text)   level: "warn" | "ok" | "info"

    if ind:
        ratio = ind["rain_recent"] / ind["rain_normal"] if ind["rain_normal"] > 0 else 1
        days = ind["days"]
        if ratio < 0.5:
            reasons.append(("warn", f"Only {ind['rain_recent']:.0f} mm of rain in the last {days} days, "
                                    f"less than half the usual {ind['rain_normal']:.0f} mm."))
        elif ratio > 1.5:
            reasons.append(("ok", f"{ind['rain_recent']:.0f} mm of rain in the last {days} days, "
                                  f"well above the usual {ind['rain_normal']:.0f} mm."))
        else:
            reasons.append(("info", f"{ind['rain_recent']:.0f} mm of rain in the last {days} days, "
                                    f"close to the usual {ind['rain_normal']:.0f} mm."))
        if ind["max_temp"] > 38:
            reasons.append(("warn", f"Heat peaks reached {ind['max_temp']:.0f} °C: risk of heat stress."))

    if root_vs_normal is not None:
        if root_vs_normal < -0.05:
            reasons.append(("warn", "The soil is drier than usual for this time of year."))
        elif root_vs_normal > 0.05:
            reasons.append(("ok", "The soil is wetter than usual for this time of year."))
        else:
            reasons.append(("info", "Soil moisture is normal for this time of year."))

    if risk:
        level = "warn" if risk["probability"] >= 0.6 else ("info" if risk["probability"] >= 0.3 else "ok")
        reasons.append((level, f"Drought risk for the next 14 days: "
                               f"{risk['level'].split(' ', 1)[-1].lower()} ({risk['probability']:.0%})."))

    if ndvi is not None:
        if ndvi < 0.2:
            reasons.append(("info", f"Vegetation index is low ({ndvi:.2f}): bare soil, stubble or sparse crop."))
        elif ndvi > 0.5:
            reasons.append(("ok", f"Vegetation is dense and green (NDVI {ndvi:.2f})."))
        else:
            reasons.append(("info", f"Vegetation is moderate (NDVI {ndvi:.2f})."))

    if rank is not None and n_years:
        if rank <= 2:
            reasons.append(("warn", f"The last 12 months are among the driest of the last {n_years} years."))
        elif rank >= n_years - 1:
            reasons.append(("ok", f"The last 12 months are among the wettest of the last {n_years} years."))

    warnings = sum(1 for lvl, _ in reasons if lvl == "warn")
    if warnings >= 2:
        headline, tone = "Watch the water: conditions are drier than usual.", "warn"
    elif warnings == 1:
        headline, tone = "Mostly normal, with one point to watch.", "info"
    elif reasons:
        headline, tone = "Conditions look normal for the season.", "ok"
    else:
        headline, tone = "Load the data to get a verdict for this field.", "info"
    return headline, tone, reasons
