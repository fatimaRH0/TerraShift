"""
TerraShift - Dashboard
------------------------
Run:
    streamlit run app.py
Weather comes live from NASA POWER.
Satellite data (SMAP, GPM, MODIS, Landsat, ECOSTRESS, SRTM) is read from data/
after running:  python download_satellite.py
"""

import importlib
import sys

import pandas as pd
import streamlit as st

# Development only (a local "venv" folder exists): reload our own modules (src/...) on every
# run, so changes to src/ files show after a page refresh. Skipped when the app is hosted,
# where reloading on each visit would be slow and unsafe with several users.
import os as _os
if _os.path.isdir(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "venv")):
    for _name in sorted((m for m in list(sys.modules) if m == "src" or m.startswith("src.")),
                        key=lambda m: (m != "src.config", m.count("."), m)):
        try:
            importlib.reload(sys.modules[_name])
        except Exception:
            pass

from src import config
from src.nasa_power import get_field_data, NasaConnectionError
from src.indicators import compute_indicators, compute_alerts
from src.satellite import load_satellite_for
from src.web_charts import (temperature_chart, rain_chart, soil_moisture_chart, humidity_chart,
                            smap_chart, rain_compare_chart, gpm_chart, vegetation_chart,
                            ecostress_chart)

from src import style, verdict, glossary, cards, i18n
from src.i18n import t, tr

from pathlib import Path as _Path
st.set_page_config(page_title="TerraShift", page_icon=str(_Path(__file__).parent / "assets" / "icon.png"),
                   layout="wide")
style.inject()
st.session_state.setdefault("lang", "en")
st.markdown(i18n.css(), unsafe_allow_html=True)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
# The field position lives in st.session_state so the MAP can change it.
# Default position = the USER'S position (browser GPS, else internet address, else config).
from src import location as _loc

if "lat" not in st.session_state:
    client_ip = getattr(getattr(st, "context", None), "ip_address", None)
    approx = _loc.ip_location(client_ip)
    if approx:
        st.session_state.lat, st.session_state.lon = round(approx[0], 4), round(approx[1], 4)
        st.session_state.location_source = f"approximate, from your internet connection ({approx[2]})"
    else:
        st.session_state.lat, st.session_state.lon = config.LATITUDE, config.LONGITUDE
        st.session_state.location_source = "default position (src/config.py)"

if not st.session_state.get("gps_done"):
    gps = _loc.browser_location()            # None while the browser has not answered yet
    if gps == "denied":
        st.session_state.gps_done = True
    elif gps:
        st.session_state.lat, st.session_state.lon = round(gps[0], 4), round(gps[1], 4)
        st.session_state.location_source = "your device location (GPS)"
        st.session_state.gps_done = True

st.session_state.setdefault("field_name", config.FIELD_NAME)


def use_my_location():
    """Ask the browser again for the user's position."""
    st.session_state.gps_done = False


def go_to_place():
    """Called when the user picks a place found by name."""
    place = st.session_state.get("place_pick")
    if place:
        st.session_state.lat = round(place["lat"], 4)
        st.session_state.lon = round(place["lon"], 4)
        st.session_state.location_source = "the place you searched"


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def find_places(text):
    return _loc.search_place(text)


@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def name_of(lat, lon):
    return _loc.place_name(lat, lon)


def use_demo_field():
    """The field near Meknes whose SMAP, ECOSTRESS, MODIS, Landsat and SRTM data are already downloaded."""
    st.session_state.lat, st.session_state.lon = config.LATITUDE, config.LONGITUDE
    st.session_state.location_source = "demo field (all NASA data already downloaded)"
    st.session_state.gps_done = True


def use_point(lat, lon):
    """Called when the user clicks '📍 Use this point' on the map."""
    st.session_state.lat = round(lat, 4)
    st.session_state.lon = round(lon, 4)


style.sidebar_brand()
with st.sidebar:
    st.header(t("your_field"))
    _here = name_of(round(st.session_state.lat, 3), round(st.session_state.lon, 3))
    st.markdown(f"📍 **{_here or t('your_field')}**", unsafe_allow_html=True)
    _c1, _c2 = st.columns(2)
    _c1.markdown(f"<small>{t('latitude')}</small><br><b>{st.session_state.lat:.4f}</b>", unsafe_allow_html=True)
    _c2.markdown(f"<small>{t('longitude')}</small><br><b>{st.session_state.lon:.4f}</b>", unsafe_allow_html=True)

    search = st.text_input(t("find_place"), placeholder=t("find_placeholder"))
    if search:
        places = find_places(search)
        if places:
            st.selectbox(t("choose_place"), places, key="place_pick",
                         format_func=lambda p: p["name"][:70])
            st.button(t("go_place"), on_click=go_to_place, type="primary", use_container_width=True)
        else:
            st.warning(t("no_place"))

    st.button(t("use_location"), on_click=use_my_location, use_container_width=True)
    st.button(t("demo_field"), on_click=use_demo_field, icon=":material/satellite_alt:",
              use_container_width=True, help=t("demo_help"))

    with st.form("field_form"):
        field_name = st.text_input(t("field_name"), key="field_name")
        with st.expander(t("periods")):
            num_days = st.slider(t("history_days"), 60, 730, config.NUM_DAYS, step=30)
            recent_days = st.slider(t("summary_days"), 7, 90, 30)
        st.form_submit_button(t("load_data"), type="primary", use_container_width=True)
    latitude, longitude = float(st.session_state.lat), float(st.session_state.lon)
    with st.expander(t("alert_thresholds")):
        thresholds = {
            "dry_soil": st.slider(t("thr_dry"), 0.1, 0.7,
                                  float(config.DRY_SOIL_THRESHOLD), 0.05, help=glossary.explain("GWETROOT")),
            "low_rain": st.slider(t("thr_rain"), 10, 100,
                                  int(config.LOW_RAIN_RATIO * 100), 5) / 100,
            "heat": st.slider(t("thr_heat"), 30, 45,
                              int(config.HEAT_THRESHOLD), 1, help=glossary.explain("T2M_MAX")),
        }
    st.divider()
    st.divider()
    st.markdown("**❓ What does this word mean?**")
    _terms = sorted(glossary.GLOSSARY, key=lambda k: glossary.name(k).lower())
    _pick = st.selectbox("Choose a word", _terms, index=None, placeholder="e.g. NDVI, T2M_MAX, RH2M ...",
                         format_func=lambda k: k if k == glossary.name(k) else f"{k} – {glossary.name(k)}",
                         label_visibility="collapsed")
    if _pick:
        st.info(glossary.explain(_pick))


