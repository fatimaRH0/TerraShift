"""
references.py - Where every piece of information in TerraShift comes from.
Shown at the bottom of the page, in the user's language (en, fr, ar).
"""

import html

TITLE = ("References and data sources", "Références et sources des données", "المراجع ومصادر البيانات")
HEAD = (("Source", "What TerraShift takes from it", "Provider"),
        ("Source", "Ce que TerraShift en tire", "Fournisseur"),
        ("المصدر", "ماذا يأخذ منه TerraShift", "الجهة"))

GROUPS = [
    (("NASA data (all measurements)", "Données NASA (toutes les mesures)", "بيانات NASA (كل القياسات)"), [
        ("NASA POWER", "https://power.larc.nasa.gov",
         ("Daily rain, temperature, humidity and root-zone wetness, 20 years",
          "Pluie, température, humidité et humidité racinaire par jour, sur 20 ans",
          "المطر والحرارة والرطوبة ورطوبة الجذور يومياً، على 20 سنة"), "NASA LaRC"),
        ("SMAP L4 (SPL4SMGP)", "https://nsidc.org/data/spl4smgp",
         ("Surface and root-zone soil moisture, 9 km", "Humidité du sol en surface et en profondeur, 9 km",
          "رطوبة التربة السطحية والعميقة، 9 كم"), "NASA / NSIDC"),
        ("ECOSTRESS (ECO_L2T_LSTE)", "https://ecostress.jpl.nasa.gov",
         ("Land surface temperature, 70 m", "Température de surface du sol, 70 m", "حرارة سطح الأرض، 70 م"),
         "NASA JPL"),
        ("MODIS MOD13Q1 v6.1", "https://lpdaac.usgs.gov/products/mod13q1v061/",
         ("Vegetation indices NDVI and EVI, 250 m, every 16 days", "Indices de végétation NDVI et EVI, 250 m, tous les 16 jours",
          "مؤشرا الغطاء النباتي NDVI وEVI، 250 م، كل 16 يوماً"), "NASA LP DAAC"),
        ("Landsat 8-9 Collection 2 Level-2", "https://landsat.gsfc.nasa.gov",
         ("NDVI and surface temperature at 30 m (3D farm, zones)", "NDVI et température de surface à 30 m (ferme 3D, zones)",
          "NDVI وحرارة السطح بدقة 30 م (الحقل ثلاثي الأبعاد)"), "NASA / USGS"),
        ("NASADEM / SRTM", "https://lpdaac.usgs.gov/products/nasadem_hgtv001/",
         ("Elevation and slope, 30 m", "Altitude et pente, 30 m", "الارتفاع والميل، 30 م"), "NASA LP DAAC"),
        ("GPM IMERG", "https://gpm.nasa.gov/data/imerg",
         ("Satellite rainfall (optional)", "Pluie mesurée par satellite (optionnel)", "المطر بالأقمار الصناعية (اختياري)"),
         "NASA / JAXA"),
        ("NASA GIBS", "https://www.earthdata.nasa.gov",
         ("Satellite image layers on the map", "Couches d'images satellite sur la carte", "طبقات صور الأقمار على الخريطة"),
         "NASA EOSDIS"),
    ]),
    (("How the NASA data is reached", "Accès aux données NASA", "طريقة الوصول إلى بيانات NASA"), [
        ("NASA AppEEARS", "https://appeears.earthdatacloud.nasa.gov",
         ("Point extraction of SMAP, ECOSTRESS, MODIS, SRTM (Earthdata account)",
          "Extraction au point de SMAP, ECOSTRESS, MODIS, SRTM (compte Earthdata)",
          "استخراج SMAP وECOSTRESS وMODIS وSRTM عند النقطة (حساب Earthdata)"), "NASA LP DAAC"),
        ("Microsoft Planetary Computer", "https://planetarycomputer.microsoft.com",
         ("Public copy of Landsat, MODIS and NASADEM, read without an account",
          "Copie publique de Landsat, MODIS et NASADEM, lue sans compte",
          "نسخة عمومية من Landsat وMODIS وNASADEM، تُقرأ بدون حساب"), "Microsoft"),
    ]),
    (("Methods", "Méthodes", "الطرق العلمية"), [
        ("FAO Irrigation and Drainage Paper 56", "https://www.fao.org/4/x0490e/x0490e00.htm",
         ("Crop water needs: crop coefficients (Kc) and growth stages", "Besoins en eau : coefficients culturaux (Kc) et stades",
          "حاجة الزراعات للماء: المعاملات Kc ومراحل النمو"), "FAO"),
        ("scikit-learn (Random Forest)", "https://scikit-learn.org",
         ("Drought-risk model, trained on the field's own NASA POWER history",
          "Modèle de risque de sécheresse, entraîné sur l'historique NASA POWER du champ",
          "نموذج خطر الجفاف، مُدرَّب على تاريخ NASA POWER للحقل"), "scikit-learn"),
    ]),
    (("Not NASA (display and search only, no number comes from these)",
      "Hors NASA (affichage et recherche seulement, aucun chiffre n'en vient)",
      "خارج NASA (للعرض والبحث فقط، لا يأتي منها أي رقم)"), [
        ("Esri World Imagery", "https://www.esri.com",
         ("Background satellite picture (cover, 3D view)", "Image satellite de fond (accueil, vue 3D)",
          "صورة الخلفية (الصفحة الرئيسية، العرض ثلاثي الأبعاد)"), "Esri"),
        ("Terrain Tiles (Terrarium)", "https://registry.opendata.aws/terrain-tiles/",
         ("Relief drawn in the 3D view (built from SRTM and other elevation data)",
          "Relief dessiné dans la vue 3D (issu de SRTM et d'autres données d'altitude)",
          "التضاريس في العرض ثلاثي الأبعاد (من SRTM ومصادر أخرى)"), "AWS Open Data"),
        ("OpenStreetMap Nominatim, Open-Meteo", "https://nominatim.openstreetmap.org",
         ("Finding a village or town by name", "Recherche d'un village ou d'une ville par son nom",
          "البحث عن قرية أو مدينة بالاسم"), "OpenStreetMap"),
    ]),
]

