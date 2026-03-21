import streamlit as st

st.set_page_config(
	page_title="Supply Chain Optimization System",
	page_icon=None,
	layout="wide",
	initial_sidebar_state="expanded",
)

st.markdown("""
<style>
	.stApp { background-color: #0A0F1E; color: #FFFFFF; }
	.metric-card {
		background: #132035;
		border: 1px solid #1E293B;
		border-radius: 8px;
		padding: 16px;
		text-align: center;
	}
	.stMetric label { color: #94A3B8 !important; font-size: 12px !important; }
	.stMetric [data-testid="stMetricValue"] { color: #22D3EE !important; font-family: monospace !important; }
</style>
""", unsafe_allow_html=True)

st.title("Intelligent Supply Chain Optimization System")
st.caption("AI-Powered Demand Forecasting and Dynamic Inventory Policy")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
	st.markdown("""
	### What This System Does

	This system solves the Supply Chain Paradox — the constant tension between
	overstock and stockout. It uses a two-phase approach:

	**Phase 1 — The Brain (Forecasting)**
	Hybrid LSTM and XGBoost ensemble predicts daily demand per SKU and Warehouse.

	**Phase 2 — The Action (Optimization)**
	Forecasts are converted into dynamic Reorder Points, Economic Order Quantities,
	and Safety Stock levels using operations research formulas.
	""")

with col2:
	st.markdown("### Project Stats")
	c1, c2 = st.columns(2)
	c1.metric("Training Rows",    "~90,000")
	c2.metric("Unique SKUs",      "50")
	c1.metric("Hybrid MAPE",      "0.74%")
	c2.metric("R2 Score",         "0.9998")
	c1.metric("Cost Saving",      "$104,446")
	c2.metric("MAPE Improvement", "16.8%")

st.markdown("---")
st.markdown("""
### Navigate Using the Sidebar

| Page | Description |
|---|---|
| Dashboard | Pre-computed results from trained pipeline |
| Models | 7-model comparison with sortable metrics |
| Inventory | 3-policy simulation and cost comparison |
| SKU Explorer | Per-SKU forecast charts and metrics |
| Upload Pipeline | Run new data through trained models |
| Results | View results from a past upload job |
| Live Inference | Real-time single-SKU prediction |

### Team

**Krish Kunjadiya** (Krish-kunjadiya) - Project Lead, ML Architecture, FastAPI, Frontend

**Khushi** (khushi911911) - Data Analysis, Feature Engineering, Testing, Documentation

Dept. of Artificial Intelligence and Machine Learning, CSPIT CHARUSAT
""")
