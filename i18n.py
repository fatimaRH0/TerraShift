"""
i18n.py - Interface language: English, Français, العربية.

t("key")      -> fixed interface text in the chosen language
crop("Wheat") -> crop name in the chosen language
tr(sentence)  -> translates the sentences TerraShift builds with numbers
                 (verdict, alerts, crop advice) using patterns; unknown text stays as is.
The chosen language is st.session_state["lang"] ("en", "fr" or "ar").
"""

import re

import streamlit as st

LANGS = {"en": "English", "fr": "Français", "ar": "العربية"}
_I = {"en": 0, "fr": 1, "ar": 2}


def lang():
    return st.session_state.get("lang") or "en"


def is_rtl():
    return lang() == "ar"


# ---------------------------------------------------------
# Fixed interface text: key -> (English, Français, العربية)
# ---------------------------------------------------------
UI = {
    # tabs
    "tab_overview": ("Overview", "Aperçu", "نظرة عامة"),
    "tab_map": ("Map", "Carte", "الخريطة"),
    "tab_history": ("History", "Historique", "التاريخ"),
    "tab_drought": ("Drought risk", "Risque de sécheresse", "خطر الجفاف"),
    "tab_crops": ("Crops", "Cultures", "الزراعات"),
    "tab_3d": ("3D farm", "Ferme 3D", "المزرعة 3D"),
    "tab_assistant": ("Assistant", "Assistant", "المساعد"),
    "tab_satellites": ("Satellites", "Satellites", "الأقمار الصناعية"),
    "tab_glossary": ("Glossary", "Glossaire", "قاموس الكلمات"),
    # sidebar
    "your_field": ("Your field", "Votre parcelle", "حقلك"),
    "latitude": ("Latitude", "Latitude", "خط العرض"),
    "longitude": ("Longitude", "Longitude", "خط الطول"),
    "find_place": ("🔎 Find your village or town", "🔎 Trouver votre village ou ville", "🔎 ابحث عن قريتك أو مدينتك"),
    "find_placeholder": ("e.g. Sidi Kaouki, Berrechid, Ouled Teima", "ex. Sidi Kaouki, Berrechid, Ouled Teima",
                         "مثلاً: سيدي كاوكي، برشيد، أولاد تايمة"),
    "choose_place": ("Choose the right place", "Choisissez le bon endroit", "اختر المكان الصحيح"),
    "go_place": ("✅ Go to this place", "✅ Aller à cet endroit", "✅ اذهب إلى هذا المكان"),
    "no_place": ("No place found with this name. Try another spelling or a bigger town nearby.",
                 "Aucun lieu trouvé. Essayez une autre orthographe ou une ville proche plus grande.",
                 "لم يتم العثور على هذا المكان. جرّب كتابة أخرى أو مدينة أكبر قريبة."),
    "use_location": ("📡 Use my current location", "📡 Utiliser ma position actuelle", "📡 استعمل موقعي الحالي"),
    "field_name": ("Field name", "Nom de la parcelle", "اسم الحقل"),
    "periods": ("⚙️ Periods (expert)", "⚙️ Périodes (expert)", "⚙️ الفترات (للخبراء)"),
    "history_days": ("History (days)", "Historique (jours)", "التاريخ (أيام)"),
    "summary_days": ("Summary period (days)", "Période du résumé (jours)", "فترة الملخص (أيام)"),
    "load_data": ("Load data", "Charger les données", "حمّل البيانات"),
    "alert_thresholds": ("⚙️ Alert thresholds", "⚙️ Seuils d'alerte", "⚙️ حدود التنبيه"),
    "thr_dry": ("Dry soil below (root-zone wetness, 0–1)", "Sol sec en dessous de (humidité racinaire, 0–1)",
                "تربة جافة تحت (رطوبة منطقة الجذور، 0–1)"),
    "thr_rain": ("Low rain below (% of the usual rain)", "Pluie faible en dessous de (% de la pluie habituelle)",
                 "مطر قليل تحت (% من المطر المعتاد)"),
    "thr_heat": ("Heat stress above (max temperature, °C)", "Stress thermique au-dessus de (température max, °C)",
                 "إجهاد حراري فوق (أعلى حرارة، °م)"),
    "language": ("Language", "Langue", "اللغة"),
    # cover
    "elevation": ("elevation", "altitude", "الارتفاع"),
    "weather_from": ("weather from", "météo du", "الطقس من"),
    "to": ("to", "au", "إلى"),
    "data_loaded": ("data loaded", "données chargées", "البيانات محمّلة"),
    "not_downloaded": ("not downloaded yet", "pas encore téléchargé", "لم تُحمَّل بعد"),
    "report_title": ("Field report · {name}", "Rapport de la parcelle · {name}", "تقرير الحقل · {name}"),
    "report_sub": ("Verdict, key numbers, suggested crop, alerts and NASA sources · 1 page · print or save as PDF",
                   "Verdict, chiffres clés, culture suggérée, alertes et sources NASA · 1 page · imprimable en PDF",
                   "النتيجة، الأرقام المهمة، الزراعة المقترحة، التنبيهات ومصادر NASA · صفحة واحدة · قابل للطباعة PDF"),
    "dl_none": ("No {src} data for this place yet.", "Pas encore de données {src} pour ce lieu.",
                "لا توجد بعد بيانات {src} لهذا المكان."),
    "dl_why": ("TerraShift can download the NASA satellite data for this exact place. Landsat comes in a few "
               "minutes; SMAP, MODIS, ECOSTRESS and SRTM (AppEEARS) can take up to an hour. You can keep using "
               "the app meanwhile.",
               "TerraShift peut télécharger les données satellite NASA pour ce lieu précis. Landsat arrive en "
               "quelques minutes ; SMAP, MODIS, ECOSTRESS et SRTM (AppEEARS) peuvent prendre jusqu'à une heure. "
               "Vous pouvez continuer à utiliser l'application.",
               "يمكن لـ TerraShift تحميل بيانات الأقمار الصناعية من NASA لهذا المكان بالضبط. Landsat يصل في دقائق، "
               "أما SMAP وMODIS وECOSTRESS وSRTM (AppEEARS) فقد تأخذ حتى ساعة. يمكنك مواصلة استعمال التطبيق."),
    "dl_start": ("Download satellite data for this place", "Télécharger les données satellite de ce lieu",
                 "حمّل بيانات الأقمار الصناعية لهذا المكان"),
    "dl_account": ("Uses your free **NASA Earthdata** account ([create one](https://urs.earthdata.nasa.gov/users/new), "
                   "then log in once on [AppEEARS](https://appeears.earthdatacloud.nasa.gov) to accept the terms). "
                   "The password is only passed to this download, never saved.",
                   "Utilise votre compte gratuit **NASA Earthdata** ([créer un compte](https://urs.earthdata.nasa.gov/users/new), "
                   "puis connectez-vous une fois sur [AppEEARS](https://appeears.earthdatacloud.nasa.gov)). "
                   "Le mot de passe sert seulement à ce téléchargement, il n'est pas enregistré.",
                   "يستعمل حسابك المجاني في **NASA Earthdata** ([أنشئ حساباً](https://urs.earthdata.nasa.gov/users/new)، "
                   "ثم ادخل مرة واحدة إلى [AppEEARS](https://appeears.earthdatacloud.nasa.gov) لقبول الشروط). "
                   "كلمة السر تُستعمل لهذا التحميل فقط ولا تُحفظ."),
    "demo_field": ("Demo field (Meknès)", "Champ de démo (Meknès)", "حقل العرض (مكناس)"),
    "demo_help": ("A field near Meknès with every NASA source already downloaded: SMAP, ECOSTRESS, MODIS, Landsat, SRTM.",
                  "Un champ près de Meknès avec toutes les sources NASA déjà téléchargées : SMAP, ECOSTRESS, MODIS, Landsat, SRTM.",
                  "حقل قرب مكناس فيه كل مصادر NASA محمّلة مسبقاً: SMAP وECOSTRESS وMODIS وLandsat وSRTM."),
    "ed_title": ("NASA Earthdata account (SMAP, ECOSTRESS, GPM)", "Compte NASA Earthdata (SMAP, ECOSTRESS, GPM)",
                 "حساب NASA Earthdata (SMAP، ECOSTRESS، GPM)"),
    "ed_why": ("SMAP (soil moisture), ECOSTRESS (heat) and GPM (rain) need a free NASA Earthdata account. "
               "Enter it **once**: it is saved only on this computer (file `.env`) and then every place gets them "
               "automatically. [Create an account](https://urs.earthdata.nasa.gov/users/new), then log in once on "
               "[AppEEARS](https://appeears.earthdatacloud.nasa.gov).",
               "SMAP (humidité du sol), ECOSTRESS (chaleur) et GPM (pluie) demandent un compte gratuit NASA Earthdata. "
               "Saisissez-le **une seule fois** : il est gardé uniquement sur cet ordinateur (fichier `.env`), puis chaque "
               "lieu les reçoit automatiquement. [Créer un compte](https://urs.earthdata.nasa.gov/users/new), puis "
               "connectez-vous une fois sur [AppEEARS](https://appeears.earthdatacloud.nasa.gov).",
               "SMAP (رطوبة التربة) وECOSTRESS (الحرارة) وGPM (المطر) تحتاج حساباً مجانياً في NASA Earthdata. "
               "أدخله **مرة واحدة**: يُحفظ فقط على هذا الحاسوب (ملف `.env`) ثم يحصل كل مكان عليها تلقائياً. "
               "[أنشئ حساباً](https://urs.earthdata.nasa.gov/users/new) ثم ادخل مرة إلى [AppEEARS](https://appeears.earthdatacloud.nasa.gov)."),
    "ed_save": ("Save and download", "Enregistrer et télécharger", "احفظ وحمّل"),
    "ed_connected": ("Connected as **{user}**. SMAP, ECOSTRESS and GPM are downloaded automatically for each place.",
                     "Connecté en tant que **{user}**. SMAP, ECOSTRESS et GPM se téléchargent automatiquement pour chaque lieu.",
                     "متصل باسم **{user}**. SMAP وECOSTRESS وGPM تُحمَّل تلقائياً لكل مكان."),
    "ed_connected_all": ("SMAP, ECOSTRESS and GPM are on: they are downloaded automatically for every place, for every user.",
                         "SMAP, ECOSTRESS et GPM sont activés : ils se téléchargent automatiquement pour chaque lieu et chaque utilisateur.",
                         "SMAP وECOSTRESS وGPM مفعّلة: تُحمَّل تلقائياً لكل مكان ولكل مستخدم."),
    "ed_running": ("Downloading SMAP, ECOSTRESS and GPM (AppEEARS can take up to an hour)…",
                   "Téléchargement de SMAP, ECOSTRESS et GPM (AppEEARS peut prendre jusqu'à une heure)…",
                   "جارٍ تحميل SMAP وECOSTRESS وGPM (AppEEARS قد يأخذ حتى ساعة)…"),
    "ed_forget": ("Remove the account from this computer", "Retirer le compte de cet ordinateur", "احذف الحساب من هذا الحاسوب"),
    "dl_user": ("Earthdata username", "Identifiant Earthdata", "اسم المستخدم في Earthdata"),
    "dl_pass": ("Earthdata password", "Mot de passe Earthdata", "كلمة سر Earthdata"),
    "dl_go": ("Start download", "Lancer le téléchargement", "ابدأ التحميل"),
    "dl_need": ("Enter your username and password.", "Entrez l'identifiant et le mot de passe.",
                "أدخل اسم المستخدم وكلمة السر."),
    "dl_running": ("Getting the NASA satellite data for this place automatically (a few minutes)…",
                   "Récupération automatique des données satellite NASA de ce lieu (quelques minutes)…",
                   "جارٍ جلب بيانات الأقمار الصناعية من NASA لهذا المكان تلقائياً (بضع دقائق)…"),
    "dl_account_note": ("It needs a free NASA Earthdata account (optional): soil moisture and rain already come from NASA POWER.",
                        "Il faut un compte gratuit NASA Earthdata (optionnel) : l'humidité du sol et la pluie viennent déjà de NASA POWER.",
                        "يحتاج حساباً مجانياً في NASA Earthdata (اختياري): رطوبة التربة والمطر يأتيان أصلاً من NASA POWER."),
    "dl_not_found": ("No usable image was found for this place and period.",
                     "Aucune image exploitable trouvée pour ce lieu et cette période.",
                     "لم توجد صورة صالحة لهذا المكان وهذه الفترة."),
    "dl_details": ("Download details", "Détails du téléchargement", "تفاصيل التحميل"),
    "dl_again": ("Try again", "Réessayer", "عاود المحاولة"),
    "dl_refresh": ("Check progress", "Voir l'avancement", "شوف التقدم"),
    "dl_failed": ("The last download stopped with an error: see the details", "Le dernier téléchargement a échoué : voir le détail",
                  "توقف آخر تحميل بخطأ: شوف التفاصيل"),
    "dl_done_none": ("The last download finished but returned no {src} data: see the details",
                     "Le dernier téléchargement est terminé mais sans données {src} : voir le détail",
                     "انتهى آخر تحميل لكن بدون بيانات {src}: شوف التفاصيل"),
    "download": ("Download", "Télécharger", "تحميل"),
    "download_report": ("📄 Download the field report (open it, print it or save it as PDF)",
                        "📄 Télécharger le rapport (ouvrir, imprimer ou enregistrer en PDF)",
                        "📄 حمّل تقرير الحقل (افتحه، اطبعه أو احفظه PDF)"),
    # overview
    "water": ("Water", "Eau", "الماء"),
    "heat": ("Heat", "Chaleur", "الحرارة"),
    "vegetation": ("Vegetation", "Végétation", "الغطاء النباتي"),
    "alerts": ("Alerts", "Alertes", "التنبيهات"),
    "no_alerts": ("No alerts for this period.", "Aucune alerte pour cette période.", "لا توجد تنبيهات في هذه الفترة."),
    "rain_last": ("Rain, last {d} days", "Pluie, {d} derniers jours", "المطر، آخر {d} يوم"),
    "vs_usual": ("{x} mm vs usual {u} mm", "{x} mm par rapport aux {u} mm habituels", "{x} ملم مقارنة بالمعتاد {u} ملم"),
    "root_wet": ("Root-zone wetness", "Humidité de la zone racinaire", "رطوبة منطقة الجذور"),
    "above_dry": ("{x} above the dry limit {l}", "{x} au-dessus de la limite sèche {l}", "{x} فوق حد الجفاف {l}"),
    "below_dry": ("{x} below the dry limit {l}", "{x} sous la limite sèche {l}", "{x} تحت حد الجفاف {l}"),
    "smap_root": ("SMAP root-zone moisture", "Humidité racinaire SMAP", "رطوبة الجذور (SMAP)"),
    "max_air": ("Max air temperature", "Température max de l'air", "أعلى حرارة للهواء"),
    "mean_air": ("Mean air temperature", "Température moyenne de l'air", "متوسط حرارة الهواء"),
    "above_heat": ("above heat limit {l} °C", "au-dessus de la limite {l} °C", "فوق حد الحرارة {l} °م"),
    "below_heat": ("below heat limit {l} °C", "sous la limite {l} °C", "تحت حد الحرارة {l} °م"),
    "last_days": ("last {d} days", "{d} derniers jours", "آخر {d} يوم"),
    "surface_temp": ("Surface temperature", "Température de surface", "حرارة سطح الأرض"),
    "ndvi_name": ("NDVI (greenness)", "NDVI (verdure)", "NDVI (الخضرة)"),
    "ndvi_bare": ("Bare soil", "Sol nu", "تربة عارية"),
    "ndvi_mod": ("Moderate", "Modérée", "متوسطة"),
    "ndvi_dense": ("Dense, healthy", "Dense, en bonne santé", "كثيفة وسليمة"),
    "no_veg": ("Vegetation data for this place is being fetched from NASA (a few minutes): refresh the page soon.",
               "Les données de végétation de ce lieu arrivent de la NASA (quelques minutes) : rafraîchissez bientôt.",
               "بيانات الغطاء النباتي لهذا المكان في طريقها من NASA (بضع دقائق): حدّث الصفحة بعد قليل."),
    # crops tab
    "build_title": ("🔀 Build your rotation", "🔀 Construisez votre rotation", "🔀 خطط لدورتك الزراعية"),
    "build_sub": ("Tell us what this field grew the last 3 seasons. TerraShift proposes the best crop for this season "
                  "({s}); you can pick another one to compare.",
                  "Indiquez ce que la parcelle a porté les 3 dernières saisons. TerraShift propose la meilleure culture "
                  "pour cette saison ({s}) ; vous pouvez en choisir une autre pour comparer.",
                  "أخبرنا بما زرعته في هذا الحقل خلال المواسم الثلاثة الأخيرة. يقترح TerraShift أفضل زراعة لهذا الموسم "
                  "({s})، ويمكنك اختيار زراعة أخرى للمقارنة."),
    "you_grew": ("YOU GREW · {s}", "VOUS AVEZ CULTIVÉ · {s}", "زرعتَ · {s}"),
    "this_season": ("THIS SEASON · {s}", "CETTE SAISON · {s}", "هذا الموسم · {s}"),
    "suggested": ("★ Suggested · {p}% match", "★ Proposée · {p} % d'adéquation", "★ مقترحة · توافق {p}%"),
    "changed": ("changed by you", "modifiée par vous", "اختيارك أنت"),
    "back_suggestion": ("↺ Back to the suggestion", "↺ Revenir à la proposition", "↺ الرجوع إلى الاقتراح"),
    "other_choices": ("Other good choices:", "Autres bons choix :", "اختيارات جيدة أخرى:"),
    "water_avail": ("Irrigation water you can use (mm per year)", "Eau d'irrigation disponible (mm par an)",
                    "ماء السقي المتوفر (ملم في السنة)"),
    "water_help": ("0 = rainfed only. 1 mm on 1 hectare = 10 m³ of water.",
                   "0 = pluvial uniquement. 1 mm sur 1 hectare = 10 m³ d'eau.",
                   "0 = بدون سقي (بعلي). 1 ملم على هكتار = 10 م³ من الماء."),
    "sow_around": ("Sow around", "Semer vers le", "ازرع حوالي"),
    "irr_normal": ("Irrigation, normal year", "Irrigation, année normale", "السقي في سنة عادية"),
    "irr_dry": ("Irrigation, dry year", "Irrigation, année sèche", "السقي في سنة جافة"),
    "rain_covers": ("rain covers {p} %", "la pluie couvre {p} %", "المطر يغطي {p}%"),
    "one_in_five": ("1 year in 5", "1 année sur 5", "سنة من كل 5"),
    "if_again": ("If you grow {c} again", "Si vous refaites {c}", "إذا زرعت {c} مرة أخرى"),
    "more_mm": ("{x} mm more irrigation", "{x} mm d'irrigation en plus", "{x} ملم سقي إضافي"),
    "less_mm": ("{x} mm less irrigation", "{x} mm d'irrigation en moins", "{x} ملم سقي أقل"),
    "verdict_best": ("✓ {c} is the best choice for this field this season.",
                     "✓ {c} est le meilleur choix pour cette parcelle cette saison.",
                     "✓ {c} هي أفضل زراعة لهذا الحقل هذا الموسم."),
    "verdict_other": ("{b} fits this field better ({pb}% vs {pc}% for {c}).",
                      "{b} convient mieux à cette parcelle ({pb} % contre {pc} % pour {c}).",
                      "{b} تناسب هذا الحقل أكثر ({pb}% مقابل {pc}% لـ {c})."),
    "all_ranked": ("All crops ranked for this field", "Toutes les cultures classées pour cette parcelle",
                   "كل الزراعات مرتبة لهذا الحقل"),
    "col_crop": ("Crop", "Culture", "الزراعة"),
    "col_match": ("Match (%)", "Adéquation (%)", "التوافق (%)"),
    "col_rot": ("Rotation fit (%)", "Rotation (%)", "ملاءمة الدورة (%)"),
    "col_water": ("Water fit (%)", "Eau (%)", "ملاءمة الماء (%)"),
    "col_sow": ("Sow around", "Semis vers", "الزرع حوالي"),
    "water_needs": ("Water needs per crop", "Besoins en eau par culture", "حاجة كل زراعة من الماء"),
    "needs": ("needs", "besoin", "تحتاج"),
    "irrigate": ("irrigate", "irriguer", "اسقِ"),
    "in_dry": ("in a dry year", "en année sèche", "في سنة جافة"),
    "rain_word": ("rain", "pluie", "مطر"),
    "legend_rain": ("Covered by rain (normal year)", "Couvert par la pluie (année normale)", "يغطيه المطر (سنة عادية)"),
    "legend_irr": ("You must irrigate", "À irriguer", "يجب سقيه"),
    "water_table": ("Table of water needs", "Tableau des besoins en eau", "جدول الحاجة إلى الماء"),
    "no_history": ("❌ Could not load the history: {e}", "❌ Impossible de charger l'historique : {e}",
                   "❌ تعذّر تحميل البيانات التاريخية: {e}"),
    # assistant
    "as_title": ("Field assistant", "Assistant de la parcelle", "مساعد الحقل"),
    "as_ready": ("● Ready", "● Prêt", "● جاهز"),
    "as_from": ("answers only from your NASA data ({n} facts) · free, works offline",
                "répond uniquement avec vos données NASA ({n} faits) · gratuit, sans internet",
                "يجيب فقط من بيانات NASA الخاصة بحقلك ({n} معلومة) · مجاني ويعمل دون إنترنت"),
    "as_clear": ("Clear", "Effacer", "مسح"),
    "as_empty": ("Ask anything about your field: rain, soil, drought, what to grow. Every answer gives the NASA source.",
                 "Posez une question sur votre parcelle : pluie, sol, sécheresse, quoi cultiver. Chaque réponse cite la source NASA.",
                 "اسأل أي سؤال عن حقلك: المطر، التربة، الجفاف، ماذا تزرع. كل جواب يذكر مصدر NASA."),
    "as_placeholder": ("Ask about your field in English, Français or العربية",
                       "Posez votre question en English, Français ou العربية",
                       "اكتب سؤالك بالعربية أو Français أو English"),
    "as_know": ("What I know about your field", "Ce que je sais de votre parcelle", "ما أعرفه عن حقلك"),
    "as_all": ("See all {n} facts", "Voir les {n} faits", "عرض كل المعلومات ({n})"),
    "as_try": ("Try asking", "Essayez de demander", "جرّب أن تسأل"),
    "as_usual_rain": ("Usual rain", "Pluie habituelle", "المطر المعتاد"),
    "as_drought": ("Drought risk, 14 days", "Risque de sécheresse, 14 jours", "خطر الجفاف، 14 يوماً"),
    "as_suggested": ("Suggested crop", "Culture proposée", "الزراعة المقترحة"),
    "q_summary": ("📋 Summarise my field", "📋 Résume la situation de ma parcelle", "📋 لخّص لي حالة حقلي"),
    "q_drought": ("🌵 Is there a drought risk?", "🌵 Y a-t-il un risque de sécheresse ?", "🌵 هل هناك خطر جفاف؟"),
    "q_irrigation": ("💧 Which crop needs the least irrigation?", "💧 Quelle culture demande le moins d'irrigation ?",
                     "💧 أي زراعة تحتاج أقل سقي؟"),
    "q_grow": ("🌱 What should I grow this season?", "🌱 Que dois-je cultiver cette saison ?", "🌱 ماذا أزرع هذا الموسم؟"),
    "q_soil": ("🟫 How is the soil moisture?", "🟫 Comment est l'humidité du sol ?", "🟫 كيف هي حالة رطوبة التربة؟"),
}

