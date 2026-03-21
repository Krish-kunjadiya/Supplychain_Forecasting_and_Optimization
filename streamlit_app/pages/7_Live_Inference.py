import streamlit as st
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

st.set_page_config(page_title="Live Inference", layout="wide")
st.title("Live Inference")
st.caption("Real-time single-SKU prediction from trained models")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
	st.subheader("Input Features")

	sku_id       = st.text_input("SKU ID",        value="SKU_1")
	warehouse_id = st.text_input("Warehouse ID",  value="WH_1")
	strategy     = st.selectbox("Blend Strategy", ["meta", "dynamic", "simple", "weighted"])

	st.markdown("**Lag Features**")
	c1, c2, c3 = st.columns(3)
	lag1  = c1.number_input("Units Sold Lag 1d",  value=45.0)
	lag7  = c2.number_input("Units Sold Lag 7d",  value=42.0)
	lag30 = c3.number_input("Units Sold Lag 30d", value=40.0)

	st.markdown("**Rolling Features**")
	c1, c2, c3 = st.columns(3)
	rm7  = c1.number_input("Rolling Mean 7d",  value=43.0)
	rm30 = c2.number_input("Rolling Mean 30d", value=41.0)
	rs7  = c3.number_input("Rolling Std 7d",   value=3.2)

	st.markdown("**Inventory and Supplier**")
	c1, c2 = st.columns(2)
	inv_level = c1.number_input("Inventory Level",    value=320.0)
	lead_time = c2.number_input("Lead Time (days)",   value=7.0)
	rop       = c1.number_input("Reorder Point",      value=100.0)
	unit_cost = c2.number_input("Unit Cost ($)",      value=25.0)
	unit_price= c1.number_input("Unit Price ($)",     value=45.0)
	promo     = c2.number_input("Promotion Flag 0/1", value=0.0, min_value=0.0, max_value=1.0, step=1.0)
	demand_fc = c1.number_input("Demand Forecast",    value=44.0)

	run = st.button("Run Prediction", type="primary")

with col2:
	st.subheader("Results")

	if run:
		with st.spinner("Loading models and running inference..."):
			try:
				import joblib
				from streamlit_app.utils.data_loader import load_feature_registry, MODELS

				registry     = load_feature_registry()
				XGB_FEATURES = registry["xgboost_features"]

				xgb_model    = joblib.load(os.path.join(MODELS, "xgb_final_model.pkl"))
				meta_model   = joblib.load(os.path.join(MODELS, "hybrid_meta_model.pkl"))
				meta_scaler  = joblib.load(os.path.join(MODELS, "hybrid_meta_scaler.pkl"))

				features = {
					"units_sold_lag_1"        : lag1,
					"Units_Sold_Lag_1"        : lag1,
					"units_sold_lag_7"        : lag7,
					"Units_Sold_Lag_7"        : lag7,
					"units_sold_lag_30"       : lag30,
					"Units_Sold_Lag_30"       : lag30,
					"rolling_mean_7d"         : rm7,
					"Rolling_Mean_7d"         : rm7,
					"rolling_mean_30d"        : rm30,
					"Rolling_Mean_30d"        : rm30,
					"rolling_std_7d"          : rs7,
					"Rolling_Std_7d"          : rs7,
					"inventory_level"         : inv_level,
					"Inventory_Level"         : inv_level,
					"supplier_lead_time_days" : lead_time,
					"Supplier_Lead_Time_Days" : lead_time,
					"reorder_point"           : rop,
					"Reorder_Point"           : rop,
					"unit_cost"               : unit_cost,
					"Unit_Cost"               : unit_cost,
					"unit_price"              : unit_price,
					"Unit_Price"              : unit_price,
					"promotion_flag"          : promo,
					"Promotion_Flag"          : promo,
					"demand_forecast"         : demand_fc,
					"Demand_Forecast"         : demand_fc,
				}

				feat_vec = np.array(
					[features.get(f, 0.0) for f in XGB_FEATURES],
					dtype=np.float32
				).reshape(1, -1)

				xgb_pred  = float(np.clip(xgb_model.predict(feat_vec)[0], 0, None))
				lstm_pred = xgb_pred  # LSTM not available for single inference

				if strategy == "simple":
					hybrid = (xgb_pred + lstm_pred) / 2
				elif strategy == "weighted":
					hybrid = 0.3 * lstm_pred + 0.7 * xgb_pred
				else:
					meta_in = meta_scaler.transform([[lstm_pred, xgb_pred]])
					hybrid  = float(np.clip(meta_model.predict(meta_in)[0], 0, None))

				# Inventory policy
				Z  = 1.645
				d  = rm30
				sd = rs7
				L  = lead_time
				sL = 1.5
				ss = Z * np.sqrt(L * sd**2 + d**2 * sL**2)
				computed_rop = d * L + ss
				annual = d * 365
				eoq = np.sqrt(2 * annual * 50 / max(unit_cost * 0.25, 0.01))

				st.success("Prediction complete")

				st.markdown("**Demand Predictions**")
				pc1, pc2, pc3 = st.columns(3)
				pc1.metric("XGBoost",     f"{xgb_pred:.4f}")
				pc2.metric("LSTM (proxy)",f"{lstm_pred:.4f}")
				pc3.metric("Hybrid",      f"{hybrid:.4f}", delta=f"Strategy: {strategy}")

				st.markdown("---")
				st.markdown("**Computed Inventory Policy**")
				ic1, ic2, ic3 = st.columns(3)
				ic1.metric("Safety Stock", f"{max(0, ss):.2f}")
				ic2.metric("Reorder Point",f"{max(0, computed_rop):.2f}")
				ic3.metric("EOQ",          f"{max(1, eoq):.0f}")

			except Exception as e:
				st.error(f"Inference failed: {str(e)}")
	else:
		st.info("Fill in features on the left and click Run Prediction.")
