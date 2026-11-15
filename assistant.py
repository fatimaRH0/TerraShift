"""
assistant.py - "AI Agronomist" (function 10 of the document).

The assistant ONLY uses the indicators computed by TerraShift (the "facts"),
cites the source of each value, and says what is missing. Simple rules find the
topic of the question (rain, soil, drought, vegetation, temperature, crops) in
English, French or Arabic, and show the matching facts. Free, no internet needed.
The assistant is a TerraShift software feature, not a NASA dataset.
"""

import re

# ---------------------------------------------------------
# Facts: everything the assistant is allowed to use
# ---------------------------------------------------------
def facts_to_text(facts):
    return "\n".join(f"- [{f['source']}] {f['name']}: {f['value']}" for f in facts)


def add(facts, source, name, value):
    if value is not None:
        facts.append({"source": source, "name": name, "value": value})


# ---------------------------------------------------------
# Answers (rules)
# ---------------------------------------------------------
TOPICS = {
    "rain": ["rain", "pluie", "précip", "precip", "مطر", "أمطار", "امطار", "تساقط"],
    "soil": ["soil", "sol", "humid", "moisture", "تربة", "رطوبة", "smap"],
    "drought": ["drought", "sécheresse", "secheresse", "dry", "جفاف", "جاف", "risk", "risque", "خطر"],
    "vegetation": ["ndvi", "vegetation", "végétation", "plant", "crop health", "نبات", "غطاء", "خضر"],
    "temperature": ["temp", "heat", "chaleur", "chaud", "حرارة", "سخون"],
    "crops": ["crop", "culture", "cultiver", "planter", "rotation", "irrig", "water need", "grow", "plant",
              "زراع", "زرع", "أزرع", "ازرع", "نزرع", "نزرعو", "الموسم", "غراس", "محصول", "سقي", "تناوب", "قمح", "شعير"],
    "summary": ["summary", "summarise", "résumé", "resume", "situation", "status", "ملخص", "لخص", "لخّص", "وضعية"],
}


def is_arabic(text):
    return bool(re.search(r"[؀-ۿ]", text))


def find_topics(question):
    q = question.lower()
    found = [t for t, words in TOPICS.items() if any(w in q for w in words)]
    return found or ["summary"]


def pick(facts, *keywords):
    return [f for f in facts if any(k in f["name"].lower() for k in keywords)]


# Fact names shown in answers, translated (regex -> FR, AR)
_NAMES = [
    (r"Location", "Localisation", "الموقع"),
    (r"Rain, last (\d+) days", r"Pluie, \1 derniers jours", r"المطر، آخر \1 يوم"),
    (r"Root-zone wetness \(0-1\), recent mean", "Humidité de la zone racinaire (0-1), moyenne récente",
     "رطوبة منطقة الجذور (0-1)، المعدل الأخير"),
    (r"Max temperature, last (\d+) days", r"Température max, \1 derniers jours", r"أعلى حرارة، آخر \1 يوم"),
    (r"Mean temperature, recent", "Température moyenne récente", "متوسط الحرارة مؤخراً"),
    (r"Current alerts", "Alertes actuelles", "التنبيهات الحالية"),
    (r"Rain, last 12 months", "Pluie, 12 derniers mois", "المطر، آخر 12 شهراً"),
    (r"Most unusual recent months", "Mois récents les plus inhabituels", "أكثر الأشهر الأخيرة غرابة"),
    (r"Risk of unusually dry next (\d+) days", r"Risque de sécheresse, \1 prochains jours",
     r"خطر الجفاف في الأيام \1 القادمة"),
    (r"SMAP root-zone soil moisture", "SMAP humidité du sol (racines)", "SMAP رطوبة التربة (الجذور)"),
    (r"SMAP surface soil moisture", "SMAP humidité du sol (surface)", "SMAP رطوبة سطح التربة"),
    (r"MODIS NDVI latest", "MODIS NDVI (dernier)", "MODIS NDVI (آخر قيمة)"),
    (r"Landsat NDVI latest", "Landsat NDVI (dernier)", "Landsat NDVI (آخر قيمة)"),
    (r"ECOSTRESS surface temperature latest", "ECOSTRESS température de surface (dernière)",
     "ECOSTRESS حرارة السطح (آخر قيمة)"),
    (r"SRTM elevation", "SRTM altitude", "SRTM الارتفاع"),
    (r"Irrigation need per crop, normal year \(mm\)", "Besoin d'irrigation par culture, année normale (mm)",
     "حاجة كل زراعة للسقي، سنة عادية (ملم)"),
    (r"Best scenario for the chosen criteria", "Meilleur scénario selon vos critères", "أفضل سيناريو حسب معاييرك"),
    (r"Suggested crops for (.+) after (.+)", r"Cultures suggérées pour \1 après \2", r"الزراعات المقترحة لـ \1 بعد \2"),
    (r"Missing data", "Données manquantes", "بيانات ناقصة"),
]
_WORDS = {"fr": [("normal ", "normale "), ("rank ", "rang "), ("1 = driest year of the reference period",
                                                                 "1 = année la plus sèche"), ("none", "aucune")],
          "ar": [("normal ", "العادي "), ("rank ", "الترتيب "), ("1 = driest year of the reference period",
                                                                  "1 = أجف سنة"), ("none", "لا شيء"),
                 ("score ", "النقطة ")]}