CROP_NAMES = {  # English -> (Français, العربية)
    "Wheat": ("Blé", "القمح"), "Barley": ("Orge", "الشعير"), "Oat": ("Avoine", "الخرطال"),
    "Maize": ("Maïs", "الذرة"), "Sorghum": ("Sorgho", "الذرة البيضاء"), "Chickpea": ("Pois chiche", "الحمص"),
    "Lentil": ("Lentille", "العدس"), "Faba bean": ("Fève", "الفول"), "Pea": ("Petit pois", "الجلبان"),
    "Peanut": ("Arachide", "الكاوكاو"), "Potato": ("Pomme de terre", "البطاطس"), "Tomato": ("Tomate", "الطماطم"),
    "Pepper": ("Poivron", "الفلفل"), "Onion": ("Oignon", "البصل"), "Carrot": ("Carotte", "الجزر"),
    "Sugar beet": ("Betterave sucrière", "الشمندر السكري"), "Sunflower": ("Tournesol", "عباد الشمس"),
    "Rapeseed": ("Colza", "السلجم (الكولزا)"), "Melon": ("Melon", "البطيخ الأصفر"),
    "Watermelon": ("Pastèque", "الدلاح"), "Fallow": ("Jachère", "البور (راحة الأرض)"),
}
FAMILY_NAMES = {
    "Cereal": ("Céréale", "حبوب"), "Legume": ("Légumineuse", "بقوليات"), "Tuber": ("Tubercule", "درنيات"),
    "Vegetable": ("Légume", "خضر"), "Allium": ("Alliacée", "بصليات"), "Root crop": ("Racine", "جذريات"),
    "Oilseed": ("Oléagineux", "زيتيات"), "Brassica": ("Crucifère", "صليبيات"), "Cucurbit": ("Cucurbitacée", "قرعيات"),
    "Fallow": ("Jachère", "بور"),
}


