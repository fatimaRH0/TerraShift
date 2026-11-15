"""
web_charts.py - Interactive charts (Plotly) for the Streamlit dashboard.
Unlike matplotlib, Plotly charts let you zoom and hover to read values.
"""

import plotly.graph_objects as go

from src import config


def _layout(fig, title, y_title):
    fig.update_layout(
        title=dict(text=title, font=dict(family="Bricolage Grotesque, sans-serif", size=17, color="#1F2A24")),
        yaxis_title=y_title,
        height=320,
        margin=dict(l=10, r=10, t=55, b=10),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.12, x=1, xanchor="right"),
        font=dict(family="IBM Plex Sans, sans-serif", color="#4F5E55"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, linecolor="#C9D3C4")
    fig.update_yaxes(gridcolor="#E1E7DD", zeroline=False)
    return fig


def temperature_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["T2M"], name="Mean temp", line=dict(color="#C8912E")))
    fig.add_trace(go.Scatter(x=df.index, y=df["T2M_MAX"], name="Max temp",
                             line=dict(color="#EF9F27", width=1), opacity=0.7))
    fig.add_hline(y=config.HEAT_THRESHOLD, line_dash="dash", line_color="red",
                  annotation_text="Heat stress")
    return _layout(fig, "🌡️ Temperature", "°C")


def rain_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df["PRECTOTCORR"], name="Rain", marker_color="#2E6F9E"))
    return _layout(fig, "🌧️ Precipitation", "mm/day")


def soil_moisture_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["GWETTOP"], name="Surface", line=dict(color="#8DB580")))
    fig.add_trace(go.Scatter(x=df.index, y=df["GWETROOT"], name="Root zone", line=dict(color="#2F6B4F")))
    fig.add_hline(y=config.DRY_SOIL_THRESHOLD, line_dash="dash", line_color="red",
                  annotation_text="Drought threshold")
    fig.update_yaxes(range=[0, 1])
    return _layout(fig, "🌱 Soil moisture", "0 = dry, 1 = saturated")


def humidity_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RH2M"], name="Air humidity", line=dict(color="#1D9E75")))
    return _layout(fig, "💧 Air humidity", "%")


# =========================================================
# Satellite charts
# =========================================================
def smap_chart(smap):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=smap.index, y=smap["sm_surface"], name="Surface 0–5 cm",
                             line=dict(color="#8DB580")))
    fig.add_trace(go.Scatter(x=smap.index, y=smap["sm_rootzone"], name="Root zone 0–100 cm",
                             line=dict(color="#2F6B4F")))
    return _layout(fig, "🛰️ SMAP L4 soil moisture (daily mean)", "m³/m³")


def rain_compare_chart(power_df, gpm=None, smap=None):
    """Monthly rainfall totals from the different NASA sources."""
    fig = go.Figure()
    monthly = power_df["PRECTOTCORR"].resample("MS").sum()
    fig.add_trace(go.Bar(x=monthly.index, y=monthly, name="NASA POWER", marker_color="#B4B2A9"))
    if gpm is not None and "rain_gpm_mm" in gpm:
        m = gpm["rain_gpm_mm"].resample("MS").sum(min_count=1)
        fig.add_trace(go.Bar(x=m.index, y=m, name="GPM IMERG", marker_color="#2E6F9E"))
    if smap is not None and "rain_smap_mm" in smap:
        m = smap["rain_smap_mm"].resample("MS").sum(min_count=1)
        fig.add_trace(go.Bar(x=m.index, y=m, name="SMAP forcing", marker_color="#7F77DD"))
    fig.update_layout(barmode="group")
    return _layout(fig, "🌧️ Monthly rainfall by source", "mm/month")


def gpm_chart(gpm):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=gpm.index, y=gpm["rain_gpm_mm"], name="GPM IMERG", marker_color="#2E6F9E"))
    return _layout(fig, "🛰️ GPM IMERG daily precipitation", "mm/day")


def vegetation_chart(modis=None, landsat=None):
    fig = go.Figure()
    if modis is not None:
        fig.add_trace(go.Scatter(x=modis.index, y=modis["ndvi"], name="NDVI MODIS (250 m)",
                                 mode="lines+markers", line=dict(color="#2F6B4F")))
        if "evi" in modis:
            fig.add_trace(go.Scatter(x=modis.index, y=modis["evi"], name="EVI MODIS",
                                     mode="lines+markers", line=dict(color="#8DB580", dash="dot")))
    if landsat is not None:
        fig.add_trace(go.Scatter(x=landsat.index, y=landsat["ndvi_landsat"],
                                 name="NDVI Landsat C2 (30 m)", mode="markers",
                                 marker=dict(color="#BA7517", size=7)))
    fig.update_yaxes(range=[-0.1, 1])
    return _layout(fig, "🌿 Vegetation index", "NDVI / EVI")


