import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from streamlit_app.utils.data_loader import load_job_results, list_completed_jobs
from streamlit_app.utils.charts import forecast_timeline, waterfall_chart, policy_cost_chart

st.set_page_config(page_title="Pipeline Results", layout="wide")
st.title("Pipeline Results")
st.caption("View results from a completed upload job")
st.markdown("---")

completed = list_completed_jobs()

if not completed:
	st.warning("No completed jobs found. Upload a dataset on the Upload Pipeline page first.")
	st.stop()

default_job = st.session_state.get("last_job_id", completed[-1])
default_idx = completed.index(default_job) if default_job in completed else 0
selected_job = st.selectbox("Select Job", completed, index=default_idx)

if selected_job:
	results = load_job_results(selected_job)
	st.caption(f"Job ID: {selected_job}")

	if not results:
		st.error("No results found for this job.")
		st.stop()

	bv   = results.get("business_value", {})
	pred = results.get("predictions")
	inv  = results.get("inventory")

	# KPI metrics
	if bv:
		st.subheader("Key Metrics")
		c1, c2, c3, c4 = st.columns(4)
		c1.metric("Hybrid MAPE",     f"{bv.get('hybrid_mape', 0):.4f}%")
		c2.metric("Baseline MAPE",   f"{bv.get('baseline_mape', 0):.4f}%")
		c3.metric("R2 Score",        f"{bv.get('r2', 0):.4f}")
		c4.metric("MAPE Improvement",f"{bv.get('mape_improvement', 0):.4f}%")

		c1, c2, c3, c4 = st.columns(4)
		c1.metric("MAE",         f"{bv.get('mae', 0):.4f}")
		c2.metric("RMSE",        f"{bv.get('rmse', 0):.4f}")
		c3.metric("Total Rows",  f"{bv.get('total_rows', 0):,}")
		c4.metric("Unique SKUs", f"{bv.get('unique_skus', 0)}")

	st.markdown("---")

	# Forecast chart
	if pred is not None:
		st.subheader("Forecast Timeline")
		skus = sorted(pred["SKU_ID"].unique().tolist()) if "SKU_ID" in pred.columns else []
		sel  = st.selectbox("Select SKU", ["All"] + skus)
		sku_filter = None if sel == "All" else sel
		st.plotly_chart(forecast_timeline(pred, sku_filter), use_container_width=True)

		with st.expander("Show raw predictions"):
			st.dataframe(pred.head(200), use_container_width=True)

	st.markdown("---")

	# Inventory
	if inv is not None:
		st.subheader("Inventory Policy")
		st.dataframe(inv, use_container_width=True)

