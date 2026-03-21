import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

BG       = "#0A0F1E"
CARD_BG  = "#132035"
BLUE     = "#1F78FF"
CYAN     = "#22D3EE"
GREEN    = "#00C853"
YELLOW   = "#FFB300"
PURPLE   = "#A78BFA"
RED      = "#EF4444"
LGRAY    = "#94A3B8"

LAYOUT = dict(
	paper_bgcolor=BG,
	plot_bgcolor=CARD_BG,
	font=dict(color=LGRAY, family="monospace"),
	margin=dict(l=40, r=20, t=40, b=40),
	legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=LGRAY)),
)

def forecast_timeline(df, sku_id=None):
	if sku_id:
		df = df[df["SKU_ID"] == sku_id]
	df = df.sort_values("Date").head(500)
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=df["Date"], y=df["Units_Sold"],  name="Actual",   line=dict(color=BLUE,   width=2)))
	fig.add_trace(go.Scatter(x=df["Date"], y=df["Hybrid_Pred"], name="Hybrid",   line=dict(color=CYAN,   width=2)))
	fig.add_trace(go.Scatter(x=df["Date"], y=df["XGB_Pred"],    name="XGBoost",  line=dict(color=YELLOW, width=1, dash="dot")))
	if "LSTM_Pred" in df.columns:
		fig.add_trace(go.Scatter(x=df["Date"], y=df["LSTM_Pred"], name="LSTM",   line=dict(color=PURPLE, width=1, dash="dot")))
	fig.update_layout(**LAYOUT, title=f"Forecast Timeline{' — ' + sku_id if sku_id else ''}", xaxis=dict(gridcolor="#1E293B"), yaxis=dict(gridcolor="#1E293B"))
	return fig

def model_comparison_bar(df, metric="MAPE"):
	df_sorted = df.sort_values(metric, ascending=(metric != "R2"))
	colors    = [GREEN if i == 0 else BLUE for i in range(len(df_sorted))]
	fig = go.Figure(go.Bar(
		x=df_sorted["Model"], y=df_sorted[metric],
		marker_color=colors,
		text=df_sorted[metric].round(4).astype(str),
		textposition="outside",
	))
	fig.update_layout(**LAYOUT, title=f"Model Comparison — {metric}", xaxis_tickangle=-30, yaxis=dict(gridcolor="#1E293B"))
	return fig

def waterfall_chart(bv):
	items  = ["Ordering Cost", "Holding Cost", "Stockout Reduction", "Net Saving"]
	values = [
		-bv.get("avg_inventory_change", 0) * 0.1,
		bv.get("cost_saving_vs_original", 0) * 0.6,
		bv.get("cost_saving_vs_original", 0) * 0.4,
		bv.get("cost_saving_vs_original", 0),
	]
	colors = [GREEN if v >= 0 else RED for v in values]
	fig = go.Figure(go.Bar(x=items, y=values, marker_color=colors, text=[f"${v:,.0f}" for v in values], textposition="outside"))
	fig.update_layout(**LAYOUT, title="Business Value Waterfall", yaxis=dict(gridcolor="#1E293B"))
	return fig

def policy_cost_chart(df):
	policies = df["Policy"].unique() if "Policy" in df.columns else []
	if len(policies) == 0:
		return go.Figure()
	summary = df.groupby("Policy")["Total_Cost"].sum().reset_index()
	color_map = {"Original": LGRAY, "Baseline": YELLOW, "Hybrid": GREEN}
	colors = [color_map.get(p, BLUE) for p in summary["Policy"]]
	fig = go.Figure(go.Bar(
		x=summary["Policy"], y=summary["Total_Cost"],
		marker_color=colors,
		text=summary["Total_Cost"].apply(lambda v: f"${v:,.0f}"),
		textposition="outside",
	))
	fig.update_layout(**LAYOUT, title="Total Cost by Policy", yaxis=dict(gridcolor="#1E293B"))
	return fig

def feature_importance_chart(df, top_n=20):
	col = "Gain" if "Gain" in df.columns else df.columns[1]
	df_top = df.nlargest(top_n, col)
	fig = go.Figure(go.Bar(
		x=df_top[col], y=df_top.iloc[:, 0],
		orientation="h",
		marker_color=CYAN,
	))
	fig.update_layout(**LAYOUT, title=f"Top {top_n} Features by {col}", margin=dict(l=180, r=20, t=40, b=40), yaxis=dict(gridcolor="#1E293B"))
	return fig

def sku_mape_scatter(lstm_df, xgb_df):
	key_col = "SKU_ID" if "SKU_ID" in lstm_df.columns else lstm_df.columns[0]
	mape_col= "MAPE"   if "MAPE"   in lstm_df.columns else "mape"
	merged  = lstm_df[[key_col, mape_col]].rename(columns={mape_col:"LSTM_MAPE"}).merge(
		xgb_df[[key_col, mape_col]].rename(columns={mape_col:"XGB_MAPE"}), on=key_col
	)
	merged["Winner"] = merged.apply(lambda r: "XGBoost" if r["XGB_MAPE"] < r["LSTM_MAPE"] else "LSTM", axis=1)
	fig = px.scatter(
		merged, x="LSTM_MAPE", y="XGB_MAPE", color="Winner", text=key_col,
		color_discrete_map={"XGBoost": YELLOW, "LSTM": PURPLE},
	)
	fig.add_shape(type="line", x0=0, y0=0, x1=merged["LSTM_MAPE"].max(), y1=merged["LSTM_MAPE"].max(),
				  line=dict(color=LGRAY, dash="dash"))
	fig.update_layout(**LAYOUT, title="LSTM vs XGBoost MAPE per SKU (below diagonal = XGB wins)")
	return fig

def inventory_sku_chart(inv_df, sku_id):
	df = inv_df[inv_df["SKU_ID"] == sku_id] if "SKU_ID" in inv_df.columns else inv_df
	if df.empty:
		return go.Figure()
	metrics = ["Safety_Stock", "ROP", "EOQ"]
	values  = [df[m].mean() if m in df.columns else 0 for m in metrics]
	colors  = [YELLOW, BLUE, GREEN]
	fig = go.Figure(go.Bar(x=metrics, y=values, marker_color=colors, text=[f"{v:.1f}" for v in values], textposition="outside"))
	fig.update_layout(**LAYOUT, title=f"Inventory Policy — {sku_id}", yaxis=dict(gridcolor="#1E293B"))
	return fig

def pipeline_progress_chart(progress):
	fig = go.Figure(go.Bar(
		x=[progress], y=["Progress"],
		orientation="h",
		marker_color=CYAN,
		text=[f"{progress}%"],
		textposition="inside",
	))
	fig.update_layout(**LAYOUT, xaxis=dict(range=[0, 100], gridcolor="#1E293B"), height=80, margin=dict(l=10,r=10,t=10,b=10))
	return fig
