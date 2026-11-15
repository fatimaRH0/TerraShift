"""
history.py - Compare the recent period with the past years ("is this year normal?").
Functions 3 and 4 of the document: compare with a historical reference and
detect unusual variations.

Main ideas (simple statistics):
  - normal (mean) and spread (standard deviation) for each calendar month
  - anomaly = value - normal
  - z-score = anomaly / spread     ->  |z| > 1 unusual, |z| > 2 very unusual
"""

import pandas as pd

from src import config
from src.nasa_power import get_field_data

# How each variable is summarised per month
MONTHLY_RULES = {
    "PRECTOTCORR": "sum",      # rain: monthly total (mm)
    "T2M": "mean",             # mean temperature (°C)
    "T2M_MAX": "mean",         # mean of daily max temperature (°C)
    "GWETROOT": "mean",        # root-zone wetness (0-1)
}
LABELS = {
    "PRECTOTCORR": "Rainfall (mm/month)",
    "T2M": "Mean temperature (°C)",
    "T2M_MAX": "Max temperature (°C)",
    "GWETROOT": "Root-zone wetness (0-1)",
}


def get_long_history(lat, lon, field_name, years=10):
    """Download (or read from cache) `years` + 1 years of daily POWER data."""
    return get_field_data(lat, lon, f"{field_name}_history", num_days=365 * (years + 1))


def monthly_table(df):
    """One row per month (e.g. 2025-03), one column per variable."""
    months = df.resample("MS").agg(MONTHLY_RULES)
    # A month needs at least 25 days of data to be counted
    days = df["T2M"].resample("MS").count()
    return months[days >= 25]


def climatology(monthly, recent_months=12):
    """Normal and spread for each calendar month, WITHOUT the recent months."""
    reference = monthly.iloc[:-recent_months] if len(monthly) > recent_months else monthly
    grouped = reference.groupby(reference.index.month)
    return grouped.mean(), grouped.std()


def compare_recent(monthly, recent_months=12):
    """Table comparing each of the last months with its normal."""
    normal, spread = climatology(monthly, recent_months)
    recent = monthly.iloc[-recent_months:]
    rows = []
    for month_start, values in recent.iterrows():
        m = month_start.month
        row = {"month": month_start}
        for var in MONTHLY_RULES:
            value, mean, std = values[var], normal.loc[m, var], spread.loc[m, var]
            row[var] = value
            row[f"{var}_normal"] = mean
            row[f"{var}_z"] = (value - mean) / std if std and std > 0 else 0.0
        rows.append(row)
    return pd.DataFrame(rows).set_index("month")


def describe_z(z):
    if z <= -2:
        return "🔴 much lower than normal"
    if z <= -1:
        return "🟠 lower than normal"
    if z >= 2:
        return "🔴 much higher than normal"
    if z >= 1:
        return "🟠 higher than normal"
    return "🟢 normal"


def anomalies(comparison):
    """List of unusual months (|z| >= 1), most unusual first."""
    found = []
    for month, row in comparison.iterrows():
        for var in MONTHLY_RULES:
            z = row[f"{var}_z"]
            if abs(z) >= 1:
                found.append({"Month": month.strftime("%b %Y"), "Variable": LABELS[var],
                              "Value": round(row[var], 2), "Normal": round(row[f"{var}_normal"], 2),
                              "z-score": round(z, 1), "Status": describe_z(z)})
    return pd.DataFrame(found).sort_values("z-score", key=abs, ascending=False) if found else pd.DataFrame()


def yearly_rain_ranking(df):
    """Rain of the last 12 months compared with each previous 12-month window."""
    totals = []
    end = df.index.max()
    while end - pd.DateOffset(years=1) >= df.index.min():
        start = end - pd.DateOffset(years=1)
        totals.append((start, end, df.loc[(df.index > start) & (df.index <= end), "PRECTOTCORR"].sum()))
        end = start
    ranking = pd.DataFrame(totals, columns=["start", "end", "rain_mm"])
    current = ranking.iloc[0]["rain_mm"]
    rank = int((ranking["rain_mm"] < current).sum()) + 1           # 1 = driest
    return ranking, current, rank


def drought_days(df, threshold=config.DRY_SOIL_THRESHOLD):
    """Number of days per year with root-zone wetness below the drought threshold."""
    dry = df["GWETROOT"] < threshold
    return dry.groupby(df.index.year).sum()
