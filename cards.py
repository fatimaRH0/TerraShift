"""
cards.py - Metric cards of the Overview tab (Water / Heat / Vegetation):
icon, full label, big value, a red/green comparison pill and the data source.
"""

import html

import streamlit as st


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
                f'<div class="fs-mg" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">{"".join(html_cards)}</div>', unsafe_allow_html=True)


def water_share(summary):
    from src import i18n
    from src.crop_icons import icon as crop_icon
    """Water needs per crop as 100 % bars: blue = part covered by rain, orange = part to irrigate.
    summary = crops.crop_summary(...) (normal year = median of the past seasons)."""
    blue, orange = "#2E6F9E", "#E59A2B"
    rows = summary[summary["Crop water use (mm)"] > 0].copy()
    rows["share"] = rows["Rain covers (%)"].clip(0, 100) / 100
    rows = rows.sort_values("share", ascending=False)
    lines = []
    for _, r in rows.iterrows():
        p = float(r["share"])
        rain_w = i18n.t("rain_word")
        inside = f'{p:.0%} {rain_w}' if p >= 0.14 else ""
        outside = "" if inside else (f'<span style="color:#5A3A00;font-size:0.8rem;font-weight:700;'
                                     f'padding-left:8px;display:flex;align-items:center">{p:.0%} {rain_w}</span>')
        lines.append(
            f'<div style="display:grid;grid-template-columns:190px minmax(0,1fr) 420px;gap:14px;align-items:center;'
            f'padding:6px 0">'
            f'<span style="display:flex;align-items:center;gap:10px">{crop_icon(r["Crop"], 34)}'
            f'<b style="font-size:0.98rem">{html.escape(i18n.crop(str(r["Crop"])))}</b></span>'
            f'<div style="display:flex;height:24px;border-radius:6px;overflow:hidden;background:{orange}">'
            f'<div style="width:{p * 100:.1f}%;background:{blue};color:#fff;font-size:0.8rem;font-weight:700;'
            f'display:flex;align-items:center;padding-left:8px;white-space:nowrap">{inside}</div>{outside}</div>'
            f'<span style="font-size:0.9rem;color:#3A463F">{i18n.t("needs")} <b>{r["Crop water use (mm)"]:.0f} mm</b> · '
            f'{i18n.t("irrigate")} <b>{r["Irrigation – normal year (mm)"]:.0f} mm</b>'
            f'<span style="color:#7A867E"> ({r["Irrigation – dry year (mm)"]:.0f} {i18n.t("in_dry")})</span></span></div>')
    legend = (f'<div style="display:flex;gap:22px;margin-top:10px;font-size:0.85rem;color:#5E6B63">'
              f'<span><i style="display:inline-block;width:12px;height:12px;border-radius:3px;background:{blue};'
              f'margin-right:6px;vertical-align:-1px"></i>{i18n.t("legend_rain")}</span>'
              f'<span><i style="display:inline-block;width:12px;height:12px;border-radius:3px;background:{orange};'
              f'margin-right:6px;vertical-align:-1px"></i>{i18n.t("legend_irr")}</span></div>')
    st.markdown(f'<div style="background:#fff;border:1px solid #DDE3D8;border-radius:14px;padding:12px 20px 14px">'
                f'{"".join(lines)}{legend}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# "Build your rotation" (Crops tab)
# ---------------------------------------------------------
BUILDER_CSS = """<style>
[class*="st-key-fs_past"], [class*="st-key-fs_now"] { border-radius: 14px; padding: 0.7rem 0.85rem 0.6rem;
  border: 1.5px solid #DDE3D8; background: #FAFBF8; }
[class*="st-key-fs_now"] { border: 2px solid #2F6B4F; background: #F1F7F2; box-shadow: 0 6px 18px rgba(47,107,79,.12); }
.fs-b-lab { font-size: 0.74rem; font-weight: 700; color: #7A867E; letter-spacing: .02em; }
[class*="st-key-fs_now"] .fs-b-lab { color: #2F6B4F; }
.fs-b-crop { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.35rem; flex-wrap: wrap; }
.fs-b-fam { font-size: 0.75rem; font-weight: 700; border-radius: 999px; padding: 0.1rem 0.55rem; }
.fs-b-arrow { text-align: center; font-size: 1.4rem; color: #9DB8A6; }
.fs-b-tiles { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.75rem; margin: 0.9rem 0 0.6rem; }
.fs-b-tile { background: #F3F5F0; border-radius: 12px; padding: 0.75rem 0.9rem; }
.fs-b-tile small { display: block; color: #5E6B63; font-size: 0.82rem; }
.fs-b-tile b { font-size: 1.7rem; letter-spacing: -0.01em; }
.fs-b-tile em { display: block; font-style: normal; font-size: 0.78rem; font-weight: 700; color: #5E6B63; }
.fs-b-tile em.good { color: #1E6B3A; } .fs-b-tile em.bad { color: #B3261E; }
.fs-b-verdict { border-radius: 12px; padding: 0.7rem 1rem; font-weight: 700; margin: 0.3rem 0 0.5rem; }
.fs-b-verdict.ok { background: #E3F1E7; color: #1E6B3A; } .fs-b-verdict.info { background: #FFF4DE; color: #7A4A00; }
.fs-b-pc { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem 1.2rem; font-size: 0.92rem; }
.fs-b-chips { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; font-size: 0.88rem; color: #5E6B63; margin-top: 0.5rem; }
.fs-b-chip { display: inline-flex; align-items: center; gap: 0.35rem; border: 1px solid #DDE3D8; border-radius: 999px;
  padding: 0.15rem 0.7rem 0.15rem 0.2rem; background: #fff; font-weight: 700; color: #1F2A24; }
@media (max-width: 900px) { .fs-b-tiles, .fs-b-pc { grid-template-columns: 1fr 1fr; } }
</style>"""

FAMILY_COLOR = {"Cereal": "#C8912E", "Legume": "#2F6B4F", "Fallow": "#8A6A4A"}


def season_label(text):
    return f'<div class="fs-b-lab">{html.escape(text)}</div>'


def crop_badge(crop, extra=""):
    """Icon + family pill (+ optional extra pill) under a season selector."""
    from src import i18n
    from src.crop_icons import icon as crop_icon
    from src.crops import CROPS
    fam = CROPS[crop]["family"]
    c = FAMILY_COLOR.get(fam, "#5E6B63")
    return (f'<div class="fs-b-crop">{crop_icon(crop, 40)}<span class="fs-b-fam" style="background:{c}1F;color:{c}">'
            f'{html.escape(i18n.family(fam))}</span>{extra}</div>')


def pill(text, solid=False):
    style = ("background:#2F6B4F;color:#fff" if solid else "background:#EEF1EC;color:#5E6B63")
    return f'<span class="fs-b-fam" style="{style}">{html.escape(text)}</span>'


def chips(label, crops_pcts):
    from src import i18n
    from src.crop_icons import icon as crop_icon
    items = "".join(f'<span class="fs-b-chip">{crop_icon(c, 24)}{html.escape(i18n.crop(c))} · {p}%</span>'
                    for c, p in crops_pcts)
    return f'<div class="fs-b-chips">{html.escape(label)} {items}</div>'


def tiles(items):
    """items = [(label, value, note, tone)]  tone: good / bad / ''"""
    cells = "".join(f'<div class="fs-b-tile"><small>{html.escape(l)}</small><b>{html.escape(v)}</b>'
                    f'<em class="{tone}">{html.escape(n)}</em></div>' for l, v, n, tone in items)
    return f'<div class="fs-b-tiles">{cells}</div>'


def verdict_box(text, tone="ok"):
    return f'<div class="fs-b-verdict {tone}">{html.escape(text)}</div>'


def pros_cons(reasons, warnings):
    left = "<br>".join("✅ " + html.escape(r) for r in reasons[:4])
    right = "<br>".join("⚠️ " + html.escape(w) for w in warnings[:3])
    return f'<div class="fs-b-pc"><div>{left}</div><div>{right}</div></div>'


# ---------------------------------------------------------
# Assistant (chat + field panel)
# ---------------------------------------------------------
CHAT_CSS = """<style>
[class*="st-key-fs_chat"] { background: #fff; border: 1px solid #DDE3D8; border-radius: 16px; padding: 0 0 0.6rem; overflow: hidden; }
[class*="st-key-fs_side"] { background: #fff; border: 1px solid #DDE3D8; border-radius: 16px; padding: 1rem 1.1rem; }
.fs-ch-head { display: flex; align-items: center; gap: 0.75rem; padding: 0.9rem 1.1rem 0.2rem; }
.fs-ch-av { width: 40px; height: 40px; border-radius: 50%; background: #2F6B4F; display: grid; place-items: center; flex: none; }
.fs-ch-head b { font-size: 1.08rem; display: block; } .fs-ch-head small { color: #5E6B63; font-size: 0.82rem; }
.fs-ch-head small span { color: #2F6B4F; font-weight: 700; }
[class*="st-key-fs_chat"] [data-testid="stChatMessage"] { background: transparent; padding: 0.35rem 1.1rem; }
[class*="st-key-fs_chat"] [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
  background: #fff; border: 1px solid #DDE3D8; border-radius: 16px 16px 16px 4px; padding: 0.6rem 0.9rem; max-width: 80%; }
[class*="st-key-fs_chat"] [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { flex-direction: row-reverse; }
[class*="st-key-fs_chat"] [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
  background: #2F6B4F; border-color: #2F6B4F; border-radius: 16px 16px 4px 16px; flex: 0 1 auto; margin-left: auto; }
[class*="st-key-fs_chat"] [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p { color: #fff; }
[class*="st-key-fs_chat"] [data-testid="stChatMessageAvatarCustom"] { background: #2F6B4F; color: #fff; border-radius: 50%; }
[class*="st-key-fs_chat"] [data-testid="stChatMessageAvatarCustom"] [data-testid="stIconMaterial"] { color: #fff; }
[class*="st-key-fs_chat"] [data-testid="stChatMessageAvatarUser"] { background: #E8F0EA; color: #2F6B4F; }
[class*="st-key-fs_chat"] [data-testid="stChatInput"] { margin: 0.4rem 1.1rem 0; border: 1.5px solid #CFE0D4; border-radius: 14px; }
[class*="st-key-fs_chat"] [data-testid="stChatInput"] button { background: #2F6B4F; color: #fff; border-radius: 10px; }
[class*="st-key-fs_chat"] [data-testid="stChatMessageContent"] :is(p, li) { unicode-bidi: plaintext; text-align: start; }
.fs-ch-empty { margin: 0.6rem 1.1rem; padding: 0.8rem 1rem; border-radius: 12px; background: #F1F7F2; color: #2F6B4F; font-size: 0.92rem; }
.fs-ch-kv { display: flex; justify-content: space-between; gap: 1rem; padding: 0.55rem 0; border-bottom: 1px solid #EEF1EC; font-size: 0.93rem; }
.fs-ch-kv span { color: #5E6B63; } .fs-ch-kv b { text-align: right; }
.fs-ch-h { font-weight: 700; font-size: 1.02rem; margin: 0.2rem 0 0.5rem; }
[class*="st-key-sugg_"] button { justify-content: flex-start; text-align: left; font-weight: 600; }
[class*="st-key-sugg_"] button > div { justify-content: flex-start; width: 100%; }
[class*="st-key-sugg_"] button p { text-align: start; }
</style>"""

LEAF_WHITE = ('<svg width="22" height="22" viewBox="0 0 24 24" fill="#fff" aria-hidden="true"><path d="M11 20A7 7 0 '
              '0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z"/></svg>')


def chat_header(title, ready, subtitle):
    return (f'<div class="fs-ch-head"><span class="fs-ch-av">{LEAF_WHITE}</span><div><b>{html.escape(title)}</b>'
            f'<small><span>{html.escape(ready)}</span> · {html.escape(subtitle)}</small></div></div>')


def chat_empty(text):
    return f'<div class="fs-ch-empty">{html.escape(text)}</div>'


def key_facts(title, rows):
    items = "".join(f'<div class="fs-ch-kv"><span>{html.escape(k)}</span><b>{html.escape(v)}</b></div>' for k, v in rows)
    return f'<div class="fs-ch-h">{html.escape(title)}</div>{items}'


# ---------------------------------------------------------
# 3D farm: NDVI before -> after story
# ---------------------------------------------------------
_TI = ('<span style="font-family:\'Material Symbols Rounded\';font-size:18px;vertical-align:-4px;font-weight:400">{}</span>')


def _ndvi_word(v):
    return "mostly bare soil" if v < 0.2 else "sparse plants" if v < 0.4 else "good vegetation"


def ndvi_story(ndvi_a, date_a, ndvi_b, date_b, temp_b, pixels):
    def side(v, d, label, align):
        if v is None:
            return f'<div style="text-align:{align}"><div class="fs-st-s">{label}</div><div class="fs-st-v">–</div></div>'
        col = "#3B6D11" if v >= 0.25 else "#854F0B"
        return (f'<div style="text-align:{align}"><div class="fs-st-s">{label} · {d:%d %b}</div>'
                f'<div class="fs-st-v" style="color:{col}">{v:.2f}</div>'
                f'<div class="fs-st-s">{_ndvi_word(v)}</div></div>')

    if ndvi_a is not None and ndvi_b is not None:
        diff = ndvi_b - ndvi_a
        pct = f" ({diff / ndvi_a:+.0%})" if ndvi_a else ""
        down = diff < 0
        pill_bg, pill_fg = ("#FAEEDA", "#633806") if down else ("#E5F1E3", "#27500A")
        icon = "trending_down" if down else "trending_up"
        word = "less vegetation" if down else "more vegetation"
        c1, c2 = ("#97C459", "#DFC27D") if down else ("#DFC27D", "#97C459")
        middle = (f'<div style="flex:1;text-align:center;min-width:120px"><div style="height:6px;border-radius:3px;'
                  f'background:linear-gradient(90deg,{c1},{c2})"></div><span class="fs-st-pill" '
                  f'style="background:{pill_bg};color:{pill_fg}">{_TI.format(icon)} {diff:+.2f}{pct} {word}</span></div>')
    else:
        middle = '<div style="flex:1"></div>'

    def chip(icon, label, value):
        return (f'<div class="fs-st-card fs-st-chip"><span class="fs-st-s">{_TI.format(icon)} {label}</span>'
                f'<b>{value}</b></div>')

    temp = f"{temp_b:.1f} °C" if temp_b is not None else "–"
    return (
        "<style>.fs-st{display:grid;grid-template-columns:minmax(0,2.2fr) minmax(0,1fr);gap:12px;margin:.4rem 0 1rem}"
        ".fs-st-card{background:#fff;border:1px solid #DDE3D8;border-radius:14px;padding:14px 18px}"
        ".fs-st-main{display:flex;align-items:center;gap:18px}"
        ".fs-st-s{font-size:.85rem;color:#5E6B63}.fs-st-v{font-size:2rem;font-weight:700;line-height:1.15}"
        ".fs-st-pill{display:inline-block;margin-top:8px;font-size:.85rem;font-weight:600;padding:3px 12px;border-radius:999px}"
        ".fs-st-chip{display:flex;justify-content:space-between;align-items:center;padding:10px 16px}"
        ".fs-st-chip b{font-size:1.15rem}.fs-st-side{display:grid;gap:10px}"
        "@media(max-width:800px){.fs-st{grid-template-columns:1fr}}</style>"
        f'<div class="fs-st"><div class="fs-st-card fs-st-main">{side(ndvi_a, date_a, "Period A", "left")}{middle}'
        f'{side(ndvi_b, date_b, "Period B", "right")}</div><div class="fs-st-side">'
        f'{chip("device_thermostat", "Ground heat", temp)}{chip("hexagon", "Landsat pixels (30 m)", pixels)}</div></div>')


# ---------------------------------------------------------
# Download report card
# ---------------------------------------------------------
REPORT_CSS = """<style>
[class*="st-key-fs_report"] { background: #F7FAF6; border: 1px solid #CFE0D4; border-radius: 14px; padding: 10px 16px; margin: .6rem 0 1rem; }
.fs-rp { display: flex; align-items: center; gap: 14px; }
.fs-rp-doc { width: 44px; height: 52px; border-radius: 7px; background: #fff; border: 1px solid #DDE3D8; display: grid; place-items: center; flex: none; }
.fs-rp b { display: block; font-size: 1.02rem; } .fs-rp small { color: #5E6B63; font-size: .86rem; }
[class*="st-key-dl_report"] button { background: #2F6B4F; border-color: #2F6B4F; border-radius: 10px; font-weight: 600; }
[class*="st-key-dl_report"] button:hover { background: #255A41; border-color: #255A41; }
</style>"""

DOC_ICON = ('<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2F6B4F" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3v4a1 1 0 0 0 1 1h4"/>'
            '<path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13h6M9 17h6"/></svg>')


def report_card(title, subtitle):
    return (REPORT_CSS + f'<div class="fs-rp"><span class="fs-rp-doc">{DOC_ICON}</span><div>'
            f'<b>{html.escape(title)}</b><small>{html.escape(subtitle)}</small></div></div>')
