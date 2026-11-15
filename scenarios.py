"""
scenarios.py - Compare crop rotation scenarios (functions 6, 8 and 11 of the document).

A scenario = a sequence of crops, one per year, e.g. Wheat -> Chickpea.
Each scenario gets transparent scores (0 = bad, 1 = good):
  - Water   : average irrigation need per year (less is better)
  - Risk    : share of past years where the need is larger than the water available
  - Rotation: simple agronomy rules (legumes, no same crop twice, no cereal after cereal ...)
The final rank uses the weights chosen by the user. All assumptions are shown.
"""

import pandas as pd

from src.crops import CROPS, seasons_table

DEFAULT_SCENARIOS = {
    "Wheat → Wheat (monoculture)": ["Wheat", "Wheat"],
    "Wheat → Chickpea": ["Wheat", "Chickpea"],
    "Wheat → Faba bean": ["Wheat", "Faba bean"],
    "Barley → Fallow": ["Barley", "Fallow"],
    "Wheat → Lentil → Barley": ["Wheat", "Lentil", "Barley"],
    "Wheat → Tomato (irrigated)": ["Wheat", "Tomato"],
}


def rotation_notes(crops, previous_crop=None):
    """Agronomy score (0..1) with the reasons, so the user sees WHY."""
    score, pros, cons = 0.6, [], []
    sequence = ([previous_crop] if previous_crop and previous_crop != "Unknown" else []) + crops
    families = [CROPS[c]["family"] for c in sequence]

    if any(CROPS[c]["legume"] for c in crops):
        score += 0.25
        pros.append("includes a legume (adds nitrogen to the soil)")
    if "Fallow" in crops:
        score += 0.05
        pros.append("fallow year rests the soil and stores some water")
    for a, b, fa, fb in zip(sequence, sequence[1:], families, families[1:]):
        if a == b and a != "Fallow":
            score -= 0.3
            cons.append(f"{a} after {a}: more diseases and weeds, lower yields")
        elif fa == fb == "Cereal":
            score -= 0.15
            cons.append(f"{b} after {a}: cereal after cereal")
        elif fa == fb and fa != "Fallow":
            score -= 0.1
            cons.append(f"{b} after {a}: same family")
    if len(set(crops)) >= 3:
        score += 0.1
        pros.append("diverse rotation (3 different crops)")
    return max(0.0, min(1.0, score)), pros, cons


def evaluate_scenario(df, latitude, crops, water_available_mm, previous_crop=None):
    tables = [seasons_table(df, c, latitude) for c in crops]
    needs = [t["irrigation_mm"] for t in tables if not t.empty]
    if not needs:
        return None
    mean_need = sum(n.median() for n in needs) / len(needs)
    dry_need = sum(n.quantile(0.8) for n in needs) / len(needs)
    # risk: share of past seasons where the need is above the available water
    shortfall = pd.concat(needs) > water_available_mm
    agronomy, pros, cons = rotation_notes(crops, previous_crop)
    if mean_need < 50:
        pros.append("can be grown almost fully rainfed")
    if dry_need > water_available_mm:
        cons.append(f"in a dry year needs ~{dry_need:.0f} mm, more than the {water_available_mm:.0f} mm available")
    return {"need_mm": mean_need, "dry_need_mm": dry_need, "risk": float(shortfall.mean()),
            "agronomy": agronomy, "pros": pros, "cons": cons}


def rank_scenarios(df, latitude, scenarios, water_available_mm, weights, previous_crop=None):
    rows = []
    for name, crops in scenarios.items():
        r = evaluate_scenario(df, latitude, crops, water_available_mm, previous_crop)
        if r:
            rows.append({"Scenario": name, **r})
    table = pd.DataFrame(rows)
    if table.empty:
        return table
    max_need = max(table["need_mm"].max(), 1)
    table["water_score"] = 1 - table["need_mm"] / max_need
    table["risk_score"] = 1 - table["risk"]
    total = sum(weights.values()) or 1
    table["score"] = (weights["water"] * table["water_score"] + weights["risk"] * table["risk_score"]
                      + weights["rotation"] * table["agronomy"]) / total
    return table.sort_values("score", ascending=False).reset_index(drop=True)


def compare_to_baseline(table, baseline_name):
    """Add 'difference vs the current rotation' to every scenario."""
    base = table[table["Scenario"] == baseline_name]
    if base.empty:
        return table
    base = base.iloc[0]
    table = table.copy()
    table["water_vs_current"] = table["need_mm"] - base["need_mm"]
    table["score_vs_current"] = table["score"] - base["score"]
    notes = []
    for _, row in table.iterrows():
        if row["Scenario"] == baseline_name:
            notes.append("This is your current rotation (the reference).")
            continue
        dw = row["water_vs_current"]
        water_txt = (f"{-dw:.0f} mm less irrigation per year" if dw < -5 else
                     f"{dw:.0f} mm more irrigation per year" if dw > 5 else "about the same water")
        dr = 100 * (row["risk"] - base["risk"])
        risk_txt = (f"{-dr:.0f} % fewer years short of water" if dr < -2 else
                    f"{dr:.0f} % more years short of water" if dr > 2 else "same shortage risk")
        da = row["agronomy"] - base["agronomy"]
        soil_txt = ("better for the soil" if da > 0.05 else "worse for the soil" if da < -0.05
                    else "similar for the soil")
        notes.append(f"Compared with your current rotation: {water_txt}, {risk_txt}, {soil_txt}.")
    table["vs_current"] = notes
    return table
