import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from streamlit_app.utils.data_loader import load_sku_list, load_sku_data, load_sku_performance
from streamlit_app.utils.charts import forecast_timeline

st.set_page_config(page_title="SKU Explorer", layout="wide")
st.title("SKU Explorer")
st.caption("Per-SKU forecast charts and performance metrics")
st.markdown("---")

sku_list        = load_sku_list()
lstm_df, xgb_df = load_sku_performance()

search      = st.text_input("Search SKU", placeholder="e.g. SKU_1")
filtered    = [s for s in sku_list if search.lower() in s.lower()] if search else sku_list
selected    = st.selectbox("Select SKU", filtered)

if selected:
	sku_data = load_sku_data(selected)

	# Metrics
	c1, c2, c3, c4 = st.columns(4)
	c1.metric("Data Points", len(sku_data))

	lstm_row = lstm_df[lstm_df.iloc[:,0] == selected] if not lstm_df.empty else None
	xgb_row  = xgb_df[xgb_df.iloc[:,0]  == selected] if not xgb_df.empty  else None

	mape_col = "MAPE" if "MAPE" in lstm_df.columns else lstm_df.columns[1] if len(lstm_df.columns) > 1 else None
	if mape_col and lstm_row is not None and not lstm_row.empty:
		c2.metric("LSTM MAPE", f"{lstm_row.iloc[0][mape_col]:.3f}%")
	if mape_col and xgb_row is not None and not xgb_row.empty:
		c3.metric("XGBoost MAPE", f"{xgb_row.iloc[0][mape_col]:.3f}%")

	# Determine winner
	if mape_col and lstm_row is not None and xgb_row is not None and not lstm_row.empty and not xgb_row.empty:
		winner = "XGBoost" if xgb_row.iloc[0][mape_col] < lstm_row.iloc[0][mape_col] else "LSTM"
		c4.metric("Best Model", winner)

	st.markdown("---")

	# Forecast chart
	st.subheader(f"Forecast vs Actual — {selected}")
	st.plotly_chart(forecast_timeline(sku_data, selected), use_container_width=True)

	# Raw data
	with st.expander("Show raw forecast data"):
		st.dataframe(sku_data.tail(100), use_container_width=True)

