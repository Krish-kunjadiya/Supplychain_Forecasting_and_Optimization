"""
pipeline_service.py — Real ML inference pipeline
NB01 → NB07 logic as async background task
"""

import os, asyncio, json
import numpy as np
import pandas as pd
import joblib
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", category=UserWarning)

_HERE       = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.abspath(os.path.join(_HERE, "../../.."))
MODELS_DIR  = os.path.join(_ROOT, "models")
OUTPUTS_DIR = os.path.join(_ROOT, "outputs")
UPLOADS_DIR = os.path.join(_ROOT, "uploads")

REQUIRED_COLUMNS = [
    "Date","SKU_ID","Warehouse_ID","Supplier_ID","Region",
    "Units_Sold","Inventory_Level","Supplier_Lead_Time_Days",
    "Reorder_Point","Order_Quantity","Unit_Cost","Unit_Price",
    "Promotion_Flag","Stockout_Flag","Demand_Forecast"
]

LOOKBACK = 30


async def run_pipeline(csv_path: str, job_id: str):
    from backend.app.services.job_service import update_job
    job_dir = os.path.join(UPLOADS_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    try:
        # ── STEP 1: Validate & Clean (0→10%) ──────────────────────
        await update_job(job_id, 5, "Validating schema and cleaning data...")
        df = pd.read_csv(csv_path, parse_dates=["Date"])
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        df["Units_Sold"] = df["Units_Sold"].clip(lower=0)
        df = df.drop_duplicates().reset_index(drop=True)
        df = df.sort_values(["SKU_ID","Warehouse_ID","Date"]).reset_index(drop=True)
        await update_job(job_id, 10, "Validation complete.")

        # ── STEP 2: Feature Engineering (10→40%) ──────────────────
        await update_job(job_id, 15, "Engineering features...")
        df = _build_features(df)
        await update_job(job_id, 35, "Saving feature sets...")

        with open(os.path.join(OUTPUTS_DIR, "feature_registry.json")) as f:
            registry = json.load(f)
        XGB_FEATURES  = registry["xgboost_features"]
        LSTM_FEATURES = registry["lstm_features"]
        TARGET        = registry.get("target", "Units_Sold")

        df_clean = df.dropna(subset=XGB_FEATURES).reset_index(drop=True)
        df_clean.to_csv(os.path.join(job_dir, "features_xgb.csv"), index=False)
        lstm_cols = ["Date","SKU_ID","Warehouse_ID"] + [
            c for c in LSTM_FEATURES if c in df_clean.columns
        ]
        df_clean[lstm_cols].to_csv(os.path.join(job_dir, "features_lstm.csv"), index=False)
        await update_job(job_id, 40, "Feature engineering complete.")

        # ── STEP 3: XGBoost Inference (40→55%) ────────────────────
        await update_job(job_id, 42, "Running XGBoost inference...")
        xgb_model = joblib.load(os.path.join(MODELS_DIR, "xgb_final_model.pkl"))
        X_xgb     = df_clean[[c for c in XGB_FEATURES if c in df_clean.columns]].values
        xgb_preds = np.clip(xgb_model.predict(X_xgb), 0, None)
        df_xgb    = df_clean[["Date","SKU_ID","Warehouse_ID",TARGET]].copy()
        df_xgb["XGB_Pred"] = xgb_preds
        await update_job(job_id, 55, "XGBoost inference complete.")

        # ── STEP 4: LSTM Inference (55→75%) ───────────────────────
        await update_job(job_id, 57, "Running LSTM inference...")
        lstm_scaler = joblib.load(os.path.join(MODELS_DIR, "lstm_scaler.pkl"))
        from tensorflow.keras.models import load_model
        lstm_model  = load_model(os.path.join(MODELS_DIR, "lstm_final_model.keras"))

        feat_cols  = [c for c in LSTM_FEATURES if c in df_clean.columns]
        target_idx = feat_cols.index(TARGET) if TARGET in feat_cols else 0
        lstm_rows  = []
        groups     = list(df_clean.groupby(["SKU_ID","Warehouse_ID"]))
        n_groups   = len(groups)

        for i, ((sku, wh), grp) in enumerate(groups):
            grp      = grp.sort_values("Date").reset_index(drop=True)
            seq_data = grp[feat_cols].values.astype(np.float32)
            if len(seq_data) < LOOKBACK:
                continue
            seqs, dates, actuals = [], [], []
            for j in range(LOOKBACK, len(seq_data)):
                seqs.append(seq_data[j-LOOKBACK:j])
                dates.append(grp["Date"].iloc[j])
                actuals.append(grp[TARGET].iloc[j] if TARGET in grp.columns else np.nan)
            if not seqs:
                continue
            X_seq   = np.array(seqs, dtype=np.float32)
            n, t, f = X_seq.shape
            X_scaled= lstm_scaler.transform(X_seq.reshape(-1, f)).reshape(n, t, f)
            y_scaled= lstm_model.predict(X_scaled, verbose=0).flatten()
            dummy   = np.zeros((len(y_scaled), f), dtype=np.float32)
            dummy[:, target_idx] = y_scaled
            y_pred  = np.clip(
                lstm_scaler.inverse_transform(dummy)[:, target_idx], 0, None
            )
            for k in range(len(dates)):
                lstm_rows.append({
                    "Date": dates[k], "SKU_ID": sku,
                    "Warehouse_ID": wh, "LSTM_Pred": float(y_pred[k]),
                    TARGET: actuals[k]
                })
            if i % max(1, n_groups // 10) == 0:
                pct = 55 + int((i / n_groups) * 20)
                await update_job(job_id, pct, f"LSTM: group {i+1}/{n_groups}...")

        df_lstm = pd.DataFrame(lstm_rows)
        await update_job(job_id, 75, "LSTM inference complete.")

        # ── STEP 5: Hybrid Blend (75→85%) ─────────────────────────
        await update_job(job_id, 76, "Blending predictions...")
        meta_model  = joblib.load(os.path.join(MODELS_DIR, "hybrid_meta_model.pkl"))
        meta_scaler = joblib.load(os.path.join(MODELS_DIR, "hybrid_meta_scaler.pkl"))

        keys      = ["Date","SKU_ID","Warehouse_ID"]
        df_merged = pd.merge(df_xgb, df_lstm[keys+["LSTM_Pred"]], on=keys, how="inner")
        df_fore   = df_clean[keys+["Demand_Forecast"]].copy()
        df_merged = pd.merge(df_merged, df_fore, on=keys, how="left")

        meta_in         = meta_scaler.transform(
            df_merged[["LSTM_Pred","XGB_Pred"]].values
        )
        df_merged["Hybrid_Pred"] = np.clip(meta_model.predict(meta_in), 0, None)
        df_merged = df_merged.rename(columns={TARGET: "Units_Sold"})

        out_cols = ["Date","SKU_ID","Warehouse_ID","Units_Sold",
                    "XGB_Pred","LSTM_Pred","Hybrid_Pred","Demand_Forecast"]
        df_merged[out_cols].to_csv(
            os.path.join(job_dir, "hybrid_predictions.csv"), index=False
        )
        await update_job(job_id, 85, "Hybrid blend complete.")

        # ── STEP 6: Inventory Optimization (85→95%) ───────────────
        await update_job(job_id, 86, "Computing inventory policy...")
        cutoff   = int(len(df_clean) * 0.70)
        df_train = df_clean.iloc[:cutoff]
        inv_rows = []

        for (sku, wh), grp in df_train.groupby(["SKU_ID","Warehouse_ID"]):
            avg_d  = float(grp["Units_Sold"].mean())
            std_d  = float(grp["Units_Sold"].std(ddof=1)) if len(grp) > 1 else 0.0
            avg_l  = float(grp["Supplier_Lead_Time_Days"].mean())
            std_l  = float(grp["Supplier_Lead_Time_Days"].std(ddof=1)) if len(grp) > 1 else 0.0
            cost   = float(grp["Unit_Cost"].mean())
            annual = avg_d * 365
            Z      = 1.645
            ss     = Z * np.sqrt(avg_l * std_d**2 + avg_d**2 * std_l**2)
            rop    = avg_d * avg_l + ss
            eoq    = np.sqrt(2 * annual * 50 / max(cost * 0.25, 0.01))
            inv_rows.append({
                "SKU_ID": sku, "Warehouse_ID": wh,
                "Safety_Stock"    : round(max(0.0, ss), 2),
                "ROP"             : round(max(0.0, rop), 2),
                "EOQ"             : round(max(1.0, eoq), 0),
                "Avg_Daily_Demand": round(avg_d, 4),
                "Avg_Lead_Time"   : round(avg_l, 4),
                "Annual_Demand"   : round(annual, 1)
            })

        pd.DataFrame(inv_rows).to_csv(
            os.path.join(job_dir, "inventory_policy.csv"), index=False
        )
        await update_job(job_id, 95, "Inventory policy computed.")

        # ── STEP 7: Business Value (95→100%) ──────────────────────
        await update_job(job_id, 96, "Computing business value metrics...")
        y_true   = df_merged["Units_Sold"].values
        y_hybrid = df_merged["Hybrid_Pred"].values
        y_base   = df_merged["Demand_Forecast"].values

        def safe_mape(actual, pred):
            mask = actual > 0
            if mask.sum() == 0:
                return 0.0
            return float(np.mean(np.abs(
                (actual[mask] - pred[mask]) / actual[mask]
            )) * 100)

        ss_res = np.sum((y_true - y_hybrid) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)

        bv = {
            "hybrid_mape"      : round(safe_mape(y_true, y_hybrid), 4),
            "baseline_mape"    : round(safe_mape(y_true, y_base), 4),
            "mape_improvement" : round(safe_mape(y_true, y_base) - safe_mape(y_true, y_hybrid), 4),
            "mae"              : round(float(np.mean(np.abs(y_true - y_hybrid))), 4),
            "rmse"             : round(float(np.sqrt(np.mean((y_true - y_hybrid)**2))), 4),
            "r2"               : round(float(1 - ss_res/ss_tot) if ss_tot > 0 else 0.0, 4),
            "total_rows"       : int(len(df_merged)),
            "unique_skus"      : int(df_merged["SKU_ID"].nunique()),
            "created_at"       : datetime.utcnow().isoformat()
        }
        with open(os.path.join(job_dir, "business_value.json"), "w") as f:
            json.dump(bv, f, indent=2)

        await update_job(job_id, 100, "Pipeline complete.", status="done")

    except Exception as e:
        from backend.app.services.job_service import update_job as _uj
        await _uj(job_id, -1, f"Pipeline failed: {str(e)}", status="failed")
        raise


# ── Feature Engineering ───────────────────────────────────────────

def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    group_keys = ["SKU_ID", "Warehouse_ID"]
    df = df.sort_values(group_keys + ["Date"]).reset_index(drop=True)
    grouped = df.groupby(group_keys)

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    df["DayOfWeek"] = df["Date"].dt.dayofweek
    df["DayOfYear"] = df["Date"].dt.dayofyear
    df["WeekOfYear"] = df["Date"].dt.isocalendar().week.astype(int)
    df["Quarter"] = df["Date"].dt.quarter
    df["Is_Weekend"] = (df["DayOfWeek"] >= 5).astype(int)
    df["Is_MonthEnd"] = df["Date"].dt.is_month_end.astype(int)
    df["Is_MonthStart"] = df["Date"].dt.is_month_start.astype(int)
    df["Is_QuarterEnd"] = df["Date"].dt.is_quarter_end.astype(int)

    df["Month_sin"] = np.sin(2 * np.pi * df["Month"] / 12)
    df["Month_cos"] = np.cos(2 * np.pi * df["Month"] / 12)
    df["DayOfWeek_sin"] = np.sin(2 * np.pi * df["DayOfWeek"] / 7)
    df["DayOfWeek_cos"] = np.cos(2 * np.pi * df["DayOfWeek"] / 7)
    df["DayOfYear_sin"] = np.sin(2 * np.pi * df["DayOfYear"] / 365)
    df["DayOfYear_cos"] = np.cos(2 * np.pi * df["DayOfYear"] / 365)
    df["WeekOfYear_sin"] = np.sin(2 * np.pi * df["WeekOfYear"] / 52)
    df["WeekOfYear_cos"] = np.cos(2 * np.pi * df["WeekOfYear"] / 52)

    for lag in [1, 2, 3, 7, 14, 21, 28, 30]:
        df[f"Units_Sold_Lag_{lag}"] = grouped["Units_Sold"].shift(lag)
    for lag in [1, 7]:
        df[f"Inventory_Lag_{lag}"] = grouped["Inventory_Level"].shift(lag)
    for lag in [1, 3, 7]:
        df[f"Promo_Lag_{lag}"] = grouped["Promotion_Flag"].shift(lag)

    for window in [7, 14, 30]:
        df[f"Rolling_Mean_{window}d"] = grouped["Units_Sold"].transform(
            lambda values, window=window: values.shift(1).rolling(window, min_periods=1).mean()
        )
        df[f"Rolling_Std_{window}d"] = grouped["Units_Sold"].transform(
            lambda values, window=window: values.shift(1).rolling(window, min_periods=2).std()
        )
        df[f"Rolling_Max_{window}d"] = grouped["Units_Sold"].transform(
            lambda values, window=window: values.shift(1).rolling(window, min_periods=1).max()
        )
        df[f"Rolling_Min_{window}d"] = grouped["Units_Sold"].transform(
            lambda values, window=window: values.shift(1).rolling(window, min_periods=1).min()
        )

    for span in [7, 14]:
        df[f"EWMA_{span}d"] = grouped["Units_Sold"].transform(
            lambda values, span=span: values.shift(1).ewm(span=span, adjust=False).mean()
        )

    df["Demand_Momentum"] = df["Rolling_Mean_7d"] / (df["Rolling_Mean_30d"] + 1e-6)

    df["Profit_Margin"] = df["Unit_Price"] - df["Unit_Cost"]
    df["Profit_Margin_Pct"] = (df["Profit_Margin"] / df["Unit_Price"].replace(0, np.nan)).round(4)
    df["Promo_x_RollingMean7"] = df["Promotion_Flag"] * df["Rolling_Mean_7d"]
    df["Promo_x_Price"] = df["Promotion_Flag"] * df["Unit_Price"]
    df["LeadTime_x_ROP"] = df["Supplier_Lead_Time_Days"] * df["Reorder_Point"]
    df["Inventory_Coverage_Days"] = df["Inventory_Level"] / (df["Rolling_Mean_7d"] + 1e-6)
    df["Inventory_Coverage_Days"] = df["Inventory_Coverage_Days"].clip(upper=365)
    df["Stock_Gap"] = df["Inventory_Level"] - df["Reorder_Point"]
    df["Below_ROP_Flag"] = (df["Inventory_Level"] < df["Reorder_Point"]).astype(int)
    df["Forecast_Error"] = df["Units_Sold"] - df["Demand_Forecast"]
    df["Forecast_Error_Abs"] = df["Forecast_Error"].abs()
    df["Recent_Promo_Window"] = grouped["Promotion_Flag"].transform(
        lambda values: values.shift(1).rolling(3, min_periods=1).max()
    ).fillna(0)

    df["Supplier_LeadTime_Std"] = df.groupby("Supplier_ID")["Supplier_Lead_Time_Days"].transform(
        lambda values: values.rolling(30, min_periods=2).std().fillna(0)
    )
    df["Inventory_Delta"] = grouped["Inventory_Level"].diff(1)
    df["Consec_Below_ROP"] = grouped["Below_ROP_Flag"].transform(
        lambda values: values * (values.groupby((values != values.shift()).cumsum()).cumcount() + 1)
    )
    df["Order_Urgency"] = (
        (df["Reorder_Point"] - df["Inventory_Level"]).clip(lower=0) * df["Supplier_Lead_Time_Days"]
    )

    for column in ["SKU_ID", "Warehouse_ID", "Supplier_ID", "Region"]:
        df[f"{column}_Enc"] = df[column].astype("category").cat.codes

    return df