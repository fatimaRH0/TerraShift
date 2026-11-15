"""
ml.py - Machine learning: predict the risk of an UNUSUALLY DRY period.
Function 5 of the TerraShift document.

Question the model answers:
    "Will the next 14 days be unusually dry for this season, at this place?"

Why "unusually dry for this season"?
    In summer the soil is ALWAYS dry in Morocco, so a fixed threshold would just
    learn "summer = dry". We compare each period with the SAME calendar month of
    the past years (like the History tab): dry = among the 20 % driest.

Steps (the classic ML workflow):
  1. features   : what we know TODAY (past rain, temperature, soil moisture, month)
  2. target     : what happened in the NEXT 14 days (1 = unusually dry, 0 = not)
  3. split      : train on the old years, test on the most recent year (never the future!)
  4. models     : baseline rule, Decision Tree, Random Forest
  5. evaluation : accuracy, precision, recall, F1, confusion matrix
  6. prediction : risk for the next 14 days from today's data
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.tree import DecisionTreeClassifier

HORIZON = 14          # days we predict ahead
DRY_PERCENTILE = 20   # "unusually dry" = among the 20 % driest for that month

FEATURE_LABELS = {
    "rain_7d": "Rain, last 7 days (mm)",
    "rain_30d": "Rain, last 30 days (mm)",
    "rain_90d": "Rain, last 90 days (mm)",
    "tmax_7d": "Mean max temperature, last 7 days (°C)",
    "t2m_30d": "Mean temperature, last 30 days (°C)",
    "rh_7d": "Air humidity, last 7 days (%)",
    "root_now": "Root-zone wetness today",
    "root_change_7d": "Root-zone wetness change over 7 days",
    "surface_now": "Surface wetness today",
    "root_vs_normal": "Root-zone wetness vs normal for the month",
    "rain30_vs_normal": "Rain last 30 days vs normal for the month (mm)",
    "month_sin": "Season (sin)",
    "month_cos": "Season (cos)",
}
FEATURES = list(FEATURE_LABELS)


# ---------------------------------------------------------
# 1) Features: only information available on that day
# ---------------------------------------------------------
def build_features(df):
    f = pd.DataFrame(index=df.index)
    f["rain_7d"] = df["PRECTOTCORR"].rolling(7).sum()
    f["rain_30d"] = df["PRECTOTCORR"].rolling(30).sum()
    f["rain_90d"] = df["PRECTOTCORR"].rolling(90).sum()
    f["tmax_7d"] = df["T2M_MAX"].rolling(7).mean()
    f["t2m_30d"] = df["T2M"].rolling(30).mean()
    f["rh_7d"] = df["RH2M"].rolling(7).mean()
    f["root_now"] = df["GWETROOT"]
    f["root_change_7d"] = df["GWETROOT"] - df["GWETROOT"].shift(7)
    f["surface_now"] = df["GWETTOP"]
    # month as a circle, so December (12) is close to January (1)
    angle = 2 * np.pi * (df.index.dayofyear / 365.25)
    f["month_sin"], f["month_cos"] = np.sin(angle), np.cos(angle)
    return f


def add_anomaly_features(feats, df, train_index):
    """
    Compare today with the NORMAL for this month (normals from TRAINING years only,
    so the model never sees information from the test period).
    """
    months = feats.index.month
    root_normal = df["GWETROOT"].loc[train_index].groupby(train_index.month).median()
    rain_normal = feats["rain_30d"].loc[train_index].groupby(train_index.month).mean()
    feats = feats.copy()
    feats["root_vs_normal"] = df["GWETROOT"] - months.map(root_normal).values
    feats["rain30_vs_normal"] = feats["rain_30d"] - months.map(rain_normal).values
    return feats, {"root": root_normal, "rain30": rain_normal}


# ---------------------------------------------------------
# 2) Target: what happens in the NEXT 14 days
# ---------------------------------------------------------
def future_wetness(df):
    """Mean root-zone wetness over the next HORIZON days (NaN at the end)."""
    return df["GWETROOT"][::-1].rolling(HORIZON).mean()[::-1].shift(-1)


def dry_thresholds(future, train_index):
    """20th percentile of future wetness for each calendar month, from TRAINING years only."""
    train = future.loc[train_index].dropna()
    return train.groupby(train.index.month).quantile(DRY_PERCENTILE / 100)


def make_target(future, thresholds):
    limit = future.index.month.map(thresholds).values
    target = (future.values < limit).astype(float)
    target[np.isnan(future.values)] = np.nan
    return pd.Series(target, index=future.index)


# ---------------------------------------------------------
# 3-5) Train and evaluate
# ---------------------------------------------------------
def evaluate(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "confusion": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(),
    }


def train_and_evaluate(df, test_days=365):
    """
    df = daily NASA POWER history (several years).
    Returns a dict with the trained models, metrics and the data used.
    """
    feats = build_features(df)
    future = future_wetness(df)

    # Time split: the last `test_days` days (that have a known future) are the test set
    known = future.dropna().index
    split_date = known[-test_days]
    train_idx = known[(known < split_date) & (known >= feats.dropna().index[0])]
    test_idx = known[known >= split_date]

    thresholds = dry_thresholds(future, train_idx)
    target = make_target(future, thresholds)
    feats, normals = add_anomaly_features(feats, df, train_idx)

    X_train, y_train = feats.loc[train_idx], target.loc[train_idx].astype(int)
    X_test, y_test = feats.loc[test_idx], target.loc[test_idx].astype(int)

    # Baseline: "if the soil is already unusually dry today, it will stay dry"
    today_limit = X_test.index.month.map(thresholds).values
    baseline_pred = (X_test["root_now"].values < today_limit).astype(int)

    tree = DecisionTreeClassifier(max_depth=4, class_weight="balanced", random_state=0)
    forest = RandomForestClassifier(n_estimators=300, max_depth=6, min_samples_leaf=10,
                                    class_weight="balanced", random_state=0, n_jobs=-1)
    tree.fit(X_train, y_train)
    forest.fit(X_train, y_train)

    forest_pred = forest.predict(X_test)
    results = {
        "Baseline rule": evaluate(y_test, baseline_pred),
        "Decision Tree": evaluate(y_test, tree.predict(X_test)),
        "Random Forest": evaluate(y_test, forest_pred),
    }

    # The HARD part: days that are NOT dry today but become dry (the onset of a drought).
    # The baseline rule can never predict these, the model can try.
    not_dry_today = baseline_pred == 0
    onsets = int(y_test[not_dry_today].sum())
    caught = int(((forest_pred == 1) & (y_test.values == 1) & not_dry_today).sum())
    false_alarms = int(((forest_pred == 1) & (y_test.values == 0) & not_dry_today).sum())
    onset = {"onsets": onsets, "caught": caught, "false_alarms": false_alarms}
    test_table = pd.DataFrame({
        "actual": y_test,
        "probability": forest.predict_proba(X_test)[:, 1],
        "future_wetness": future.loc[test_idx],
        "dry_limit": X_test.index.month.map(thresholds).values,
    }, index=test_idx)

    importance = pd.Series(forest.feature_importances_, index=FEATURES).sort_values(ascending=False)

    return {
        "forest": forest, "tree": tree, "thresholds": thresholds, "results": results,
        "onset": onset, "normals": normals,
        "importance": importance, "test": test_table, "features": feats,
        "split_date": split_date, "n_train": len(train_idx), "n_test": len(test_idx),
        "dry_share_train": float(y_train.mean()),
    }


# ---------------------------------------------------------
# 6) Prediction for today
# ---------------------------------------------------------
def risk_level(probability):
    if probability >= 0.6:
        return "🔴 High"
    if probability >= 0.3:
        return "🟠 Medium"
    return "🟢 Low"


def predict_today(model_info):
    feats = model_info["features"].dropna()
    today = feats.iloc[[-1]]
    probability = float(model_info["forest"].predict_proba(today)[0, 1])
    return {"date": today.index[0], "probability": probability, "level": risk_level(probability),
            "inputs": today.iloc[0]}