# ---------------------------------------------------------
# Data
# ---------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner="Fetching data from NASA POWER ...")
def load_power(lat, lon, name, days):
    # v2: saved copies are kept per place (the function text is part of the cache key)
    return get_field_data(lat, lon, name, days)


try:
    df = load_power(latitude, longitude, field_name.strip() or "field", num_days)
except NasaConnectionError as error:
    st.error(f"❌ {error}")
    st.stop()
except Exception as error:
    st.error(f"❌ Something went wrong: {error}")
    st.stop()

if df.empty:
    st.warning("No data returned for this location.")
    st.stop()

sat, sat_field = load_satellite_for(field_name.strip(), latitude, longitude)
from src import downloader as _dl
if not sat:
    # New place: fetch its NASA satellite data automatically, in the background
    if _dl.status(latitude, longitude)[0] is None:
        _dl.start(latitude, longitude)
elif _dl.has_credentials() and not all(k in sat for k in ("smap", "ecostress", "gpm")) \
        and _dl.status(latitude, longitude)[0] != "running" \
        and _dl.status(latitude, longitude, "nasa")[0] is None:
    # Earthdata account saved: add SMAP, ECOSTRESS and GPM for this place, once
    _dl.start(latitude, longitude, parts=["gpm", "appeears"], tag="nasa")

with st.sidebar:
    with st.expander(t("ed_title"), icon=":material/key:"):
        if _dl.has_credentials():
            st.markdown(t("ed_connected_all"))
            _state, _lines = _dl.status(latitude, longitude, "nasa")
            if _state == "running":
                st.caption(f":material/downloading: {t('ed_running')}  \n{_lines[-1] if _lines else ''}")
            elif _state in ("done", "failed") and _lines:
                st.caption(_lines[-1])
        else:
            st.markdown(t("ed_why"))
            with st.form("ed_form", border=False):
                _u = st.text_input(t("dl_user"))
                _p = st.text_input(t("dl_pass"), type="password")
                if st.form_submit_button(t("ed_save"), type="primary"):
                    if _u and _p:
                        _dl.save_credentials(_u.strip(), _p)
                        st.rerun()
                    else:
                        st.error(t("dl_need"))

def _srtm_elevation():
    if "srtm" in sat and "elevation_m" in sat["srtm"]:
        return float(sat["srtm"]["elevation_m"].dropna().iloc[-1])
    return None


_lang_col = st.columns([5, 1.6])[1]
_lang_col.segmented_control(t("language"), list(i18n.LANGS), key="lang", format_func=i18n.LANGS.get,
                            label_visibility="collapsed")
style.hero(field_name, latitude, longitude, df.index.min(), df.index.max(), sat, _srtm_elevation())
verdict_slot = st.container()          # filled at the end, once every module has run


def last_value(source, column):
    if source in sat and column in sat[source]:
        s = sat[source][column].dropna()
        if not s.empty:
            return s.iloc[-1], s.index[-1]
    return None, None


TAB_LABELS = [
    f":material/dashboard: {t('tab_overview')}", f":material/map: {t('tab_map')}",
    f":material/history: {t('tab_history')}", f":material/view_in_ar: {t('tab_3d')}",
    f":material/agriculture: {t('tab_crops')}", f":material/psychology: {t('tab_drought')}",
    f":material/forum: {t('tab_assistant')}", f":material/menu_book: {t('tab_glossary')}",
]


def _remember_tab(labels):
    # Keep the open tab by position, so it survives reruns and language changes
    if st.session_state.get("main_tabs") in labels:
        st.session_state.tab_index = labels.index(st.session_state.main_tabs)


if st.session_state.get("main_tabs") not in TAB_LABELS:
    st.session_state.main_tabs = TAB_LABELS[st.session_state.get("tab_index", 0)]
tabs = st.tabs(TAB_LABELS, key="main_tabs", on_change=_remember_tab, args=(TAB_LABELS,))
# ---------------------------------------------------------
# Overview
# ---------------------------------------------------------
with tabs[0]:
    ind = compute_indicators(df, days=recent_days)
    alerts = compute_alerts(ind, thresholds)

    v_smap, d_smap = last_value("smap", "sm_rootzone")
    v_ndvi, d_ndvi = last_value("modis", "ndvi")
    ndvi_src = "MODIS"
    if v_ndvi is None:
        v_ndvi, d_ndvi = last_value("landsat", "ndvi_landsat")
        ndvi_src = "Landsat"
    v_lst, d_lst = last_value("ecostress", "lst_c")
    lst_src = "ECOSTRESS"
    if v_lst is None:
        v_lst, d_lst = last_value("landsat", "lst_landsat_c")
        lst_src = "Landsat"

    WATER, HEAT, GREEN = "#2E6F9E", "#C8912E", "#3E8A4F"
    rain_diff = ind["rain_recent"] - ind["rain_normal"]
    root_diff = ind["root_moisture"] - thresholds["dry_soil"]
    water_cards = [
        dict(icon="rain", label=t("rain_last", d=recent_days), value=f"{ind['rain_recent']:.0f}", unit="mm",
             note=t("vs_usual", x=f"{rain_diff:+.0f}", u=f"{ind['rain_normal']:.0f}"), tone="bad" if rain_diff < 0 else "good",
             source="NASA POWER", help=glossary.explain("PRECTOTCORR")),
        dict(icon="drop", label=t("root_wet"), value=f"{ind['root_moisture']:.2f}", unit="",
             note=t("above_dry" if root_diff >= 0 else "below_dry", x=f"{root_diff:+.2f}", l=f"{thresholds['dry_soil']:.2f}"),
             tone="good" if root_diff >= 0 else "bad", source="NASA POWER", help=glossary.explain("GWETROOT")),
    ]
    if v_smap is not None:
        water_cards.append(dict(icon="sat", label=t("smap_root"), value=f"{v_smap:.2f}", unit="m³/m³",
                                note=f"{d_smap:%d %b %Y}", tone="info", source="SMAP 9 km",
                                help=glossary.explain("Soil moisture (SMAP)")))
    hot = ind["max_temp"] >= thresholds["heat"]
    heat_cards = [
        dict(icon="thermo", label=t("max_air"), value=f"{ind['max_temp']:.1f}", unit="°C",
             note=t("above_heat" if hot else "below_heat", l=f"{thresholds['heat']:.0f}"), tone="bad" if hot else "good",
             source="NASA POWER", help=glossary.explain("T2M_MAX")),
        dict(icon="thermo", label=t("mean_air"), value=f"{ind['mean_temp']:.1f}", unit="°C",
             note=t("last_days", d=recent_days), tone="info", source="NASA POWER", help=glossary.explain("T2M")),
    ]
    if v_lst is not None:
        heat_cards.append(dict(icon="sun", label=t("surface_temp"), value=f"{v_lst:.1f}", unit="°C",
                               note=f"{lst_src} · {d_lst:%d %b %Y}", tone="info",
                               source=f"{lst_src} {'70 m' if lst_src == 'ECOSTRESS' else '30 m'}",
                               help=glossary.explain("LST")))
    g1, g2 = st.columns(2, gap="medium")
    with g1:
        cards.metric_group(t("water"), WATER, "drop", water_cards)
    with g2:
        cards.metric_group(t("heat"), HEAT, "thermo", heat_cards)

    g3, g4 = st.columns([1, 2], gap="medium")
    with g3:
        if v_ndvi is not None:
            level = t("ndvi_bare") if v_ndvi < 0.2 else t("ndvi_mod") if v_ndvi < 0.5 else t("ndvi_dense")
            cards.metric_group(t("vegetation"), GREEN, "leaf", [dict(
                icon="leaf", label=t("ndvi_name"), value=f"{v_ndvi:.2f}", unit="",
                note=f"{level} · {ndvi_src} {d_ndvi:%d %b %Y}", tone="info",
                source=f"{ndvi_src} {'250 m' if ndvi_src == 'MODIS' else '30 m'}", help=glossary.explain("NDVI"))])
        else:
            st.warning(t("no_veg"))
    with g4:
        st.markdown(f'<div class="fs-mg-head" style="color:#B3261E">{t("alerts")}</div>', unsafe_allow_html=True)
        if alerts:
            for alert in alerts:
                st.warning(tr(alert))
        else:
            st.success(t("no_alerts"))

    left, right = st.columns(2)
    with left:
        st.plotly_chart(temperature_chart(df))
        st.plotly_chart(soil_moisture_chart(df))
    with right:
        st.plotly_chart(rain_chart(df))
        st.plotly_chart(humidity_chart(df))