def ecostress_chart(eco=None, power_df=None, landsat=None):
    fig = go.Figure()
    if power_df is not None:
        fig.add_trace(go.Scatter(x=power_df.index, y=power_df["T2M_MAX"], name="Air max (POWER)",
                                 line=dict(color="#D3D1C7", width=1)))
    if eco is not None:
        if "period" in eco:
            for period, color in (("day", "#C8912E"), ("night/evening", "#534AB7")):
                part = eco[eco["period"] == period]
                fig.add_trace(go.Scatter(x=part.index, y=part["lst_c"], mode="markers",
                                         name=f"ECOSTRESS {period} (~70 m)",
                                         marker=dict(color=color, size=8)))
        else:
            fig.add_trace(go.Scatter(x=eco.index, y=eco["lst_c"], name="Surface (ECOSTRESS, ~70 m)",
                                     mode="markers", marker=dict(color="#C8912E", size=8)))
    if landsat is not None and "lst_landsat_c" in landsat:
        fig.add_trace(go.Scatter(x=landsat.index, y=landsat["lst_landsat_c"],
                                 name="Surface (Landsat C2, 30 m)", mode="markers",
                                 marker=dict(color="#7F77DD", size=8, symbol="diamond")))
    return _layout(fig, "🔥 Land surface temperature", "°C")


# =========================================================
# Historical comparison charts
# =========================================================
def monthly_vs_normal_chart(comparison, var, title, unit, color):
    """Bars = this period, line = normal for the same months."""
    x = comparison.index
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=comparison[var], name="Recent months", marker_color=color))
    fig.add_trace(go.Scatter(x=x, y=comparison[f"{var}_normal"], name="Normal (past years)",
                             mode="lines+markers", line=dict(color="#444441", dash="dash")))
    return _layout(fig, title, unit)


def zscore_heatmap(comparison, labels):
    variables = list(labels)
    z = [[comparison[f"{v}_z"].iloc[i] for i in range(len(comparison))] for v in variables]
    fig = go.Figure(go.Heatmap(
        z=z, x=[d.strftime("%b %Y") for d in comparison.index], y=[labels[v] for v in variables],
        colorscale="RdBu", zmid=0, zmin=-3, zmax=3, colorbar=dict(title="z"),
        text=[[f"{val:+.1f}" for val in row] for row in z], texttemplate="%{text}"))
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10),
                      title="How unusual was each month? (z-score: blue = below normal, red = above)")
    return fig


def yearly_rain_chart(ranking):
    labels = [f"{s:%b %Y}–{e:%b %Y}" for s, e in zip(ranking["start"], ranking["end"])]
    colors = ["#C8912E"] + ["#B4B2A9"] * (len(ranking) - 1)
    fig = go.Figure(go.Bar(x=labels[::-1], y=ranking["rain_mm"][::-1], marker_color=colors[::-1]))
    fig.add_hline(y=ranking["rain_mm"].mean(), line_dash="dash", annotation_text="average")
    return _layout(fig, "🌧️ 12-month rainfall: last 12 months (orange) vs previous years", "mm")


def drought_days_chart(days):
    fig = go.Figure(go.Bar(x=days.index.astype(str), y=days.values, marker_color="#BA7517"))
    return _layout(fig, "🏜️ Days per year with root-zone wetness below the drought threshold", "days")


# =========================================================
# Machine learning charts
# =========================================================
def importance_chart(importance, labels):
    imp = importance.sort_values()
    fig = go.Figure(go.Bar(x=imp.values, y=[labels[i] for i in imp.index], orientation="h",
                           marker_color="#7F77DD"))
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10),
                      title="🔎 What the model looks at most (feature importance)")
    return fig


def risk_timeline_chart(test):
    fig = go.Figure()
    dry = test[test["actual"] == 1]
    fig.add_trace(go.Bar(x=dry.index, y=[1] * len(dry), name="Actually unusually dry",
                         marker_color="rgba(186,117,23,0.35)", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=test.index, y=test["probability"], name="Model probability",
                             line=dict(color="#534AB7")))
    fig.add_hline(y=0.6, line_dash="dash", line_color="red", annotation_text="high risk")
    fig.add_hline(y=0.3, line_dash="dot", line_color="orange", annotation_text="medium")
    fig.update_yaxes(range=[0, 1])
    fig.update_layout(bargap=0)
    return _layout(fig, "🧪 Test year: what the model predicted vs what happened", "probability")


# =========================================================
# Crops & scenarios charts
# =========================================================
def crop_needs_chart(summary):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=summary["Crop"], y=summary["Effective rain (mm)"], name="Covered by rain",
                         marker_color="#2E6F9E"))
    fig.add_trace(go.Bar(x=summary["Crop"], y=summary["Irrigation – normal year (mm)"],
                         name="Irrigation needed (normal year)", marker_color="#EF9F27"))
    fig.add_trace(go.Scatter(x=summary["Crop"], y=summary["Irrigation – dry year (mm)"],
                             name="Irrigation needed (dry year)", mode="markers",
                             marker=dict(color="#A32D2D", size=11, symbol="diamond")))
    fig.update_layout(barmode="stack")
    return _layout(fig, "💧 Water needs per crop season", "mm per season")


def scenario_chart(table, weights):
    total = sum(weights.values()) or 1
    fig = go.Figure()
    for col, label, color in (("water_score", "Water", "#2E6F9E"), ("risk_score", "Risk", "#C8912E"),
                              ("agronomy", "Rotation", "#2F6B4F")):
        key = {"water_score": "water", "risk_score": "risk", "agronomy": "rotation"}[col]
        fig.add_trace(go.Bar(y=table["Scenario"], x=table[col] * weights[key] / total, name=label,
                             orientation="h", marker_color=color))
    fig.update_layout(barmode="stack", height=60 + 45 * len(table),
                      margin=dict(l=10, r=10, t=50, b=10), yaxis=dict(autorange="reversed"),
                      title="🏆 Final score (longer = better) and what it is made of")
    return fig
