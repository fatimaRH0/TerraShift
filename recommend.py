"""
recommend.py - "What can I grow this season?"

Based on:
  1. what the farmer grew in the LAST 3 SEASONS (rotation rules: diseases, nitrogen, family)
  2. how well each crop fits the local WATER conditions (NASA POWER, FAO-56 water balance)
  3. this year's DROUGHT RISK (TerraShift model), when available
Every suggestion comes with its reasons and its warnings, so the farmer can judge.
"""

from datetime import date

import pandas as pd

from src.crops import CROPS

ICONS = {"Wheat": "🌾", "Barley": "🌾", "Oat": "🌾", "Maize": "🌽", "Sorghum": "🌾", "Chickpea": "🫘",
         "Faba bean": "🫛", "Pea": "🫛", "Peanut": "🥜", "Lentil": "🫘", "Potato": "🥔", "Tomato": "🍅",
         "Pepper": "🌶️", "Onion": "🧅", "Carrot": "🥕", "Sugar beet": "🟣", "Sunflower": "🌻", "Rapeseed": "🌼",
         "Melon": "🍈", "Watermelon": "🍉", "Fallow": "🟫"}


def season_labels(today=None):
    """Return the label of the coming season and of the 3 previous ones, e.g. '2026-27'."""
    today = today or date.today()
    start = today.year if today.month >= 7 else today.year - 1
    label = lambda y: f"{y}-{str(y + 1)[2:]}"
    return label(start), [label(start - 3), label(start - 2), label(start - 1)]


def next_sowing(crop, today=None):
    today = today or date.today()
    month, day = CROPS[crop]["sowing"]
    d = date(today.year, month, day)
    return d if d >= today else date(today.year + 1, month, day)


def rotation_score(crop, history):
    """history = crops of the last 3 seasons, oldest first (may contain None)."""
    past = [c for c in history if c]
    last = past[-1] if past else None
    family = CROPS[crop]["family"]
    score, reasons, warnings = 0.5, [], []

    if crop == "Fallow":
        if last == "Fallow":
            score -= 0.3
            warnings.append("Your field was already resting last season.")
        elif len(past) == 3 and "Fallow" not in past:
            score += 0.15
            reasons.append("After 3 cropped seasons, a rest year lets the soil recover and store water.")
        return max(0.0, min(1.0, score)), reasons, warnings

    times = past.count(crop)
    if last == crop:
        score -= 0.45
        warnings.append(f"{crop} again right after {crop}: more diseases, pests and weeds, lower yield.")
    elif times:
        score -= 0.15 * times
        warnings.append(f"{crop} was grown {times} time(s) in the last 3 seasons: wait longer if you can.")
    if last and last != crop and CROPS[last]["family"] == family and family != "Fallow":
        score -= 0.2
        warnings.append(f"Same family as last season ({family.lower()}): pests and diseases carry over.")

    if CROPS[crop]["legume"]:
        if not any(CROPS[c]["legume"] for c in past):
            score += 0.3
            reasons.append("No legume in the last 3 seasons: this one adds free nitrogen to your soil.")
        else:
            score += 0.1
            reasons.append("A legume: adds nitrogen to the soil.")
    cereal_years = sum(1 for c in past if CROPS[c]["family"] == "Cereal")
    if family != "Cereal" and cereal_years >= 2:
        score += 0.15
        reasons.append(f"Breaks a run of {cereal_years} cereal seasons: cuts cereal diseases and weeds.")
    if family == "Cereal" and last and CROPS[last]["legume"]:
        score += 0.2
        reasons.append(f"A cereal after {last.lower()} uses the nitrogen the legume left in the soil.")
    if crop not in past and family not in [CROPS[c]["family"] for c in past]:
        score += 0.05
        reasons.append("A new crop family for this field: more diversity.")
    return max(0.0, min(1.0, score)), reasons, warnings


def water_score(row, water_available_mm):
    """How well the crop's water need is covered by rain + the irrigation the farmer has."""
    etc = row["Crop water use (mm)"]
    if etc <= 0:
        return 1.0, [], []
    normal = row["Irrigation – normal year (mm)"]
    dry = row["Irrigation – dry year (mm)"]
    covered = min(1.0, (row["Effective rain (mm)"] + water_available_mm) / etc)
    reasons, warnings = [], []
    if normal <= water_available_mm + 10:
        reasons.append(f"Rain{' + your irrigation' if water_available_mm else ''} covers its needs "
                       f"in a normal year (rain alone: {row['Rain covers (%)']:.0f} %).")
    else:
        warnings.append(f"Needs about {normal:.0f} mm of irrigation in a normal year "
                        f"({normal * 10:,.0f} m³/ha), you have {water_available_mm} mm.")
    if dry > water_available_mm + 10 and normal <= water_available_mm + 10:
        warnings.append(f"In a dry year (1 in 5) it would need {dry:.0f} mm of irrigation.")
    return covered, reasons, warnings


def recommend(history, summary, water_available_mm=0, drought_probability=None, today=None):
    """Rank every crop for the coming season. Returns a DataFrame (best first)."""
    water_weight = 0.5
    context = []
    if drought_probability is not None and drought_probability >= 0.6:
        water_weight = 0.65
        context.append("High drought risk now: crops that need less water are favoured.")
    rows = []
    for _, row in summary.iterrows():
        crop = row["Crop"]
        r_score, r_reasons, r_warn = rotation_score(crop, history)
        if crop == "Fallow":          # no water needed, but also no harvest: neutral water score
            w_score, w_reasons, w_warn = 0.5, [], ["No harvest this season (no income)."]
        else:
            w_score, w_reasons, w_warn = water_score(row, water_available_mm)
        score = water_weight * w_score + (1 - water_weight) * r_score
        last = next((c for c in reversed(history) if c), None)
        if crop == last and crop != "Fallow":
            score *= 0.6                      # same crop two seasons in a row: strongly discouraged
        rows.append({"crop": crop, "icon": ICONS.get(crop, "🌱"), "score": score,
                     "rotation": r_score, "water": w_score, "sow": next_sowing(crop, today),
                     "reasons": r_reasons + w_reasons, "warnings": r_warn + w_warn,
                     # the main reason to avoid it = the weaker of the two criteria
                     "main_warning": ((w_warn if w_score < r_score else r_warn) or r_warn + w_warn or [""])[0],
                     "family": CROPS[crop]["family"]})
    table = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
    table = diversify(table)
    table.attrs["context"] = context
    return table


def diversify(table, top=3, family_penalty=0.15):
    """
    Pick the top suggestions one by one; a crop whose family is already suggested
    counts 0.15 less, so the farmer sees real alternatives (not 3 crops of one family).
    """
    remaining = list(table.index)
    chosen, families = [], []
    while remaining and len(chosen) < top:
        best = max(remaining, key=lambda i: table.loc[i, "score"]
                   - family_penalty * families.count(table.loc[i, "family"]))
        chosen.append(best)
        families.append(table.loc[best, "family"])
        remaining.remove(best)
    return table.loc[chosen + remaining].reset_index(drop=True)