# ---------------------------------------------------------
# Map (function 2 of the document)
# ---------------------------------------------------------
with tabs[1]:
    from datetime import date as _date, timedelta as _td
    from streamlit_folium import st_folium
    from src.gibs import load_capabilities, parse_layers, find_layers
    from src.map_view import build_map, polygon_info

    @st.cache_data(ttl=24 * 3600, show_spinner="Loading NASA GIBS layer list ...")
    def gibs_layers():
        return find_layers(parse_layers(load_capabilities()))

    try:
        layers = gibs_layers()
    except Exception as error:
        layers = []
        st.warning(f"NASA GIBS layers unavailable ({error}). The base map still works.")

    col_a, col_b = st.columns([1, 2])
    day = col_a.date_input("Satellite image date", value=_date.today() - _td(days=2),
                           max_value=_date.today())

    compare = None
    data_layers = [l for l in layers if l["key"] != "relief"]
    if data_layers and st.toggle("🔀 Compare two dates on the map (sliding bar)"):
        k1, k2, k3 = st.columns([2, 1, 1])
        chosen_layer = k1.selectbox("Layer", data_layers, format_func=lambda l: l["label"])
        day_a = k2.date_input("Left date", value=_date.today() - _td(days=200), max_value=_date.today())
        day_b = k3.date_input("Right date", value=_date.today() - _td(days=2), max_value=_date.today())
        compare = {"layer": chosen_layer, "day_a": day_a, "day_b": day_b}

    # Field marker: values of the field, coloured by the alert thresholds
    field_popup = (f"<b>{field_name}</b><br>Rain, last {ind['days']} days: <b>{ind['rain_recent']:.0f} mm</b> "
                   f"(usual {ind['rain_normal']:.0f})<br>Root-zone wetness: <b>{ind['root_moisture']:.2f}</b> "
                   f"(alert below {thresholds['dry_soil']:.2f})<br>Max temperature: <b>{ind['max_temp']:.1f} °C</b> "
                   f"(alert above {thresholds['heat']:.0f})<br>"
                   + ("<span style='color:#A87418'><b>⚠ " + "<br>⚠ ".join(alerts) + "</b></span>" if alerts
                      else "<span style='color:#2F6B4F'><b>✓ No alert</b></span>")
                   + "<br><small>NASA POWER, regional (~50 km)</small>")
    fmap = build_map(latitude, longitude, layers, day, compare=compare, field_popup=field_popup,
                     field_color="orange" if alerts else "green")
    try:
        result = st_folium(fmap, height=560, use_container_width=True,
                           returned_objects=["last_clicked", "last_active_drawing"])
    except TypeError:                    # older streamlit-folium versions
        result = st_folium(fmap, height=560, width=1100,
                           returned_objects=["last_clicked", "last_active_drawing"])

    @st.cache_data(ttl=6 * 3600, show_spinner="Reading NASA POWER for this point ...")
    def point_card(lat, lon):
        """Last 365 days of NASA POWER for a clicked point (not saved to disk)."""
        from src.nasa_power import fetch_nasa_data, json_to_dataframe
        end = _date.today() - _td(days=config.NASA_DELAY_DAYS)
        point_df = json_to_dataframe(fetch_nasa_data(lat, lon, end - _td(days=365), end))
        return compute_indicators(point_df, days=30)

    clicked = (result or {}).get("last_clicked")
    if clicked:
        st.markdown(f"##### 📌 Clicked point: {clicked['lat']:.4f}, {clicked['lng']:.4f}")
        try:
            pc = point_card(round(clicked["lat"], 3), round(clicked["lng"], 3))
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Rain, last 30 days", f"{pc['rain_recent']:.0f} mm",
                      f"{pc['rain_recent'] - pc['rain_normal']:+.0f} mm vs usual", help=glossary.explain("PRECTOTCORR"))
            p2.metric("Root-zone wetness", f"{pc['root_moisture']:.2f}", help=glossary.explain("GWETROOT"))
            p3.metric("Max temperature", f"{pc['max_temp']:.1f} °C", help=glossary.explain("T2M_MAX"))
            point_alerts = compute_alerts(pc, thresholds)
            p4.markdown("**Alerts**<br>" + ("<br>".join("⚠️ " + a.split(":")[0] for a in point_alerts)
                                           if point_alerts else "✅ none"), unsafe_allow_html=True)
        except Exception as error:
            st.warning(f"Values not available for this point ({error}).")
        st.button("📍 Use this point as my field", on_click=use_point, args=(clicked["lat"], clicked["lng"]))

    drawing = (result or {}).get("last_active_drawing")
    if drawing and drawing.get("geometry", {}).get("type") == "Polygon":
        info = polygon_info(drawing)
        d1, d2, d3 = st.columns(3)
        d1.metric("📐 Field area", f"{info['area_ha']:.2f} ha")
        d2.write(f"Centre: **{info['lat']:.4f}, {info['lon']:.4f}**")
        d3.button("📍 Use field centre", on_click=use_point, args=(info["lat"], info["lon"]),
                  key="use_centre")
        ring = drawing["geometry"]["coordinates"][0]
        if st.button("🌾 Use this drawing as my field (3D virtual farm)"):
            st.session_state.field_polygon = [list(p) for p in ring[:-1]] if ring[0] == ring[-1] else ring
            st.success("Field shape saved. Open the 🧊 Virtual farm 3D tab.")

    if layers:
        with st.expander("🎨 Legend: colours, units and dates of the NASA layers", expanded=False):
            for layer in layers:
                when = layer["default_time"] or "static"
                shown = min(str(day), when[:10]) if layer["default_time"] else "static"
                st.markdown(f"**{layer['label']}**  \n{layer.get('title', layer['id'])} · image date: "
                            f"**{shown}** (latest available: {when[:10]})")
                if layer.get("legend"):
                    st.markdown(f'<img src="{layer["legend"]}" style="max-width:420px;width:100%;'
                                f'background:#fff;border-radius:6px;padding:4px">', unsafe_allow_html=True)


