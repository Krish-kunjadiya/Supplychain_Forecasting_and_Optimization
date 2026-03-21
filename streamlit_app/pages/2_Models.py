import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from streamlit_app.utils.data_loader import load_model_comparison, load_sku_performance
from streamlit_app.utils.charts import model_comparison_bar, sku_mape_scatter

st.set_page_config(page_title="Model Analysis", layout="wide")
st.title("Model Analysis")
st.caption("All 7 models compared across 4 metrics")
st.markdown("---")

mc          = load_model_comparison()
lstm_df, xgb_df = load_sku_performance()

# Best per metric
st.subheader("Best Model Per Metric")
c1, c2, c3, c4 = st.columns(4)
for col, metric, asc in [(c1,"MAPE",True),(c2,"MAE",True),(c3,"RMSE",True),(c4,"R2",False)]:
	best_row = mc.sort_values(metric, ascending=asc).iloc[0]
	col.metric(f"Best {metric}", f"{best_row[metric]:.4f}", best_row["Model"])

st.markdown("---")

# Bar chart per metric
st.subheader("Comparison Charts")
cols = st.columns(2)
for i, metric in enumerate(["MAPE", "MAE", "RMSE", "R2"]):
	with cols[i % 2]:
		st.plotly_chart(model_comparison_bar(mc, metric), use_container_width=True)

st.markdown("---")

# Full table
st.subheader("Full Results Table")
st.dataframe(
	mc.sort_values("MAPE").style
	  .highlight_min(subset=["MAPE","MAE","RMSE"], color="#14532D")
	  .highlight_max(subset=["R2"], color="#14532D"),
	use_container_width=True
)

st.markdown("---")

# SKU scatter
st.subheader("LSTM vs XGBoost Per SKU")
st.caption("Points below the diagonal line mean XGBoost won for that SKU")
st.plotly_chart(sku_mape_scatter(lstm_df, xgb_df), use_container_width=True)

st.markdown("---")

# Strategy explainer
st.subheader("Blend Strategy Explanations")
c1, c2 = st.columns(2)
with c1:
	st.info("**Simple Average**\n\n50% LSTM + 50% XGBoost. No intelligence — just averages both predictions equally.")
	st.info("**Meta-Learner**\n\nRidge regression trained on LSTM and XGBoost outputs. Learns the optimal combination from validation data.")
with c2:
	st.info("**Weighted Blend**\n\nFixed weights optimized on the validation set. Better than simple average but static per dataset.")
	st.info("**Dynamic Per-SKU**\n\nInverse-MAE weights computed per SKU. The model with lower validation error automatically gets higher weight.")

