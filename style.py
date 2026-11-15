"""
style.py - TerraShift look & feel (fonts, header, metrics, tabs).
Colours:  olive #2F6B4F · saffron #C8912E · water #2E6F9E · sage #F3F5F0 · ink #1F2A24
Font:     Instrument Sans (titles, numbers and text)
"""

import html

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&display=swap');

html, body, .stApp, .stMarkdown, .stText, input, textarea, button, label, p, li, td, th {
  font-family: 'Instrument Sans', system-ui, sans-serif;
}
/* keep Streamlit's icon font (otherwise icon names like "arrow_right" show as text) */
[data-testid="stIconMaterial"], .material-symbols-rounded, span[class*="material-symbols"] {
  font-family: 'Material Symbols Rounded' !important;
}
h1, h2, h3, h4, h5, [data-testid="stMetricValue"], .fs-field {
  font-family: 'Instrument Sans', system-ui, sans-serif !important;
  letter-spacing: -0.01em;
}
.block-container { padding-top: 1.6rem; padding-left: 2rem; padding-right: 2rem; max-width: 100%; }

/* ---------- cover: the field seen from space ---------- */
.fs-cover {
  position: relative; border-radius: 14px; overflow: hidden; min-height: 300px;
  background-color: #1F3A2D; background-size: cover; background-position: center;
  display: flex; align-items: flex-end; margin-bottom: 1.1rem;
}
.fs-cover::after {
  content: ""; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(20,38,29,0.05) 20%, rgba(20,38,29,0.88) 100%);
}
.fs-cover-inner { position: relative; z-index: 1; padding: 1.5rem 1.8rem 1.3rem; width: 100%; }
.fs-brand { font-family: 'Instrument Sans', sans-serif; font-weight: 700;
            color: #CFE3C8; font-size: 0.95rem; }
.fs-field { font-size: clamp(2.6rem, 6vw, 4.6rem); font-weight: 800; line-height: 0.98;
            color: #FFFFFF; margin: 0.2rem 0 0.45rem 0; }
.fs-meta { color: #DCE7D8; font-size: 0.95rem; }
.fs-meta b { color: #FFFFFF; font-weight: 600; }
.fs-instruments { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.9rem; }
.fs-chip { display: inline-flex; align-items: center; gap: 0.4rem; border-radius: 999px;
           padding: 0.18rem 0.7rem; font-size: 0.8rem; color: #FFFFFF;
           background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.35); }
.fs-chip i { width: 0.55rem; height: 0.55rem; border-radius: 50%; display: inline-block; background: #9BD58A; }
.fs-chip.off { color: rgba(255,255,255,0.6); background: transparent; border-style: dashed; }
.fs-chip.off i { background: transparent; border: 1.5px solid rgba(255,255,255,0.6); }
.fs-crosshair { position: absolute; z-index: 1; left: 50%; top: 42%; width: 46px; height: 46px;
                margin: -23px 0 0 -23px; border: 2px solid #F2C14E; border-radius: 50%; }
.fs-crosshair::after { content: ""; position: absolute; left: 50%; top: 50%; width: 6px; height: 6px;
                       margin: -3px 0 0 -3px; background: #F2C14E; border-radius: 50%; }

/* ---------- verdict ---------- */
.fs-verdict { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
              gap: 1.6rem; align-items: start; margin: 0.4rem 0 1.4rem 0; }
.fs-verdict h2 { font-size: clamp(1.5rem, 2.6vw, 2.1rem) !important; line-height: 1.12; margin: 0;
                 font-weight: 700; color: #1F2A24; }
.fs-verdict .tone { width: 2.6rem; height: 0.35rem; border-radius: 3px; margin-bottom: 0.7rem; }
.fs-verdict .tone.warn { background: #C8912E; } .fs-verdict .tone.ok { background: #2F6B4F; }
.fs-verdict .tone.info { background: #2E6F9E; }
.fs-verdict .note { color: #5E6B63; font-size: 0.85rem; margin-top: 0.7rem; max-width: 34rem; }
.fs-reasons { list-style: none; margin: 0; padding: 0; }
.fs-reasons li { padding: 0.45rem 0 0.45rem 1.1rem; position: relative; color: #1F2A24;
                 border-bottom: 1px solid #DEE4DA; font-size: 0.97rem; }
.fs-reasons li::before { content: ""; position: absolute; left: 0; top: 0.95rem; width: 0.5rem;
                         height: 0.5rem; border-radius: 50%; }
.fs-reasons li.warn::before { background: #C8912E; } .fs-reasons li.ok::before { background: #2F6B4F; }
.fs-reasons li.info::before { background: #2E6F9E; }
.fs-group { font-family: 'Instrument Sans', sans-serif; font-weight: 700; color: #2F6B4F;
            font-size: 1.05rem; margin: 0.2rem 0 0.4rem; }
@media (max-width: 800px) { .fs-verdict { grid-template-columns: 1fr; } .fs-cover { min-height: 240px; } }

/* ---------- metrics: a rule, not a card ---------- */
[data-testid="stMetric"] {
  border-left: 3px solid #2F6B4F; padding: 0.15rem 0 0.15rem 0.85rem;
}
[data-testid="stMetricValue"] { font-weight: 700; color: #1F2A24; }
[data-testid="stMetricLabel"] p { color: #4F5E55; font-size: 0.85rem; }


/* ---------- metric cards (Overview: Water / Heat / Vegetation) ---------- */
.fs-mg-head { display: flex; align-items: center; gap: 0.5rem; font-weight: 700; font-size: 1.15rem; margin: 0.2rem 0 0.65rem; }
.fs-mg { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 0.75rem; }
.fs-mc { background: #FFFFFF; border: 1px solid #DDE3D8; border-radius: 14px; padding: 0.9rem 1rem 0.8rem; }
.fs-mc-top { display: flex; align-items: center; gap: 0.6rem; }
.fs-mc-ic { width: 34px; height: 34px; border-radius: 10px; display: inline-grid; place-items: center; flex: none; }
.fs-mc-label { font-size: 0.92rem; color: #3A463F; line-height: 1.25; }
.fs-mc-help { margin-left: auto; width: 18px; height: 18px; border-radius: 50%; border: 1.5px solid #A3AFA6; color: #7A867E;
  font-size: 0.7rem; font-weight: 700; display: inline-grid; place-items: center; cursor: help; flex: none; }
.fs-mc-value { font-size: 2.35rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.05; margin-top: 0.6rem; color: #1F2A24; }
.fs-mc-value small { font-size: 1.1rem; font-weight: 400; color: #5E6B63; margin-left: 0.25rem; }
.fs-mc-pill { display: inline-block; margin-top: 0.5rem; font-size: 0.8rem; font-weight: 600; border-radius: 999px; padding: 0.18rem 0.65rem; }
.fs-mc-pill.bad { background: #FBE7E5; color: #B3261E; } .fs-mc-pill.good { background: #E3F1E7; color: #1E6B3A; }
.fs-mc-pill.info { background: #EEF1EC; color: #5E6B63; }
.fs-mc-src { font-size: 0.78rem; color: #7A867E; margin-top: 0.45rem; }

/* ---------- tabs: one small card per page, big icon above the name ---------- */
[role="tablist"] { display: grid !important; grid-template-columns: repeat(auto-fit, minmax(96px, 1fr));
  gap: 8px; border-bottom: 0 !important; margin-bottom: 0.6rem; overflow: visible !important; }
[data-testid="stTab"] { display: flex; justify-content: center; align-items: center; height: auto !important;
  margin: 0 !important; padding: 0.75rem 0.3rem 0.65rem !important; border-radius: 12px; background: #FFFFFF;
  border: 1px solid #DDE3D8; cursor: pointer; transition: background .15s ease, border-color .15s ease, transform .15s ease; }
[data-testid="stTab"]:hover { border-color: #9DB8A6; transform: translateY(-1px); }
[data-testid="stTab"] p { display: flex; flex-direction: column; align-items: center; gap: 0.35rem; margin: 0;
  font-size: 0.84rem; font-weight: 500; color: #3A463F; text-align: center; line-height: 1.15; }
[data-testid="stTab"] p span[role="img"] { font-size: 1.55rem !important; color: #6B7A70; vertical-align: 0 !important; }
[data-testid="stTab"][aria-selected="true"] { background: #E8F0EA; border-color: #2F6B4F; box-shadow: inset 0 -3px 0 #2F6B4F; }
[data-testid="stTab"][aria-selected="true"] p,
[data-testid="stTab"][aria-selected="true"] p span[role="img"] { color: #2F6B4F; font-weight: 600; }
[data-testid="stTab"]:focus-visible { outline: 2px solid #2F6B4F; outline-offset: 2px; }
[role="tablist"] .react-aria-SelectionIndicator, [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }
@media (max-width: 640px) { [role="tablist"] { grid-template-columns: repeat(3, 1fr); } }
/* Tab bar stays at the top like a navigation bar (wide screens, where it fits on one row) */
@media (min-width: 900px) {
  [data-testid="stTabs"] [role="tablist"] { position: sticky !important; top: 3.75rem; z-index: 999;
    background: #F2F4EF; padding-top: 0.5rem; padding-bottom: 0.45rem; }
  [data-testid="stHeader"] { background: #F2F4EF !important; }   /* nothing shows above the bar */
}

/* ---------- alerts in saffron ---------- */
[data-testid="stAlertContentWarning"] { color: #5C4210; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] h2 { font-family: 'Instrument Sans', sans-serif !important; }
.fs-side-brand { font-family: 'Instrument Sans', sans-serif; font-weight: 800;
                 font-size: 1.35rem; color: #E9EFE6; margin-bottom: 0.1rem; }
.fs-side-sub { color: #A9BCAE; font-size: 0.82rem; margin-bottom: 1rem; }


/* ---------- sections ---------- */
.fs-section { margin: 1.6rem 0 0.6rem; }
.fs-section h3 { font-family: 'Instrument Sans', sans-serif !important; font-weight: 700;
                 font-size: 1.55rem; margin: 0 0 0.25rem; color: #1F2A24; }
.fs-section p { color: #5E6B63; margin: 0; max-width: 46rem; }

/* ---------- crop recommendation cards ---------- */
.fs-reco { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; margin: 0.9rem 0 0.8rem; }
.fs-card { background: #FFFFFF; border: 1px solid #D3DBCF; border-radius: 12px; padding: 1.1rem 1.15rem 0.9rem; }
.fs-card.best { border: 2px solid #2F6B4F; box-shadow: 0 6px 20px rgba(47, 107, 79, 0.12); }
.fs-card .rank { font-size: 0.8rem; font-weight: 600; color: #2F6B4F; }
.fs-card.best .rank { display: inline-block; background: #2F6B4F; color: #fff; border-radius: 999px;
                      padding: 0.1rem 0.6rem; }
.fs-card .head { display: flex; align-items: center; gap: 0.6rem; margin: 0.55rem 0 0.4rem; }
.fs-card .ic { font-size: 2.1rem; line-height: 1; }
.fs-card .name { font-family: 'Instrument Sans', sans-serif; font-weight: 800; font-size: 1.55rem;
                 color: #1F2A24; line-height: 1.05; }
.fs-card .family { color: #6B7A70; font-size: 0.8rem; }
.fs-card .match { display: flex; align-items: center; gap: 0.55rem; font-size: 0.85rem; color: #4F5E55; }
.fs-card .bar { flex: 1; height: 0.45rem; background: #E6EBE2; border-radius: 999px; overflow: hidden; }
.fs-card .bar span { display: block; height: 100%; background: #2F6B4F; border-radius: 999px; }
.fs-card .match b { color: #1F2A24; font-size: 1rem; }
.fs-card .sow { margin: 0.55rem 0 0.4rem; font-size: 0.88rem; color: #1F2A24; }
.fs-card ul { list-style: none; padding: 0; margin: 0.35rem 0 0; }
.fs-card li { font-size: 0.87rem; line-height: 1.4; padding: 0.22rem 0 0.22rem 1.25rem; position: relative; color: #2C3A31; }
.fs-card li.why::before { content: "✓"; position: absolute; left: 0; color: #2F6B4F; font-weight: 700; }
.fs-card li.watch::before { content: "!"; position: absolute; left: 0.25rem; color: #A87418; font-weight: 800; }
.fs-avoid { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; margin: 0.2rem 0 0.6rem;
            font-size: 0.88rem; color: #4F5E55; }
.fs-avoid .chip { background: #FBF3E4; border: 1px solid #E8D3A8; color: #5C4210; border-radius: 999px;
                  padding: 0.2rem 0.75rem; }
.fs-context { background: #FBF3E4; border-left: 3px solid #C8912E; padding: 0.5rem 0.8rem; margin-top: 0.6rem;
              color: #5C4210; font-size: 0.9rem; border-radius: 0; }
@media (max-width: 900px) { .fs-reco { grid-template-columns: 1fr; } }

@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
</style>
"""

INSTRUMENTS = [("power", "NASA POWER"), ("smap", "SMAP"), ("gpm", "GPM IMERG"), ("modis", "MODIS"),
               ("ecostress", "ECOSTRESS"), ("landsat", "Landsat"), ("srtm", "SRTM")]


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def sidebar_brand():
    from src.report import ICON_SVG
    st.sidebar.markdown('<div class="fs-side-brand" style="display:flex;align-items:center;gap:10px">'
                        + ICON_SVG.replace('width="44" height="44"', 'width="34" height="34"') + 'TerraShift</div>'
                        '<div class="fs-side-sub">Farm decisions from NASA data</div>',
                        unsafe_allow_html=True)


def _coord(value, pos, neg):
    return f"{abs(value):.4f}° {pos if value >= 0 else neg}"


def _satellite_image(lat, lon, half_km=1.2):
    """Esri World Imagery picture of the area around the field."""
    import math
    dlat = half_km / 111.32
    dlon = half_km / (111.32 * math.cos(math.radians(lat)))
    b = f"{lon - dlon * 1.9},{lat - dlat},{lon + dlon * 1.9},{lat + dlat}"
    return ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?"
            f"bbox={b}&bboxSR=4326&imageSR=4326&size=1600,840&format=jpg&f=image")


def hero(field_name, lat, lon, start, end, loaded, elevation=None):
    """Cover: the field seen from space, its name, where/when, and each NASA instrument's status."""
    chips = []
    for key, label in INSTRUMENTS:
        on = key == "power" or key in loaded
        from src.i18n import t as _t
        title = _t("data_loaded") if on else _t("not_downloaded")
        chips.append(f'<span class="fs-chip {"on" if on else "off"}" title="{title}"><i></i>{label}</span>')
    from src.i18n import t as _t
    elev = f" &nbsp;&nbsp; {_t('elevation')} <b>{elevation:.0f} m</b>" if elevation is not None else ""
    st.markdown(f"""
<div class="fs-cover" style="background-image:url('{_satellite_image(lat, lon)}')">
  <div class="fs-crosshair" title="Your field"></div>
  <div class="fs-cover-inner">
    <div class="fs-brand">TerraShift</div>
    <div class="fs-field">{html.escape(field_name)}</div>
    <div class="fs-meta"><b>{_coord(lat, "N", "S")}, {_coord(lon, "E", "W")}</b>{elev}
        &nbsp;&nbsp; {_t('weather_from')} <b>{start:%d %b %Y}</b> {_t('to')} <b>{end:%d %b %Y}</b></div>
    <div class="fs-instruments">{''.join(chips)}</div>
  </div>
</div>""", unsafe_allow_html=True)


def verdict(headline, tone, reasons):
    items = "".join(f'<li class="{lvl}">{html.escape(text)}</li>' for lvl, text in reasons)
    st.markdown(f"""
<div class="fs-verdict">
  <div><div class="tone {tone}"></div><h2>{html.escape(headline)}</h2></div>
  <ul class="fs-reasons">{items}</ul>
</div>""", unsafe_allow_html=True)


MC_ICONS = {
    "drop": '<path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z"/>',
    "thermo": '<path d="M14 4v10.5a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z"/><path d="M2 21c0-3 1.9-5.4 5.1-6"/>',
    "rain": '<path d="M4 14.9A7 7 0 1 1 15.7 8h1.8a4.5 4.5 0 0 1 2.5 8.2"/><path d="M16 14v6M8 14v6M12 16v6"/>',
    "sat": '<path d="M13 7 9 3 5 7l4 4"/><path d="m17 11 4 4-4 4-4-4"/><path d="m8 12 4 4 6-6-4-4Z"/><path d="M9 21a6 6 0 0 0-6-6"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
}


def _mc_icon(name, color, size=20):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{MC_ICONS[name]}</svg>')


def metric_group(title, color, icon, cards):
    """One group of metric cards (Overview). cards = list of dicts:
    icon, label, value, unit, note, tone ("good" / "bad" / "info"), source, help (tooltip text)."""
    html_cards = []
    for c in cards:
        tip = " ".join((c.get("help") or "").replace("*", "").replace("_", " ").split())
        tip = html.escape(tip, quote=True)
        help_dot = f'<span class="fs-mc-help" title="{tip}">?</span>' if tip else ""
        pill = (f'<span class="fs-mc-pill {c.get("tone", "info")}">{html.escape(c["note"])}</span>'
                if c.get("note") else "")
        html_cards.append(
            f'<div class="fs-mc"><div class="fs-mc-top"><span class="fs-mc-ic" style="background:{color}1A">'
            f'{_mc_icon(c["icon"], color)}</span><span class="fs-mc-label">{html.escape(c["label"])}</span>{help_dot}</div>'
            f'<div class="fs-mc-value">{html.escape(c["value"])}<small>{html.escape(c.get("unit", ""))}</small></div>'
            f'{pill}<div class="fs-mc-src">{html.escape(c.get("source", ""))}</div></div>')
    st.markdown(f'<div class="fs-mg-head" style="color:{color}">{_mc_icon(icon, color, 18)} {html.escape(title)}</div>'
                f'<div class="fs-mg">{"".join(html_cards)}</div>', unsafe_allow_html=True)


def group(title):
    st.markdown(f'<div class="fs-group">{html.escape(title)}</div>', unsafe_allow_html=True)


def section(title, subtitle=""):
    st.markdown(f'<div class="fs-section"><h3>{html.escape(title)}</h3>'
                f'<p>{html.escape(subtitle)}</p></div>', unsafe_allow_html=True)


def crop_cards(reco, season):
    """Top 3 crops as cards + crops better avoided this season."""
    cards = []
    for i, row in reco.head(3).iterrows():
        rank = "Best choice" if i == 0 else f"Option {i + 1}"
        why = "".join(f'<li class="why">{html.escape(t)}</li>' for t in row["reasons"][:4])
        watch = "".join(f'<li class="watch">{html.escape(t)}</li>' for t in row["warnings"][:3])
        pct = int(round(100 * row["score"]))
        cards.append(f"""
<div class="fs-card {'best' if i == 0 else ''}">
  <span class="rank">{rank}</span>
  <div class="head"><span class="ic">{row['icon']}</span>
    <div><div class="name">{html.escape(row['crop'])}</div><div class="family">{html.escape(row['family'])}</div></div></div>
  <div class="match"><div class="bar"><span style="width:{pct}%"></span></div><b>{pct}%</b> match</div>
  <div class="sow">Sow around <b>{row['sow']:%d %b %Y}</b></div>
  <ul>{why}{watch}</ul>
</div>""")
    avoid = reco.iloc[3:][reco.iloc[3:]["score"] < 0.5].sort_values("score").head(3)
    chips = "".join(f'<span class="chip">{r["icon"]} {html.escape(r["crop"])}: '
                    f'{html.escape(r["main_warning"] or "low match")}</span>' for _, r in avoid.iterrows())
    context = "".join(f'<div class="fs-context">{html.escape(c)}</div>' for c in reco.attrs.get("context", []))
    st.markdown(f'<div class="fs-reco">{"".join(cards)}</div>'
                + (f'<div class="fs-avoid">Better avoided in {season}: {chips}</div>' if chips else "")
                + context, unsafe_allow_html=True)