# ---------------------------------------------------------
# History (functions 3 and 4: compare with past years, detect anomalies)
# ---------------------------------------------------------
with tabs[2]:
    from src import history
    from src.web_charts import (monthly_vs_normal_chart, zscore_heatmap,
                                yearly_rain_chart, drought_days_chart)

    years = st.slider("Reference period (years)", 5, 30, 10,
                      help="The 'normal' is the average of these past years (NASA POWER since 1981).")

    @st.cache_data(ttl=24 * 3600, show_spinner="Downloading the long NASA POWER history ...")
    def load_history(lat, lon, name, years):
        # v2: saved copies are kept per place
        return history.get_long_history(lat, lon, name, years)

    try:
        hist = load_history(latitude, longitude, field_name.strip() or "field", years)
    except Exception as error:
        hist = None
        st.error(t("no_history", e=error))

    if hist is not None and len(hist) > 400:

        monthly = history.monthly_table(hist)
        comparison = history.compare_recent(monthly, recent_months=12)

        rain_ranking, rain_12m, rank = history.yearly_rain_ranking(hist)
        k1, k2, k3 = st.columns(3)
        k1.metric("🌧️ Rain, last 12 months", f"{rain_12m:.0f} mm",
                  f"{rain_12m - rain_ranking['rain_mm'].mean():+.0f} mm vs average")
        k2.metric("📊 Rank (1 = driest)", f"{rank} / {len(rain_ranking)}")
        k3.metric("📅 Reference", f"{monthly.index.min():%Y} – {monthly.index.max():%Y}")

        st.plotly_chart(zscore_heatmap(comparison, history.LABELS))

        st.markdown("##### ⚠️ Unusual months")
        unusual = history.anomalies(comparison)
        if unusual.empty:
            st.success("No unusual month in the last 12 months.")
        else:
            st.dataframe(unusual, hide_index=True)

        left, right = st.columns(2)
        with left:
            st.plotly_chart(monthly_vs_normal_chart(comparison, "PRECTOTCORR",
                                                    "🌧️ Monthly rainfall vs normal", "mm", "#378ADD"))
            st.plotly_chart(yearly_rain_chart(rain_ranking))
        with right:
            st.plotly_chart(monthly_vs_normal_chart(comparison, "T2M_MAX",
                                                    "🌡️ Max temperature vs normal", "°C", "#D85A30"))
            st.plotly_chart(drought_days_chart(history.drought_days(hist)))



# ---------------------------------------------------------
# Drought risk with machine learning (function 5 of the document)
# ---------------------------------------------------------
with tabs[5]:      # drought risk (shown 6th; computed here because Crops uses its result)
    from src import ml, history as _history
    from src.web_charts import importance_chart, risk_timeline_chart

    st.markdown(f"**Question:** will the next **{ml.HORIZON} days** be *unusually dry for this "
                f"season* at this place? (= among the {ml.DRY_PERCENTILE} % driest periods of the "
                "same month in past years, using NASA POWER root-zone wetness)")
    ml_years = st.slider("Years of history used to train the model", 10, 40, 20,
                         help="More years = more examples of dry periods to learn from.")

    @st.cache_resource(show_spinner="Training the model on NASA POWER history ...")
    def train(lat, lon, name, years):
        # v2: saved copies are kept per place
        hist_df = _history.get_long_history(lat, lon, name, years)
        return ml.train_and_evaluate(hist_df)

    try:
        info = train(latitude, longitude, field_name.strip() or "field", ml_years)
    except Exception as error:
        info = None
        st.error(f"❌ Could not train the model: {error}")

    if info is not None:
        today = ml.predict_today(info)
        r1, r2 = st.columns([1, 2])
        r1.metric(f"Risk for the next {ml.HORIZON} days", today["level"],
                  f"{today['probability']:.0%} probability", delta_color="off")
        with r2:
            st.progress(today["probability"])
            inputs = today["inputs"]

        st.markdown("##### 📏 How good is it? (tested on the last year, never seen during training)")
        rows = [{"Model": name, "Accuracy": r["accuracy"], "Precision": r["precision"],
                 "Recall": r["recall"], "F1": r["f1"]} for name, r in info["results"].items()]
        st.dataframe(pd.DataFrame(rows).round(2), hide_index=True, column_config={
            m: st.column_config.NumberColumn(m, help=glossary.explain(m)) for m in ("Accuracy", "Precision", "Recall", "F1")})
        o = info["onset"]
        st.info(f"**Honest result:** soil moisture changes slowly, so the simple rule "
                f"*\"dry today → dry in {ml.HORIZON} days\"* is already very good. The model's added value "
                f"is the **start** of dry periods (not dry today, dry later): in the test year there were "
                f"**{o['onsets']}** such days; the Random Forest caught **{o['caught']}** "
                f"with **{o['false_alarms']}** false alarms. The simple rule catches 0 by design.")

        cm = info["results"]["Random Forest"]["confusion"]
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("**Confusion matrix (Random Forest)**")
            st.dataframe(pd.DataFrame(cm, index=["Actual: not dry", "Actual: dry"],
                                      columns=["Predicted: not dry", "Predicted: dry"]))
        with c2:
            st.plotly_chart(risk_timeline_chart(info["test"]))
        st.plotly_chart(importance_chart(info["importance"], ml.FEATURE_LABELS))


