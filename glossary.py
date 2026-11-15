"""
glossary.py - Plain-language explanations of every technical word in TerraShift.
Each entry: name (simple), category, English explanation, Arabic explanation, unit.
Used for: hover help (ⓘ), friendly table column names, the sidebar lookup and the Glossary tab.
"""

GLOSSARY = {
    # ---------------- Weather (NASA POWER variable codes) ----------------
    "T2M": ("Mean air temperature", "Weather",
            "The average temperature of the air during the day, measured 2 metres above the ground.",
            "متوسط حرارة الهواء خلال اليوم، على علو مترين من الأرض.", "°C"),
    "T2M_MAX": ("Maximum air temperature", "Weather",
                "The hottest temperature of the day, 2 metres above the ground. Above about 35–38 °C "
                "most crops suffer (heat stress).",
                "أعلى حرارة في النهار. فوق 35 إلى 38 درجة كيتعذب الزرع.", "°C"),
    "T2M_MIN": ("Minimum air temperature", "Weather",
                "The coldest temperature of the day (usually at night). At 0 °C or below there is frost.",
                "أقل حرارة في النهار (غالباً فالليل). تحت 0 درجة كاين الجريحة (الصقيع).", "°C"),
    "PRECTOTCORR": ("Rainfall", "Weather",
                    "How much rain fell that day. 1 mm = 1 litre of water on each square metre "
                    "= 10 m³ on one hectare.",
                    "شحال طاح ديال الشتا. 1 ملم = لتر فكل متر مربع = 10 طن ديال الما فالهكتار.", "mm/day"),
    "RH2M": ("Air humidity", "Weather",
             "How much water vapour is in the air, in percent. Low humidity + heat = plants lose water fast. "
             "Very high humidity can favour fungal diseases.",
             "شحال فيه الرطوبة فالهوا. هوا ناشف وسخون = الزرع كيعطش بالزربة. رطوبة بزاف كتجيب الأمراض (الفطريات).", "%"),
    "GWETTOP": ("Surface soil wetness", "Soil & water",
                "How wet the top few centimetres of soil are, from 0 (completely dry) to 1 (full of water).",
                "شحال مبلولة الأرض فالفوق (أول سنتيمترات). من 0 (ناشفة) حتى 1 (عامرة بالما).", "0 – 1"),
    "GWETROOT": ("Root-zone soil wetness", "Soil & water",
                 "How wet the soil is where the roots live (about the first metre), from 0 (dry) to 1 (saturated). "
                 "This is the water your crop can actually drink.",
                 "شحال فيها الما الأرض عند العروق (تقريباً أول متر). هادا هو الما اللي كيشربو الزرع.", "0 – 1"),
    # ---------------- Soil & water ----------------
    "Soil moisture (SMAP)": ("Soil moisture measured by satellite", "Soil & water",
                             "Volume of water in the soil measured by the SMAP satellite. 0.30 m³/m³ means "
                             "30 % of the soil volume is water.",
                             "كمية الما فالتربة كيقيسها الستالايت SMAP. 0.30 يعني 30% من التربة ما.", "m³/m³"),
    "Root zone": ("Root zone", "Soil & water",
                  "The layer of soil where the roots grow, roughly the first metre.",
                  "الطبقة ديال الأرض فين كيعيشو العروق، تقريباً أول متر.", ""),
    "Drought threshold": ("Drought threshold", "Soil & water",
                          "A limit under which the soil is considered too dry for crops (here 0.3 on the 0–1 scale).",
                          "حد إلا نزلات تحتو الرطوبة، كنعتبرو الأرض ناشفة بزاف للزرع.", ""),
    "ET0": ("Evaporation demand (ET₀)", "Soil & water",
            "How much water the sun, heat and wind 'pull' from a green field each day. "
            "High in summer, low in winter.",
            "شحال ديال الما كتجبد الشمس والسخانة والريح من الأرض كل نهار. كثير فالصيف، قليل فالشتا.", "mm/day"),
    "ETc": ("Crop water use", "Soil & water",
            "Water the crop really uses = ET₀ × the crop coefficient (Kc).",
            "الما اللي كيستهلك الزرع بالصح = ET₀ × معامل الزرعة (Kc).", "mm"),
    "Kc": ("Crop coefficient (Kc)", "Soil & water",
           "How thirsty a crop is compared with grass. Small plants ≈ 0.3–0.7, full green crop ≈ 1.1–1.2.",
           "شحال الزرعة عطشانة مقارنة مع الربيع. الزرع صغير ≈ 0.3، الزرع كامل خضر ≈ 1.15.", ""),
    "Effective rain": ("Useful rain", "Soil & water",
                       "The part of the rain that stays in the soil for the crop (here 80 %). "
                       "The rest runs off or evaporates.",
                       "الجزء ديال الشتا اللي كيبقى فالأرض للزرع (هنا 80%). الباقي كيمشي مع الما ولا كيتبخر.", "mm"),
    "Irrigation need": ("Irrigation needed", "Soil & water",
                        "Water you must add because rain is not enough = crop water use − useful rain.",
                        "الما اللي خاصك تزيدو بالسقي حيث الشتا ماكافياش.", "mm"),
    # ---------------- Vegetation ----------------
    "NDVI": ("How green your crop is (NDVI)", "Vegetation",
             "A number from satellites that measures how green and healthy plants are. "
             "Below 0.2 = bare soil or harvested; 0.2–0.5 = sparse or tired crop; above 0.5 = dense healthy crop.",
             "رقم كيقيس شحال الزرع خضر وصحيح. تحت 0.2 = أرض خاوية؛ 0.2 حتى 0.5 = زرع قليل ولا عيان؛ فوق 0.5 = زرع قوي.", "0 – 1"),
    "EVI": ("Vegetation index (EVI)", "Vegetation",
            "Like NDVI but works better for very dense vegetation.",
            "بحال NDVI ولكن أحسن فالزرع الكثيف بزاف.", "0 – 1"),
    "LST": ("Ground surface temperature", "Vegetation",
            "Temperature of the ground or leaves themselves (not the air). A thirsty crop gets hotter "
            "than a well-watered one.",
            "حرارة الأرض ولا الورق براسهم (ماشي الهوا). الزرع العطشان كيسخن كثر من الزرع اللي شارب.", "°C"),
    # ---------------- Satellites & data sources ----------------
    "NASA POWER": ("NASA POWER", "Satellites & data",
                   "A free NASA service giving daily weather for any place since 1981 (temperature, rain, humidity, "
                   "soil wetness). Each value covers about 50 km.",
                   "خدمة مجانية ديال NASA كتعطي الطقس كل نهار من 1981. كل رقم كيغطي تقريباً 50 كلم.", ""),
    "SMAP": ("SMAP satellite", "Satellites & data",
             "NASA satellite that measures soil moisture with microwaves, about every 3 hours, 9 km pixels.",
             "ستالايت ديال NASA كيقيس الرطوبة فالتربة. كل نقطة كتغطي 9 كلم.", ""),
    "GPM": ("GPM (rain from space)", "Satellites & data",
            "Several satellites combined to measure rain every 30 minutes, 10 km pixels.",
            "بزاف ديال الستالايتات كيقيسو الشتا كل نص ساعة.", ""),
    "MODIS": ("MODIS satellite", "Satellites & data",
              "NASA instrument that photographs the whole Earth every day; we use its NDVI every 16 days, 250 m pixels.",
              "ستالايت كيصور الأرض كاملة كل نهار. كنستعملو منو NDVI كل 16 يوم.", ""),
    "Landsat": ("Landsat satellite", "Satellites & data",
                "Satellite with sharp pictures (30 m pixels) about every 8 days; used for NDVI and ground temperature "
                "inside your field.",
                "ستالايت عندو صور دقيقة (30 متر) كل 8 أيام تقريباً. كيشوف حتى داخل الأرض ديالك.", ""),
    "ECOSTRESS": ("ECOSTRESS", "Satellites & data",
                  "Instrument on the space station that measures ground temperature, day or night (70 m).",
                  "جهاز فمحطة الفضاء كيقيس حرارة الأرض بالنهار ولا بالليل.", ""),
    "SRTM": ("SRTM (altitude)", "Satellites & data",
             "Map of the height of the ground made by radar from a space shuttle in 2000 (30 m).",
             "خريطة ديال العلو ديال الأرض، تصورات من الفضاء عام 2000.", "m"),
    "Slope": ("Slope", "Soil & water",
              "How steep the ground is: metres of height gained per 100 m. Above ~5 % heavy rain runs off and carries soil away.",
              "شحال الأرض طالعة ولا هابطة. إلا كانت كثر من 5% الشتا كتجري وكتدي معاها التربة.", "%"),
    "GRACE-FO": ("GRACE-FO", "Satellites & data",
                 "Satellites that weigh water stored underground over very large regions (hundreds of km).",
                 "ستالايتات كيوزنو الما اللي تحت الأرض فمناطق كبيرة بزاف.", ""),
    "Resolution": ("Resolution (pixel size)", "Satellites & data",
                   "The size of the area one satellite value covers. 50 km means one number for a whole region; "
                   "30 m means one number for a small part of your field.",
                   "شحال كبيرة البلاصة اللي كيغطيها رقم واحد. 50 كلم = منطقة كاملة؛ 30 متر = جزء صغير من أرضك.", ""),
    # ---------------- Statistics & AI ----------------
    "z-score": ("How unusual (z-score)", "Statistics & AI",
                "Compares a value with the usual one for the same month. 0 = normal, ±1 = unusual, ±2 = very unusual.",
                "كيقارن الرقم مع العادة ديال نفس الشهر. 0 = عادي، ±1 = ماشي عادي، ±2 = ماشي عادي بزاف.", ""),
    "Anomaly": ("Difference from usual", "Statistics & AI",
                "How much a value is above or below what is normal for that time of year.",
                "شحال الرقم فوق ولا تحت العادة ديال هاد الوقت من العام.", ""),
    "Percentile": ("Percentile", "Statistics & AI",
                   "Position among past values. '20 % driest' means drier than 80 % of past cases.",
                   "البلاصة بين القيم اللي فاتت. '20% الأنشف' يعني أنشف من 80% ديال المرات.", ""),
    "Baseline": ("Simple rule (baseline)", "Statistics & AI",
                 "A very simple prediction used to check if the AI is really useful.",
                 "توقع بسيط بزاف كنقارنو بيه باش نعرفو واش الذكاء الاصطناعي نافع بالصح.", ""),
    "Random Forest": ("Random Forest (AI model)", "Statistics & AI",
                      "An AI model made of hundreds of small decision trees that vote together.",
                      "نموذج ذكاء اصطناعي فيه مئات ديال 'الشجرات' الصغار كيصوتو مع بعض.", ""),
    "Decision Tree": ("Decision Tree (AI model)", "Statistics & AI",
                      "An AI model that asks yes/no questions one after another (e.g. 'rain < 20 mm?').",
                      "نموذج كيطرح أسئلة واحد من بعد واحد (مثلاً: واش الشتا أقل من 20 ملم؟).", ""),
    "Accuracy": ("Accuracy", "Statistics & AI",
                 "Share of all predictions that were right.",
                 "شحال من مرة كان التوقع صحيح من بين جميع المرات.", "%"),
    "Precision": ("Precision", "Statistics & AI",
                  "When the model says 'drought', how often it is really a drought. Low = many false alarms.",
                  "ملي النموذج كيقول 'جفاف'، شحال من مرة كان صحيح. ضعيف = إنذارات غالطة بزاف.", "%"),
    "Recall": ("Recall", "Statistics & AI",
               "Of all real droughts, how many the model caught. Low = it misses droughts.",
               "من بين جميع حالات الجفاف الحقيقية، شحال لقا النموذج. ضعيف = كيفوتو.", "%"),
    "F1": ("F1 score", "Statistics & AI",
           "One number that balances Precision and Recall (1 = perfect).",
           "رقم واحد كيجمع بين Precision و Recall (1 = كامل).", ""),
    "Confusion matrix": ("Confusion matrix", "Statistics & AI",
                         "A table that counts right and wrong predictions: real drought vs predicted drought.",
                         "جدول كيحسب التوقعات الصحيحة والغالطة.", ""),
    "Probability": ("Probability", "Statistics & AI",
                    "How likely something is, from 0 % (impossible) to 100 % (certain). 70 % = likely, not sure.",
                    "شحال الحاجة ممكنة، من 0% حتى 100%. 70% = غالباً، ماشي أكيد.", "%"),
    # ---------------- Farming ----------------
    "Crop rotation": ("Crop rotation", "Farming",
                      "Changing the crop grown on a field from one season to the next, to keep the soil healthy "
                      "and break disease cycles.",
                      "تبديل الزرعة فالأرض من عام لعام، باش تبقى الأرض صحيحة وتنقص الأمراض.", ""),
    "Legume": ("Legume", "Farming",
               "Crops like faba bean, chickpea, lentil, pea, alfalfa: they take nitrogen from the air and "
               "leave it in the soil (free fertiliser).",
               "القطاني (فول، حمص، عدس، جلبانة، فصة): كياخدو الأزوت من الهوا وكيخليوه فالأرض (سماد فابور).", ""),
    "Nitrogen": ("Nitrogen", "Farming",
                 "Main food of plants (the 'N' in fertiliser). Legumes add it to the soil.",
                 "الأزوت: الماكلة الأساسية ديال الزرع. القطاني كيزيدوه للأرض.", ""),
    "Fallow": ("Fallow", "Farming",
               "Leaving the field without a crop for one season so the soil rests and stores water.",
               "البور: كتخلي الأرض بلا زريعة عام باش ترتاح وتجمع الما.", ""),
    "Monoculture": ("Monoculture", "Farming",
                    "Growing the same crop every year on the same field. Increases diseases, pests and weeds.",
                    "نفس الزرعة كل عام فنفس الأرض. كتكثر الأمراض والحشرات والربيع.", ""),
    "Hectare": ("Hectare (ha)", "Farming",
                "An area of 100 m × 100 m = 10 000 m².", "الهكتار = 100 متر × 100 متر.", "ha"),
}