NOTE = ("The verdict, the crop suggestion and the drought risk are computed by TerraShift from these data: "
        "they are not official NASA forecasts.",
        "Le verdict, la culture conseillée et le risque de sécheresse sont calculés par TerraShift à partir de ces "
        "données : ce ne sont pas des prévisions officielles de la NASA.",
        "النتيجة والزراعة المقترحة وخطر الجفاف يحسبها TerraShift من هذه البيانات: ليست توقعات رسمية من NASA.")

CSS = """<style>
.fs-ref { width: 100%; border-collapse: collapse; font-size: .92rem; margin: .2rem 0 1rem; }
.fs-ref th { text-align: start; color: #5E6B63; font-weight: 600; font-size: .82rem; padding: 4px 8px; border-bottom: 1px solid #DDE3D8; }
.fs-ref td { padding: 7px 8px; border-bottom: 1px solid #EEF1EC; vertical-align: top; }
.fs-ref td:first-child { width: 30%; font-weight: 600; } .fs-ref td:last-child { width: 16%; color: #5E6B63; }
.fs-ref a { color: #2F6B4F; text-decoration: none; } .fs-ref a:hover { text-decoration: underline; }
.fs-ref-g { font-weight: 700; color: #1F3D2E; margin: .9rem 0 .2rem; }
.fs-ref-n { background: #F7FAF6; border: 1px solid #CFE0D4; border-radius: 10px; padding: 10px 14px; color: #2F4A3A; font-size: .92rem; }
</style>"""


def _i(lang):
    return {"en": 0, "fr": 1, "ar": 2}.get(lang, 0)


def title(lang):
    return TITLE[_i(lang)]


def render(lang):
    i = _i(lang)
    esc = html.escape
    out = [CSS]
    for name, rows in GROUPS:
        out.append(f'<div class="fs-ref-g">{esc(name[i])}</div><table class="fs-ref"><tr>'
                   + "".join(f"<th>{esc(h)}</th>" for h in HEAD[i]) + "</tr>")
        for label, url, what, who in rows:
            out.append(f'<tr><td><a href="{esc(url)}" target="_blank" rel="noopener">{esc(label)}</a></td>'
                       f"<td>{esc(what[i])}</td><td>{esc(who)}</td></tr>")
        out.append("</table>")
    out.append(f'<div class="fs-ref-n">{esc(NOTE[i])}</div>')
    return "".join(out)