# ---------------------------------------------------------
# Crops & scenarios (functions 6, 8 and 11 of the document)
# ---------------------------------------------------------
with tabs[4]:
    from src import crops as _crops, scenarios as _scen, history as _hist2
    from src.web_charts import crop_needs_chart, scenario_chart

    @st.cache_data(ttl=24 * 3600, show_spinner="Loading 20 years of NASA POWER data ...")
    def crop_history(lat, lon, name):
        # v2: saved copies are kept per place
        return _hist2.get_long_history(lat, lon, name, 20)

    try:
        crop_df = crop_history(latitude, longitude, field_name.strip() or "field")
    except Exception as error:
        crop_df = None
        st.error(t("no_history", e=error))

    if crop_df is not None:
        from src import recommend as _rec
        summary = _crops.crop_summary(crop_df, latitude)
        next_season, past_seasons = _rec.season_labels()

        # ---------- 1) Build your rotation: last 3 seasons -> crop for this season ----------
        from src.crop_icons import icon as crop_icon
        st.markdown(cards.BUILDER_CSS, unsafe_allow_html=True)
        st.markdown(f'<div class="fs-section"><h3>{t("build_title")}</h3><p>{t("build_sub", s=next_season)}</p></div>',
                    unsafe_allow_html=True)
        crop_list = list(_crops.CROPS)
        crop_options = ["—"] + crop_list
        row = st.columns([1, 0.13, 1, 0.13, 1, 0.18, 1.35], vertical_alignment="center")
        past = []
        for i, (col, season) in enumerate(zip((row[0], row[2], row[4]), past_seasons)):
            with col, st.container(key=f"fs_past{i}"):
                st.markdown(cards.season_label(t("you_grew", s=season)), unsafe_allow_html=True)
                choice = st.selectbox(season, crop_options, index=crop_options.index("Wheat"), key=f"cur{i + 1}",
                                      format_func=lambda c: c if c == "—" else i18n.crop(c),
                                      label_visibility="collapsed")
                if choice != "—":
                    st.markdown(cards.crop_badge(choice), unsafe_allow_html=True)
                past.append(choice)
        for col in (row[1], row[3]):
            col.markdown('<div class="fs-b-arrow">→</div>', unsafe_allow_html=True)
        row[5].markdown('<div class="fs-b-arrow" style="color:#2F6B4F;font-size:1.8rem">➜</div>',
                        unsafe_allow_html=True)
        current_rotation = [c for c in past if c != "—"]
        previous = current_rotation[-1] if current_rotation else "Unknown"

        water = st.slider(t("water_avail"), 0, 800, 0, step=25, help=t("water_help"))
        risk_now = globals().get("today") if isinstance(globals().get("today"), dict) else None
        reco = _rec.recommend([None] * (3 - len(current_rotation)) + current_rotation, summary, water,
                              risk_now["probability"] if risk_now else None)
        best = reco.iloc[0]["crop"]
        if st.session_state.get("now_suggest") != best:
            st.session_state.now_suggest = best
            st.session_state.now_crop = best

        with row[6], st.container(key="fs_now"):
            st.markdown(cards.season_label(t("this_season", s=next_season)), unsafe_allow_html=True)
            chosen = st.selectbox(next_season, crop_list, key="now_crop", format_func=i18n.crop,
                                  label_visibility="collapsed")
            pick = reco[reco["crop"] == chosen].iloc[0]
            badge = (cards.pill(t("suggested", p=int(round(100 * pick["score"]))), solid=True) if chosen == best
                     else cards.pill(t("changed")))
            st.markdown(cards.crop_badge(chosen, badge), unsafe_allow_html=True)

        others = [(r["crop"], int(round(100 * r["score"]))) for _, r in reco.head(4).iterrows()
                  if r["crop"] != chosen][:2]
        c_left, c_right = st.columns([4, 1.2], vertical_alignment="center")
        c_left.markdown(cards.chips(t("other_choices"), others), unsafe_allow_html=True)
        if chosen != best:
            c_right.button(t("back_suggestion"), use_container_width=True,
                           on_click=lambda b=best: st.session_state.update(now_crop=b))

        info_row = summary[summary["Crop"] == chosen].iloc[0]
        tiles = [(t("sow_around"), f"{pick['sow']:%d %b}", f"{pick['sow']:%Y}", "")]
        if chosen == "Fallow":
            tiles += [(t("irr_normal"), "0 mm", "", ""), (t("irr_dry"), "0 mm", "", "")]
        else:
            tiles += [(t("irr_normal"), f"{info_row['Irrigation – normal year (mm)']:.0f} mm",
                       t("rain_covers", p=f"{info_row['Rain covers (%)']:.0f}"), "good"),
                      (t("irr_dry"), f"{info_row['Irrigation – dry year (mm)']:.0f} mm", t("one_in_five"), "")]
        if previous in set(summary["Crop"]) and previous != chosen:
            prev_row = summary[summary["Crop"] == previous].iloc[0]
            diff = prev_row["Irrigation – normal year (mm)"] - info_row["Irrigation – normal year (mm)"]
            tiles.append((t("if_again", c=i18n.crop(previous)), f"{prev_row['Irrigation – normal year (mm)']:.0f} mm",
                          t("more_mm" if diff >= 0 else "less_mm", x=f"{abs(diff):.0f}"), "bad" if diff > 0 else "good"))
        st.markdown(cards.tiles(tiles), unsafe_allow_html=True)

        if chosen == best:
            st.markdown(cards.verdict_box(t("verdict_best", c=i18n.crop(chosen)), "ok"), unsafe_allow_html=True)
        else:
            st.markdown(cards.verdict_box(t("verdict_other", b=i18n.crop(best),
                                            pb=int(round(100 * reco.iloc[0]["score"])),
                                            pc=int(round(100 * pick["score"])), c=i18n.crop(chosen)), "info"),
                        unsafe_allow_html=True)
        st.markdown(cards.pros_cons([tr(x) for x in pick["reasons"]], [tr(x) for x in pick["warnings"]]
                                    + [tr(x) for x in reco.attrs.get("context", [])]), unsafe_allow_html=True)
        with st.expander(t("all_ranked")):
            st.dataframe(pd.DataFrame({
                t("col_crop"): reco["icon"] + " " + reco["crop"].map(i18n.crop),
                t("col_match"): (100 * reco["score"]).round(0),
                t("col_rot"): (100 * reco["rotation"]).round(0),
                t("col_water"): (100 * reco["water"]).round(0),
                t("col_sow"): reco["sow"].map(lambda d: d.strftime("%d %b %Y")),
            }), hide_index=True)

        # ---------- 2) Water needs ----------
        st.markdown(f'<div class="fs-section"><h3>{t("water_needs")}</h3></div>', unsafe_allow_html=True)
        cards.water_share(summary)
        with st.expander(t("water_table")):
            st.dataframe(summary.round(0), hide_index=True)

        # ---------- Strategies ranked quietly (used by the report and the assistant) ----------
        weights = {"water": 2, "risk": 2, "rotation": 1}
        scenarios = {name: crops_ for name, crops_ in _scen.DEFAULT_SCENARIOS.items() if crops_ != current_rotation}
        scenarios[f"Suggested: {best}"] = [best] + current_rotation[-2:] if current_rotation else [best]
        baseline_name = None
        if current_rotation:
            baseline_name = "⭐ Your current rotation: " + " → ".join(current_rotation)
            scenarios = {baseline_name: current_rotation, **scenarios}
        ranking = _scen.rank_scenarios(crop_df, latitude, scenarios, water, weights, previous)
        if not ranking.empty and baseline_name:
            ranking = _scen.compare_to_baseline(ranking, baseline_name)
        best_scenario_text = None
        if not ranking.empty:
            best_scenario_text = (f"{ranking.iloc[0]['Scenario']} (score {ranking.iloc[0]['score']:.2f}, "
                                  f"about {ranking.iloc[0]['need_mm']:.0f} mm/yr of irrigation)")