def _name(text, lang):
    import re
    if lang not in ("fr", "ar"):
        return text
    for pat, fr_txt, ar_txt in _NAMES:
        if re.fullmatch(pat, text):
            return _value(re.sub(pat, fr_txt if lang == "fr" else ar_txt, text), lang)
    return text


def _value(text, lang):
    try:
        from src.i18n import tr
        text = "; ".join(tr(part.strip()) for part in text.split(";"))
    except Exception:
        pass
    for a, b in _WORDS.get(lang, []):
        text = text.replace(a, b)
    if lang in ("fr", "ar"):
        import re
        try:
            from src.i18n import CROP_NAMES, _LEVELS
        except Exception:
            return text
        i = 0 if lang == "fr" else 1
        words = {**{k: v[i] for k, v in CROP_NAMES.items()}, **{k: v[i] for k, v in _LEVELS.items() if k != "very"}}
        names = sorted(words, key=len, reverse=True)
        lower = {k.lower(): v for k, v in words.items()}
        text = re.sub(r"\b(" + "|".join(map(re.escape, names)) + r")\b", lambda m: lower[m.group(1).lower()],
                      text, flags=re.I)
    return text


def answer_offline(facts, question, lang="en"):
    topics = find_topics(question)
    selected = []
    for topic in topics:
        keys = {"rain": ("rain",), "soil": ("wetness", "moisture", "smap"),
                "drought": ("risk", "alert", "rank", "unusual"),
                "vegetation": ("ndvi", "evi"), "temperature": ("temp",),
                "crops": ("crop", "scenario", "irrigation", "suggest"),
                "summary": ("rain", "wetness", "risk", "alert", "ndvi", "temp")}[topic]
        selected += [f for f in pick(facts, *keys) if f not in selected]

    ar = is_arabic(question) or lang == "ar"
    fr = not ar and lang == "fr"
    if not selected:
        return ("لا توجد بيانات كافية للإجابة عن هذا السؤال. حمّل البيانات أولاً."
                if ar else "Je n'ai pas encore les données pour cette question. Chargez d'abord les données."
                if fr else "I don't have the data needed for this question yet. Load the data first.")
    intro = ("📋 ما تقوله بيانات NASA عن حقلك:" if ar else "📋 Ce que disent les données NASA sur votre parcelle :"
             if fr else "📋 What the NASA data says about your field:")
    out = "ar" if ar else "fr" if fr else "en"
    lines = [intro] + [f"- **{_name(f['name'], out)}**: {_value(f['value'], out)}  _({f['source']})_"
                       for f in selected[:10]]
    lines.append("" )
    lines.append("⚠️ مؤشرات جهوية (POWER ~50 كم، SMAP ~9 كم)، تساعد على القرار ولا تعوض زيارة الحقل."
                 if ar else "⚠️ Indicateurs régionaux (POWER ~50 km, SMAP ~9 km) : une aide à la décision, "
                            "pas un remplacement de la visite du champ." if fr else
                 "⚠️ Regional indicators (POWER ~50 km, SMAP ~9 km): they support decisions "
                 "but do not replace a field visit.")
    return "\n".join(lines)


def missing_data(sat_sources):
    expected = {"smap": "SMAP soil moisture", "gpm": "GPM precipitation", "modis": "MODIS NDVI",
                "ecostress": "ECOSTRESS surface temperature", "landsat": "Landsat", "srtm": "SRTM elevation"}
    return [label for key, label in expected.items() if key not in sat_sources]
