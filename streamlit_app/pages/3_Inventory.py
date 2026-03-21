import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from streamlit_app.utils.data_loader import (
	load_policy_comparison, load_inventory_policy, load_sku_list
)
from streamlit_app.utils.charts import policy_cost_chart, inventory_sku_chart

st.set_page_config(page_title="Inventory Policy", layout="wide")
st.title("Inventory Policy")
st.caption("3-policy simulation — Original vs Baseline vs Hybrid")
st.markdown("---")

policy_df = load_policy_comparison()
inv_df    = load_inventory_policy()

# Policy summary
st.subheader("Policy Cost Summary")
c1, c2, c3 = st.columns(3)
for col, policy, color in [(c1,"Original","gray"),(c2,"Baseline","orange"),(c3,"Hybrid","green")]:
	subset = policy_df[policy_df["Policy"] == policy] if "Policy" in policy_df.columns else policy_df
	total  = subset["Total_Cost"].sum() if "Total_Cost" in subset.columns else 0
	stockout= subset["Stockout_Days"].sum() if "Stockout_Days" in subset.columns else 0
	col.metric(f"{policy} Policy Total Cost", f"${total:,.0f}", f"Stockout days: {stockout}")

st.plotly_chart(policy_cost_chart(policy_df), use_container_width=True)

st.markdown("---")

# Per SKU inventory
st.subheader("Per-SKU Inventory Policy (ROP / EOQ / Safety Stock)")
sku_list     = sorted(inv_df["SKU_ID"].unique().tolist()) if "SKU_ID" in inv_df.columns else []
selected_sku = st.selectbox("Select SKU", sku_list)
if selected_sku:
	st.plotly_chart(inventory_sku_chart(inv_df, selected_sku), use_container_width=True)
	sku_data = inv_df[inv_df["SKU_ID"] == selected_sku]
	st.dataframe(sku_data, use_container_width=True)

st.markdown("---")

# Full policy table
st.subheader("Full Policy Comparison Table")
filter_policy = st.multiselect("Filter by Policy", options=policy_df["Policy"].unique().tolist() if "Policy" in policy_df.columns else [], default=policy_df["Policy"].unique().tolist() if "Policy" in policy_df.columns else [])
filtered = policy_df[policy_df["Policy"].isin(filter_policy)] if filter_policy else policy_df
st.dataframe(filtered, use_container_width=True)