# ---------------------------------------------------------
# Virtual farm 3D (function 7 of the document)
# ---------------------------------------------------------
with tabs[3]:      # 3D farm (shown 4th)
    from datetime import date as _d, timedelta as _td3
    from src.field import square_polygon, size_km
    from src import twin

    polygon = st.session_state.get("field_polygon") or square_polygon(latitude, longitude, 400)
    width_km, height_km = size_km(polygon)

    if width_km > 3 or height_km > 3:
        st.warning("The field is larger than 3 km. Draw a smaller field for the 3D view.")
    else:
        view = st.radio("View", ["⛰️ Terrain (SRTM relief + satellite image)",
                                 "🧱 Zones (Landsat 30 m indicators)"], horizontal=True)

        if view.startswith("⛰️"):
            exaggeration = st.slider("Relief exaggeration", 1.0, 5.0, 2.0, 0.5)
            elev, _ = last_value("srtm", "elevation_m")
            if elev is None:
                @st.cache_data(ttl=30 * 24 * 3600, show_spinner=False)
                def _ground_height(lat, lon):
                    from src.terrain import elevation_tile
                    grid, _px, (r, c) = elevation_tile(lat, lon)
                    return float(grid[r, c])
                try:
                    elev = _ground_height(round(latitude, 4), round(longitude, 4))
                except Exception:
                    elev = 0
            @st.cache_resource(show_spinner="Building the 3D relief ...", max_entries=8)
            def _relief(poly_key, base, ex):
                return twin.terrain_deck([list(p) for p in poly_key], base, ex)

            _deck3d = _relief(tuple(tuple(p) for p in polygon), float(elev or 0), float(exaggeration))
            st.pydeck_chart(_deck3d, height=540)
        else:
            today3 = _d.today()
            p1, p2 = st.columns(2)
            period_a = p1.date_input("Period A (e.g. spring)", value=(_d(today3.year, 3, 1), _d(today3.year, 4, 30)),
                                     max_value=today3)
            period_b = p2.date_input("Period B (e.g. recent)", value=(today3 - _td3(days=60), today3),
                                     max_value=today3)

            @st.cache_data(ttl=24 * 3600, show_spinner="Reading Landsat pixels over the field ...")
            def field_grid(poly_key, start, end):
                from src.sources.landsat import best_scene_grid
                return best_scene_grid([list(p) for p in poly_key], start, end)

            if st.button("🛰️ Load Landsat images for the field"):
                st.session_state.twin_request = (tuple(tuple(p) for p in polygon),
                                                 tuple(period_a), tuple(period_b))

            request = st.session_state.get("twin_request")
            if request and request[0] == tuple(tuple(p) for p in polygon) \
                    and len(request[1]) == 2 and len(request[2]) == 2:
                try:
                    date_a, grid_a = field_grid(request[0], *request[1])
                    date_b, grid_b = field_grid(request[0], *request[2])
                except Exception as error:
                    date_a = date_b = None
                    grid_a = grid_b = pd.DataFrame()
                    st.error(f"❌ Landsat reading failed: {error}")

                if grid_b.empty and grid_a.empty:
                    st.warning("No clear Landsat image found for these periods. Try longer periods.")
                else:
                    available = ["NDVI (vegetation)", "Surface temperature"]
                    if not grid_a.empty and not grid_b.empty:
                        available.append("Change in NDVI (B − A)")
                    o1, o2, o3 = st.columns([2, 1, 1])
                    indicator = o1.selectbox("Indicator", available)
                    mode = o2.radio("Show", ["pixels", "zones"], horizontal=True,
                                    help="pixels = each 30 m Landsat pixel shown as a hexagon; zones = field split into 3 × 3")
                    scale = o3.slider("Height ×", 0.5, 4.0, 1.0, 0.5)
                    which = o1.radio("Date", ["B", "A"], horizontal=True,
                                     disabled=indicator.startswith("Change"))

                    if indicator.startswith("Change"):
                        pixels = twin.compare_periods(grid_a, grid_b)
                    else:
                        pixels, when = (grid_b, date_b) if (which == "B" and not grid_b.empty) else (grid_a, date_a)

                    st.markdown(cards.ndvi_story(
                        grid_a["ndvi"].mean() if not grid_a.empty else None, date_a,
                        grid_b["ndvi"].mean() if not grid_b.empty else None, date_b,
                        grid_b["lst_c"].mean() if not grid_b.empty else None, len(pixels)),
                        unsafe_allow_html=True)

                    _deck3d = twin.zones_deck(pixels, polygon, indicator, mode, scale)
                    st.pydeck_chart(_deck3d, height=540)
                    column = twin.INDICATORS[indicator][0]
                    zones = twin.zone_table(pixels, polygon, column)
                    if not zones.empty:
                        st.markdown("**Virtual zones** (A = north row, 1 = west column)")
                        st.dataframe(zones[["zone", "pixels", "value"]].rename(
                            columns={"value": twin.INDICATORS[indicator][1]}).round(2), hide_index=True)
            else:
                st.info("Choose two periods and click **🛰️ Load Landsat images for the field**.")


