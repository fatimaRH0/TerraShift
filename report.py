"""
report.py - Exportable field report (function 9: "Exporter une synthèse ou un rapport").
One self-contained HTML page: open it in any browser, print it or save it as PDF.
Layout: one-page farmer sheet (header, verdict, key numbers, suggested crops, alerts, sources).
"""

import html
from datetime import datetime

ICON_SVG = ('<svg viewBox="0 0 64 64" width="44" height="44" xmlns="http://www.w3.org/2000/svg">'
            '<rect width="64" height="64" rx="16" fill="#1F3D2E"/><circle cx="32" cy="36" r="17" fill="#2F6B4F"/>'
            '<path d="M15 36 Q32 30 49 36" stroke="#C9A35A" stroke-width="2.5" fill="none"/>'
            '<path d="M17 43 Q32 38 47 43" stroke="#C9A35A" stroke-width="2.5" fill="none"/>'
            '<path d="M20 29 Q32 25 44 29" stroke="#9FD07A" stroke-width="2.5" fill="none"/>'
            '<path d="M8 22 Q32 2 56 22" stroke="#E8F0EA" stroke-width="1.6" fill="none" stroke-dasharray="3 3"/>'
            '<g transform="rotate(25 45 11)"><rect x="41" y="8" width="9" height="6" rx="1.5" fill="#E8F0EA"/>'
            '<rect x="36" y="9" width="5" height="3" fill="#8FB8E0"/><rect x="50" y="9" width="5" height="3" '
            'fill="#8FB8E0"/></g></svg>')

TONES = {"warn": ("#FAEEDA", "#633806", "#C8912E"), "info": ("#E6F1FB", "#0C447C", "#378ADD"),
         "ok": ("#E5F1E3", "#27500A", "#2F6B4F")}


def build_html(field_name, lat, lon, headline, reasons, facts, alerts, crop_cards=None,
               best_scenario=None, limits=None, tone="info", place=None, key_numbers=None):
    esc = html.escape

    bg, fg, bar = TONES.get(tone, TONES["info"])
    why = "".join(f"<li class='{lvl}'>{esc(t)}</li>" for lvl, t in reasons)

    tiles = "".join(f"<div class='k'><span>{esc(n)}</span><b>{esc(v)}</b></div>"
                    for n, v in (key_numbers or []))
    tiles = f"<div class='kpis'>{tiles}</div>" if tiles else ""

    crops = ""
    if crop_cards is not None and len(crop_cards):
        cards = []
        for i, r in enumerate(crop_cards.head(3).itertuples()):
            sow = f"<small>sow around {r.sow:%d %b %Y}</small>" if getattr(r, "sow", None) is not None else ""
            why_c = f"<p>{esc(r.reasons[0])}</p>" if i == 0 and getattr(r, "reasons", None) else ""
            cards.append(f"<div class='crop{' best' if i == 0 else ''}'><b>{esc(r.crop)} · {r.score:.0%}</b>"
                         f"{sow}{why_c}</div>")
        crops = "<h2>Suggested crop for this season</h2><div class='crops'>" + "".join(cards) + "</div>"
    scen = (f"<p class='scen'><b>Best rotation for your criteria:</b> {esc(best_scenario)}</p>"
            if best_scenario else "")

    alert_li = "".join(f"<li>{esc(a)}</li>" for a in alerts) or "<li>No alert for this period.</li>"
    rows = "".join(f"<tr><td>{esc(f['name'])}</td><td><b>{esc(str(f['value']))}</b></td>"
                   f"<td class='src'>{esc(f['source'])}</td></tr>" for f in facts)
    lim = "".join(f"<li>{esc(x)}</li>" for x in (limits or []))
    where = f"{esc(place)} · " if place else ""

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>TerraShift report – {esc(field_name)}</title>
<style>
 @import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&display=swap');
 * {{ box-sizing: border-box }}
 body {{ font-family: 'Instrument Sans', Arial, sans-serif; color:#1E2A22; background:#E6E9E2; margin:0; padding:24px 12px }}
 .page {{ background:#fff; max-width: 800px; margin:0 auto; padding:26px 30px; border-radius:10px; line-height:1.5 }}
 .head {{ background:#2F6B4F; color:#fff; border-radius:10px; padding:16px 20px; display:flex; justify-content:space-between; align-items:center; gap:16px }}
 .head small {{ opacity:.85; display:block }} .head h1 {{ margin:2px 0; font-size:1.8rem; font-weight:700 }}
 .verdict {{ margin:16px 0 12px; padding:12px 16px; border-radius:10px; background:{bg}; color:{fg}; border-left:4px solid {bar} }}
 .verdict b {{ font-size:1.15rem; display:block; margin-bottom:4px }} .verdict ul {{ margin:4px 0 0; padding-left:18px }}
 .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px }}
 .k {{ background:#F2F4EF; border-radius:10px; padding:10px 12px }} .k span {{ color:#5E6B63; font-size:.85rem }}
 .k b {{ display:block; font-size:1.35rem }}
 h2 {{ font-size:1rem; color:#2F6B4F; margin:20px 0 8px }}
 .crops {{ display:grid; grid-template-columns:1.4fr 1fr 1fr; gap:10px }}
 .crop {{ background:#F2F4EF; border-radius:10px; padding:10px 12px }} .crop small {{ display:block; color:#5E6B63 }}
 .crop.best {{ background:#fff; border:2px solid #2F6B4F }} .crop p {{ margin:6px 0 0; font-size:.85rem; color:#3B4A41 }}
 .scen {{ font-size:.9rem; margin:8px 0 0 }}
 ul {{ margin:0; padding-left:20px }} li.warn::marker {{ color:#C8912E }} li.ok::marker {{ color:#2F6B4F }} li.info::marker {{ color:#378ADD }}
 table {{ border-collapse:collapse; width:100%; font-size:.9rem }} td {{ border-bottom:1px solid #EEF1EC; padding:5px 6px; vertical-align:top }}
 .src {{ color:#6B7A70; font-size:.82rem; text-align:right }}
 .limits {{ font-size:.82rem; color:#5E6B63 }} .foot {{ margin-top:16px; font-size:.8rem; color:#5E6B63; border-top:1px solid #EEF1EC; padding-top:10px }}
 @media (max-width:640px) {{ .kpis, .crops {{ grid-template-columns:1fr 1fr }} }}
 @media print {{ body {{ background:#fff; padding:0 }} .page {{ padding:0; max-width:none }}
   .head, .verdict, .k, .crop {{ -webkit-print-color-adjust:exact; print-color-adjust:exact }} }}
</style></head><body><div class="page">
<div class="head"><div><small>TerraShift · field report · {datetime.now():%d %b %Y}</small>
<h1>{esc(field_name)}</h1><small>{where}{lat:.4f}, {lon:.4f}</small></div>{ICON_SVG}</div>
<div class="verdict"><b>{esc(headline)}</b><ul>{why}</ul></div>
{tiles}
{crops}{scen}
<h2>Alerts</h2><ul>{alert_li}</ul>
<h2>Numbers and their sources</h2><table>{rows}</table>
<h2>Limits</h2><ul class="limits">{lim}</ul>
<div class="foot">This report supports decisions; it does not replace a field visit or the advice of an agronomist.
NASA provides observations and estimates; predictions and simulations are computed by TerraShift and are not official NASA forecasts.</div>
</div></body></html>"""