def t(key, **kw):
    row = UI.get(key)
    text = row[_I[lang()]] if row else key
    return text.format(**kw) if kw else text


def crop(name):
    if lang() == "en" or name not in CROP_NAMES:
        return name
    return CROP_NAMES[name][_I[lang()] - 1]


def family(name):
    if lang() == "en" or name not in FAMILY_NAMES:
        return name
    return FAMILY_NAMES[name][_I[lang()] - 1]


# ---------------------------------------------------------
# Sentences with numbers: (English regex, Français, العربية). {0}, {1} = captured parts.
# ---------------------------------------------------------
PATTERNS = [
    # verdict
    (r"Watch the water: conditions are drier than usual\.",
     "Attention à l'eau : conditions plus sèches que d'habitude.", "انتبه للماء: الظروف أجف من المعتاد."),
    (r"Mostly normal, with one point to watch\.",
     "Plutôt normal, avec un point à surveiller.", "الوضع عادي في الغالب، مع نقطة واحدة للمراقبة."),
    (r"Conditions look normal for the season\.",
     "Les conditions semblent normales pour la saison.", "الظروف تبدو عادية بالنسبة لهذا الموسم."),
    (r"Load the data to get a verdict for this field\.",
     "Chargez les données pour obtenir un avis sur cette parcelle.", "حمّل البيانات للحصول على تقييم لهذا الحقل."),
    (r"Only (\S+) mm of rain in the last (\d+) days, less than half the usual (\S+) mm\.",
     "Seulement {0} mm de pluie ces {1} derniers jours, moins de la moitié des {2} mm habituels.",
     "فقط {0} ملم من المطر في آخر {1} يوماً، أقل من نصف المعتاد ({2} ملم)."),
    (r"(\S+) mm of rain in the last (\d+) days, well above the usual (\S+) mm\.",
     "{0} mm de pluie ces {1} derniers jours, bien au-dessus des {2} mm habituels.",
     "{0} ملم من المطر في آخر {1} يوماً، أكثر بكثير من المعتاد ({2} ملم)."),
    (r"(\S+) mm of rain in the last (\d+) days, close to the usual (\S+) mm\.",
     "{0} mm de pluie ces {1} derniers jours, proche des {2} mm habituels.",
     "{0} ملم من المطر في آخر {1} يوماً، قريب من المعتاد ({2} ملم)."),
    (r"Heat peaks reached (\S+) °C: risk of heat stress\.",
     "Les pics de chaleur ont atteint {0} °C : risque de stress thermique.",
     "وصلت الحرارة القصوى إلى {0} °م: خطر الإجهاد الحراري."),
    (r"The soil is drier than usual for this time of year\.",
     "Le sol est plus sec que d'habitude pour cette période.", "التربة أجف من المعتاد في هذا الوقت من السنة."),
    (r"The soil is wetter than usual for this time of year\.",
     "Le sol est plus humide que d'habitude pour cette période.", "التربة أرطب من المعتاد في هذا الوقت من السنة."),
    (r"Soil moisture is normal for this time of year\.",
     "L'humidité du sol est normale pour cette période.", "رطوبة التربة عادية في هذا الوقت من السنة."),
    (r"Drought risk for the next 14 days: (.+) \((\S+)\)\.",
     "Risque de sécheresse pour les 14 prochains jours : {0} ({1}).",
     "خطر الجفاف في الأيام الـ14 القادمة: {0} ({1})."),
    (r"Vegetation index is low \((\S+)\): bare soil, stubble or sparse crop\.",
     "Indice de végétation faible ({0}) : sol nu, chaumes ou culture clairsemée.",
     "مؤشر الغطاء النباتي منخفض ({0}): تربة عارية أو بقايا حصاد أو زرع خفيف."),
    (r"Vegetation is dense and green \(NDVI (\S+)\)\.",
     "La végétation est dense et verte (NDVI {0}).", "الغطاء النباتي كثيف وأخضر (NDVI {0})."),
    (r"Vegetation is moderate \(NDVI (\S+)\)\.",
     "La végétation est modérée (NDVI {0}).", "الغطاء النباتي متوسط (NDVI {0})."),
    (r"The last 12 months are among the driest of the last (\d+) years\.",
     "Les 12 derniers mois sont parmi les plus secs des {0} dernières années.",
     "الأشهر الـ12 الأخيرة من بين الأكثر جفافاً في آخر {0} سنوات."),
    (r"The last 12 months are among the wettest of the last (\d+) years\.",
     "Les 12 derniers mois sont parmi les plus humides des {0} dernières années.",
     "الأشهر الـ12 الأخيرة من بين الأكثر مطراً في آخر {0} سنوات."),
    # alerts
    (r"Low soil moisture: root-zone wetness (\S+) is below your threshold (\S+)",
     "Sol sec : humidité racinaire {0} sous votre seuil {1}", "تربة جافة: رطوبة الجذور {0} تحت الحد {1}"),
    (r"Low rainfall: (\S+) mm, less than (\S+) of the usual (\S+) mm",
     "Pluie faible : {0} mm, moins de {1} des {2} mm habituels", "مطر قليل: {0} ملم، أقل من {1} من المعتاد ({2} ملم)"),
    (r"Heat stress: maximum temperature (\S+) °C is above your threshold (\S+) °C",
     "Stress thermique : température max {0} °C au-dessus de votre seuil {1} °C",
     "إجهاد حراري: أعلى حرارة {0} °م فوق الحد {1} °م"),
    # crop advice
    (r"Your field was already resting last season\.",
     "Votre parcelle était déjà au repos la saison dernière.", "حقلك كان في راحة الموسم الماضي."),
    (r"After 3 cropped seasons, a rest year lets the soil recover and store water\.",
     "Après 3 saisons cultivées, une année de repos permet au sol de récupérer et de stocker l'eau.",
     "بعد 3 مواسم زراعة، سنة راحة تسمح للتربة بأن تسترجع وتخزن الماء."),
    (r"(.+) again right after (.+): more diseases, pests and weeds, lower yield\.",
     "{0} juste après {1} : plus de maladies, ravageurs et mauvaises herbes, rendement plus faible.",
     "{0} مباشرة بعد {1}: أمراض وحشرات وأعشاب أكثر ومردود أقل."),
    (r"(.+) was grown (\d+) time\(s\) in the last 3 seasons: wait longer if you can\.",
     "{0} a été cultivé {1} fois ces 3 dernières saisons : attendez plus si possible.",
     "{0} زُرع {1} مرة في المواسم الثلاثة الأخيرة: انتظر أكثر إن أمكن."),
    (r"Same family as last season \((.+)\): pests and diseases carry over\.",
     "Même famille que la saison dernière ({0}) : ravageurs et maladies se transmettent.",
     "نفس عائلة الموسم الماضي ({0}): الحشرات والأمراض تنتقل."),
    (r"No legume in the last 3 seasons: this one adds free nitrogen to your soil\.",
     "Aucune légumineuse ces 3 dernières saisons : celle-ci apporte de l'azote gratuit au sol.",
     "لا بقوليات في المواسم الثلاثة الأخيرة: هذه الزراعة تضيف الآزوت مجاناً للتربة."),
    (r"A legume: adds nitrogen to the soil\.",
     "Une légumineuse : apporte de l'azote au sol.", "من البقوليات: تضيف الآزوت للتربة."),
    (r"Breaks a run of (\d+) cereal seasons: cuts cereal diseases and weeds\.",
     "Interrompt {0} saisons de céréales : réduit les maladies et mauvaises herbes.",
     "تكسر {0} مواسم متتالية من الحبوب: تقلل أمراض الحبوب والأعشاب."),
    (r"A cereal after (.+) uses the nitrogen the legume left in the soil\.",
     "Une céréale après {0} profite de l'azote laissé par la légumineuse.",
     "الحبوب بعد {0} تستفيد من الآزوت الذي تركته البقوليات."),
    (r"A new crop family for this field: more diversity\.",
     "Une nouvelle famille de cultures pour cette parcelle : plus de diversité.",
     "عائلة زراعات جديدة لهذا الحقل: تنوع أكثر."),
    (r"Rain \+ your irrigation covers its needs in a normal year \(rain alone: (\S+) %\)\.",
     "Pluie + votre irrigation couvrent ses besoins en année normale (pluie seule : {0} %).",
     "المطر + سقيك يغطيان حاجتها في سنة عادية (المطر وحده: {0}%)."),
    (r"Rain covers its needs in a normal year \(rain alone: (\S+) %\)\.",
     "La pluie couvre ses besoins en année normale (pluie seule : {0} %).",
     "المطر يغطي حاجتها في سنة عادية (المطر وحده: {0}%)."),
    (r"Needs about (\S+) mm of irrigation in a normal year \((\S+) m³/ha\), you have (\S+) mm\.",
     "Demande environ {0} mm d'irrigation en année normale ({1} m³/ha), vous avez {2} mm.",
     "تحتاج حوالي {0} ملم من السقي في سنة عادية ({1} م³/هكتار)، ولديك {2} ملم."),
    (r"In a dry year \(1 in 5\) it would need (\S+) mm of irrigation\.",
     "En année sèche (1 sur 5), il faudrait {0} mm d'irrigation.",
     "في سنة جافة (1 من 5) ستحتاج {0} ملم من السقي."),
    (r"No harvest this season \(no income\)\.",
     "Pas de récolte cette saison (pas de revenu).", "لا حصاد هذا الموسم (لا دخل)."),
    (r"High drought risk now: crops that need less water are favoured\.",
     "Risque de sécheresse élevé : les cultures qui demandent moins d'eau sont favorisées.",
     "خطر جفاف مرتفع الآن: نفضّل الزراعات التي تحتاج ماء أقل."),
]
_COMPILED = [(re.compile(rx), fr, ar) for rx, fr, ar in PATTERNS]
_LEVELS = {"low": ("faible", "منخفض"), "moderate": ("modéré", "متوسط"), "high": ("élevé", "مرتفع"), "very high": ("très élevé", "مرتفع جداً"), "medium": ("moyen", "متوسط"),
           "very": ("très élevé", "مرتفع جداً")}