# ---------------------------------------------------------
# AI Agronomist (function 10 of the document)
# ---------------------------------------------------------
with tabs[6]:
    from src import assistant

    # 1) Collect the facts computed by the other tabs
    g = globals()
    facts = []
    A = assistant.add
    A(facts, "Field", "Location", f"{field_name} ({latitude:.4f}, {longitude:.4f})")
    if "ind" in g:
        A(facts, "NASA POWER", f"Rain, last {ind['days']} days",
          f"{ind['rain_recent']:.0f} mm (normal {ind['rain_normal']:.0f} mm)")
        A(facts, "NASA POWER", "Root-zone wetness (0-1), recent mean", f"{ind['root_moisture']:.2f}")
        A(facts, "NASA POWER", f"Max temperature, last {ind['days']} days", f"{ind['max_temp']:.1f} °C")
        A(facts, "NASA POWER", "Mean temperature, recent", f"{ind['mean_temp']:.1f} °C")
    if "alerts" in g:
        A(facts, "TerraShift rules", "Current alerts", "; ".join(alerts) if alerts else "none")
    if "rain_12m" in g and "rank" in g:
        A(facts, "NASA POWER history", "Rain, last 12 months",
          f"{rain_12m:.0f} mm (rank {rank}, 1 = driest year of the reference period)")
    if "unusual" in g and not unusual.empty:
        top = unusual.head(3)
        A(facts, "NASA POWER history", "Most unusual recent months",
          "; ".join(f"{r.Month} {r.Variable} z={r['z-score']}" for _, r in top.iterrows()))
    if "today" in g and isinstance(today, dict) and "probability" in today:
        A(facts, "TerraShift ML model (Random Forest)", f"Risk of unusually dry next {ml.HORIZON} days",
          f"{today['level']} ({today['probability']:.0%})")
    for src_key, col, label, unit in (("smap", "sm_rootzone", "SMAP root-zone soil moisture", "m³/m³"),
                                      ("smap", "sm_surface", "SMAP surface soil moisture", "m³/m³"),
                                      ("modis", "ndvi", "MODIS NDVI latest", ""),
                                      ("landsat", "ndvi_landsat", "Landsat NDVI latest", ""),
                                      ("ecostress", "lst_c", "ECOSTRESS surface temperature latest", "°C"),
                                      ("srtm", "elevation_m", "SRTM elevation", "m")):
        v, d = last_value(src_key, col)
        if v is not None:
            A(facts, src_key.upper(), label, f"{v:.2f} {unit} ({d:%d %b %Y})".strip())
    if "summary" in g and hasattr(summary, "columns") and "Crop" in summary.columns:
        A(facts, "TerraShift crops (FAO-56)", "Irrigation need per crop, normal year (mm)",
          ", ".join(f"{r.Crop} {r['Irrigation – normal year (mm)']:.0f}" for _, r in summary.iterrows()))
    if "ranking" in g and hasattr(ranking, "columns") and "Scenario" in ranking.columns and len(ranking):
        A(facts, "TerraShift scenarios", "Best scenario for the chosen criteria",
          f"{ranking.iloc[0]['Scenario']} (score {ranking.iloc[0]['score']:.2f})")
    if "reco" in g and hasattr(reco, "columns") and len(reco):
        A(facts, "TerraShift crop suggestions (rotation + water)",
          f"Suggested crops for {next_season} after {' → '.join(current_rotation) or 'unknown'}",
          ", ".join(f"{r.crop} ({r.score:.0%})" for r in reco.head(3).itertuples()))
    missing_sources = assistant.missing_data(sat)
    A(facts, "TerraShift", "Missing data", ", ".join(missing_sources) if missing_sources else "none")


    # 2) Chat on the left, what the assistant knows on the right
    st.markdown(cards.CHAT_CSS, unsafe_allow_html=True)
    st.session_state.setdefault("chat", [])

    def _ask(question):
        # Runs as a widget callback, so the page keeps the Assistant tab open
        question = (question or "").strip()
        if question:
            st.session_state.chat += [
                {"role": "user", "content": question},
                {"role": "assistant", "content": assistant.answer_offline(facts, question, i18n.lang())}]

    chat_col, side_col = st.columns([1.7, 1], gap="medium")

    with side_col, st.container(key="fs_side"):
        _risk = g.get("today") if isinstance(g.get("today"), dict) else None
        _nd = g.get("v_ndvi")
        rows = []
        if "ind" in g:
            rows += [(t("rain_last", d=ind["days"]), f"{ind['rain_recent']:.0f} mm"),
                     (t("as_usual_rain"), f"{ind['rain_normal']:.0f} mm"),
                     (t("root_wet"), f"{ind['root_moisture']:.2f}")]
        if _risk and "probability" in _risk:
            rows.append((t("as_drought"), f"{_risk['probability']:.0%}"))
        if _nd is not None:
            rows.append(("NDVI", f"{_nd:.2f}"))
        if "best" in g:
            rows.append((t("as_suggested"), i18n.crop(best)))
        st.markdown(cards.key_facts(t("as_know"), rows), unsafe_allow_html=True)
        with st.expander(t("as_all", n=len(facts))):
            st.dataframe(pd.DataFrame(facts), hide_index=True)
        st.markdown(f'<div class="fs-ch-h" style="margin-top:.8rem">{t("as_try")}</div>', unsafe_allow_html=True)
        for qk in ("q_summary", "q_drought", "q_irrigation", "q_grow", "q_soil"):
            st.button(t(qk), key=f"sugg_{qk}", use_container_width=True,
                      on_click=_ask, args=(t(qk).split(" ", 1)[1],))

    with chat_col, st.container(key="fs_chat"):
        h_left, h_right = st.columns([5, 1], vertical_alignment="center")
        h_left.markdown(cards.chat_header(t("as_title"), t("as_ready"), t("as_from", n=len(facts))),
                        unsafe_allow_html=True)
        h_right.button(t("as_clear"), icon=":material/delete:", disabled=not st.session_state.chat,
                       key="chat_clear", on_click=lambda: st.session_state.update(chat=[]))
        if not st.session_state.chat:
            st.markdown(cards.chat_empty(t("as_empty")), unsafe_allow_html=True)
        for m in st.session_state.chat:
            with st.chat_message(m["role"], avatar=":material/eco:" if m["role"] == "assistant" else None):
                st.markdown(m["content"])
        st.chat_input(t("as_placeholder"), key="chat_q",
                      on_submit=lambda: _ask(st.session_state.get("chat_q")))


