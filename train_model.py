"""
FIELD SHIFT - Step 7: train the drought-risk model in the terminal
-------------------------------------------------------------------
Run:
    python train_model.py
It uses the long NASA POWER history (downloaded by the History tab)
and prints how good the model is. The dashboard trains the same model itself.
"""

import joblib
import os

from src import config, ml
from src.history import get_long_history


def main(years=20):
    # More years = more examples of dry periods for the model to learn from
    df = get_long_history(config.LATITUDE, config.LONGITUDE, config.FIELD_NAME, years=years)
    print(f"📚 {len(df)} days of NASA POWER data ({df.index.min():%Y-%m-%d} → {df.index.max():%Y-%m-%d})")

    info = ml.train_and_evaluate(df)
    print(f"✂️  Train: {info['n_train']} days   Test: {info['n_test']} days (from {info['split_date']:%Y-%m-%d})")
    print(f"   'Unusually dry' periods in training data: {info['dry_share_train']:.0%}\n")

    print(f"{'Model':16s} {'Accuracy':>9s} {'Precision':>10s} {'Recall':>8s} {'F1':>6s}")
    for name, r in info["results"].items():
        print(f"{name:16s} {r['accuracy']:9.2f} {r['precision']:10.2f} {r['recall']:8.2f} {r['f1']:6.2f}")

    cm = info["results"]["Random Forest"]["confusion"]
    print("\nRandom Forest confusion matrix (rows = actual, columns = predicted):")
    print(f"               not dry   dry")
    print(f"   not dry     {cm[0][0]:7d} {cm[0][1]:5d}")
    print(f"   dry         {cm[1][0]:7d} {cm[1][1]:5d}")

    o = info["onset"]
    print(f"\n🌱→🏜️  Start of a dry period (not dry today, dry in {ml.HORIZON} days): {o['onsets']} days in the test year")
    print(f"   Random Forest caught {o['caught']} of them, with {o['false_alarms']} false alarms "
          f"(the baseline rule catches 0 by design)")

    print("\n🔎 Most important features:")
    for name, value in info["importance"].head(5).items():
        print(f"   {ml.FEATURE_LABELS[name]:42s} {value:.2f}")

    today = ml.predict_today(info)
    print(f"\n🌦️  Risk of an unusually dry period in the next {ml.HORIZON} days "
          f"(from {today['date']:%d %b %Y}): {today['level']}  ({today['probability']:.0%})")

    os.makedirs(os.path.join(config.DATA_DIR, "models"), exist_ok=True)
    path = os.path.join(config.DATA_DIR, "models", f"{config.FIELD_NAME}_drought_rf.joblib")
    joblib.dump({"model": info["forest"], "thresholds": info["thresholds"],
                 "normals": info["normals"], "features": ml.FEATURES}, path)
    print(f"💾 Model saved: {path}")


if __name__ == "__main__":
    main()