def _word(part):
    """Translate crop / family / level words found inside a sentence."""
    for table in (CROP_NAMES, FAMILY_NAMES):
        for en, (fr, ar) in table.items():
            if part.lower() == en.lower():
                return fr if lang() == "fr" else ar
    if part.lower() in _LEVELS:
        return _LEVELS[part.lower()][0 if lang() == "fr" else 1]
    return part


def tr(text):
    if lang() == "en" or not text:
        return text
    for rx, fr, ar in _COMPILED:
        m = rx.fullmatch(text.strip())
        if m:
            return (fr if lang() == "fr" else ar).format(*[_word(g) for g in m.groups()])
    return text


def css():
    """Arabic font and right-to-left layout when Arabic is chosen."""
    base = ("<style>@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');"
            "html, body, .stApp, p, li, label, button, h1, h2, h3, h4 "
            "{ font-family: 'Instrument Sans', 'Cairo', system-ui, sans-serif; }"
            "[data-testid='stIconMaterial'], span[role='img'][translate='no'] "
            "{ font-family: 'Material Symbols Rounded' !important; }</style>")
    if not is_rtl():
        return base
    return base + ("<style>[data-testid='stMain'] .block-container, [data-testid='stSidebarContent'] "
                   "{ direction: rtl; text-align: right; }"
                   ".js-plotly-plot, iframe, [data-testid='stDeckGlJsonChart'], .stSlider { direction: ltr; }"
                   "[data-testid='stMetricValue'], .fs-mc-value { direction: ltr; text-align: right; }</style>")