# ---------------------------------------------------------
# Raw data
# ---------------------------------------------------------
with st.expander("📋 Raw weather data (NASA POWER)"):
    nice_df, nice_cfg = glossary.friendly_columns(df)
    st.dataframe(nice_df, column_config=nice_cfg)
    st.download_button("⬇️ Download CSV", df.to_csv().encode("utf-8"),
                       file_name=f"{field_name}_nasa_power.csv", mime="text/csv")



# ---------------------------------------------------------
# Glossary: every technical word explained simply
# ---------------------------------------------------------
with tabs[7]:
    style.section("Glossary")
    query = st.text_input("Search a word", placeholder="e.g. NDVI, humidity, رطوبة, legume ...").strip().lower()
    for category, terms in glossary.categories().items():
        hits = [t for t in terms if not query or any(query in str(x).lower() for x in (t, *glossary.GLOSSARY[t]))]
        if not hits:
            continue
        st.markdown(f"#### {category}")
        for term in hits:
            n, _, en, ar, unit = glossary.GLOSSARY[term]
            title = n if term == n else f"{n}  ·  {term}"
            with st.expander(title + (f"  ({unit})" if unit else "")):
                st.write(en)
                st.markdown(f'<div dir="rtl" style="text-align:right;font-size:1.05rem">{ar}</div>',
                            unsafe_allow_html=True)

# ---------------------------------------------------------
# Verdict at the top of the page (needs the results of every tab)
# ---------------------------------------------------------
with verdict_slot:
    _g = globals()
    _risk = _g.get("today") if isinstance(_g.get("today"), dict) else None
    _rvn = _risk["inputs"]["root_vs_normal"] if _risk and "root_vs_normal" in _risk["inputs"] else None
    _ndvi = _g.get("v_ndvi")
    _rank = _g.get("rank")
    _nyears = len(_g["rain_ranking"]) if "rain_ranking" in _g else None
    _headline, _tone, _reasons = verdict.build_verdict(_g.get("ind"), _risk, _rvn, _ndvi, _rank, _nyears)
    style.verdict(tr(_headline), _tone, [(lvl, tr(txt)) for lvl, txt in _reasons])

    from src import report
    _ind = _g.get("ind")
    _facts = []
    if _ind:
        _facts += [
            {"name": f"Rain, last {_ind['days']} days", "value": f"{_ind['rain_recent']:.0f} mm "
             f"(usual {_ind['rain_normal']:.0f} mm)", "source": "NASA POWER"},
            {"name": "Root-zone soil wetness (0–1)", "value": f"{_ind['root_moisture']:.2f}", "source": "NASA POWER"},
            {"name": "Max temperature", "value": f"{_ind['max_temp']:.1f} °C", "source": "NASA POWER"},
        ]
    if _ndvi is not None:
        _facts.append({"name": "Vegetation index (NDVI)", "value": f"{_ndvi:.2f}", "source": "MODIS / Landsat"})
    if _risk:
        _facts.append({"name": "Chance of a dry spell (next 14 days)", "value": f"{_risk['probability']:.0%}",
                       "source": "TerraShift model on NASA POWER"})
    _numbers = []
    if _ind:
        _numbers += [(f"Rain, last {_ind['days']} days", f"{_ind['rain_recent']:.0f} mm"),
                     ("Usual rain", f"{_ind['rain_normal']:.0f} mm")]
    if _risk:
        _numbers.append(("Dry-spell risk (14 days)", f"{_risk['probability']:.0%}"))
    if _ndvi is not None:
        _numbers.append(("Vegetation (NDVI)", f"{_ndvi:.2f}"))
    try:
        _place = name_of(latitude, longitude)
    except Exception:
        _place = None
    _report = report.build_html(
        field_name, latitude, longitude, _headline, _reasons, _facts, _g.get("alerts") or [],
        crop_cards=_g.get("reco"), best_scenario=_g.get("best_scenario_text"), tone=_tone,
        place=_place, key_numbers=_numbers,
        limits=["NASA POWER is regional (~50 km); satellite pixels are 30 m to 9 km.",
                "Crop water needs use indicative FAO-56 values; soil type and yields are not included.",
                "Climate simulations are TerraShift scenarios, not NASA forecasts.",
                f"Alert thresholds used: dry soil < {thresholds['dry_soil']:.2f}, "
                f"rain < {thresholds['low_rain']:.0%} of usual, heat > {thresholds['heat']:.0f} °C."])
    with st.container(key="fs_report"):
        _rc1, _rc2 = st.columns([5, 1.3], vertical_alignment="center")
        _rc1.markdown(cards.report_card(t("report_title", name=field_name.strip() or "field"),
                                        t("report_sub")), unsafe_allow_html=True)
        _rc2.download_button(t("download"), _report.encode("utf-8"), icon=":material/download:",
                             file_name=f"TerraShift_report_{field_name.strip() or 'field'}.html",
                             mime="text/html", type="primary", use_container_width=True, key="dl_report")


# =========================================================
# References: where every piece of information comes from (bottom of every page)
# =========================================================
from src import references as _refs
with st.expander(_refs.title(i18n.lang()), icon=":material/menu_book:"):
    st.markdown(_refs.render(i18n.lang()), unsafe_allow_html=True)
