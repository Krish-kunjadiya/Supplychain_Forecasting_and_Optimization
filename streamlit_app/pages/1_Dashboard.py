import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from streamlit_app.utils.data_loader import (
	load_business_value, load_hybrid_metrics, load_model_comparison,
	load_hybrid_predictions, load_feature_importance, load_sku_list
)
from streamlit_app.utils.charts import (
	forecast_timeline, model_comparison_bar,
	waterfall_chart, feature_importance_chart
)

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Results Dashboard")
st.caption("Pre-computed results from trained pipeline — all 35 output files")
st.markdown("---")

# Load data
bv   = load_business_value()
hm   = load_hybrid_metrics()
mc   = load_model_comparison()
pred = load_hybrid_predictions()
fi   = load_feature_importance()

# KPI row
st.subheader("Key Performance Indicators")
c1, c2, c3, c4, c5, c6 = st.columns(6)
bv_data = bv.get("business_value", bv)
hm_data = bv.get("hybrid_metrics", hm)
c1.metric("Hybrid MAPE",       f"{hm_data.get('MAPE', hm.get('MAPE', 0)):.3f}%")
c2.metric("R2 Score",          f"{hm_data.get('R2',   hm.get('R2',   0)):.4f}")
c3.metric("MAE",               f"{hm_data.get('MAE',  hm.get('MAE',  0)):.4f}")
c4.metric("Cost Saving",       f"${bv_data.get('cost_saving_vs_original', 0):,.0f}")
c5.metric("Saving Percentage", f"{bv_data.get('pct_cost_saving', 0):.1f}%")
c6.metric("Best Strategy",     str(bv_data.get('best_strategy', 'Hybrid')))

st.markdown("---")

# Forecast Timeline
st.subheader("Forecast Timeline")
sku_list    = load_sku_list()
selected_sku= st.selectbox("Select SKU", ["All"] + sku_list)
sku_filter  = None if selected_sku == "All" else selected_sku
st.plotly_chart(forecast_timeline(pred, sku_filter), use_container_width=True)

st.markdown("---")

# Model Comparison
st.subheader("Model Comparison")
metric = st.radio("Metric", ["MAPE", "MAE", "RMSE", "R2"], horizontal=True)
st.plotly_chart(model_comparison_bar(mc, metric), use_container_width=True)
st.dataframe(mc.style.highlight_min(subset=["MAPE","MAE","RMSE"], color="#0A2A0A")
					 .highlight_max(subset=["R2"], color="#0A2A0A"),
			 use_container_width=True)

st.markdown("---")

# Feature Importance
st.subheader("Top Feature Importance")
top_n = st.slider("Number of features to show", 5, 30, 20)
st.plotly_chart(feature_importance_chart(fi, top_n), use_container_width=True)

# Waterfall
st.subheader("Business Value Waterfall")
st.plotly_chart(waterfall_chart(bv_data), use_container_width=True)