# Map raw table column names to glossary keys
COLUMN_KEYS = {"T2M": "T2M", "T2M_MAX": "T2M_MAX", "T2M_MIN": "T2M_MIN", "PRECTOTCORR": "PRECTOTCORR",
               "RH2M": "RH2M", "GWETTOP": "GWETTOP", "GWETROOT": "GWETROOT"}


def name(term):
    return GLOSSARY[term][0] if term in GLOSSARY else term


def explain(term, arabic=True):
    """Short help text for a ⓘ tooltip."""
    if term not in GLOSSARY:
        return None
    n, _, en, ar, unit = GLOSSARY[term]
    try:
        from src.i18n import lang
        current = lang()
    except Exception:
        current = "en"
    if current == "ar":
        return ar + (f" ({unit})" if unit else "")
    text = f"{en}" + (f" (unit: {unit})" if unit else "")
    return text + (f"\n\n{ar}" if arabic and current == "en" else "")


def friendly_columns(df):
    """Rename codes like T2M_MAX into words, and build hover help for st.dataframe."""
    import streamlit as st
    renamed, config = {}, {}
    for col in df.columns:
        key = COLUMN_KEYS.get(col)
        if key:
            unit = GLOSSARY[key][4]
            label = f"{GLOSSARY[key][0]} ({unit})" if unit else GLOSSARY[key][0]
            renamed[col] = label
            config[label] = st.column_config.NumberColumn(label, help=explain(key), format="%.2f")
    return df.rename(columns=renamed), config


def categories():
    order = ["Weather", "Soil & water", "Vegetation", "Satellites & data", "Statistics & AI", "Farming"]
    return {c: [k for k, v in GLOSSARY.items() if v[1] == c] for c in order}
