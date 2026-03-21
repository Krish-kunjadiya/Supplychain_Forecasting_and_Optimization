import os, json
import pandas as pd

_ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
OUTPUTS  = os.path.join(_ROOT, "outputs")
MODELS   = os.path.join(_ROOT, "models")
UPLOADS  = os.path.join(_ROOT, "uploads")

def load_business_value():
	with open(os.path.join(OUTPUTS, "business_value.json")) as f:
		return json.load(f)

def load_hybrid_metrics():
	with open(os.path.join(OUTPUTS, "hybrid_metrics.json")) as f:
		return json.load(f)

def load_model_comparison():
	return pd.read_csv(os.path.join(OUTPUTS, "all_model_comparison.csv"))

def load_hybrid_predictions():
	df = pd.read_csv(os.path.join(OUTPUTS, "hybrid_predictions.csv"), parse_dates=["Date"])
	return df

def load_inventory_policy():
	return pd.read_csv(os.path.join(OUTPUTS, "inventory_policy.csv"))

def load_policy_comparison():
	return pd.read_csv(os.path.join(OUTPUTS, "policy_comparison.csv"))

def load_simulation_results():
	return pd.read_csv(os.path.join(OUTPUTS, "simulation_results.csv"))

def load_sku_performance():
	lstm = pd.read_csv(os.path.join(OUTPUTS, "lstm_sku_performance.csv"))
	xgb  = pd.read_csv(os.path.join(OUTPUTS, "xgb_sku_performance.csv"))
	return lstm, xgb

def load_feature_importance():
	return pd.read_csv(os.path.join(OUTPUTS, "xgb_feature_importance.csv"))

def load_feature_registry():
	with open(os.path.join(OUTPUTS, "feature_registry.json")) as f:
		return json.load(f)

def load_sku_list():
	df = load_hybrid_predictions()
	return sorted(df["SKU_ID"].unique().tolist())

def load_sku_data(sku_id):
	df = load_hybrid_predictions()
	return df[df["SKU_ID"] == sku_id].sort_values("Date")

def load_job_results(job_id):
	job_dir = os.path.join(UPLOADS, job_id)
	results = {}
	bv_path = os.path.join(job_dir, "business_value.json")
	hp_path = os.path.join(job_dir, "hybrid_predictions.csv")
	iv_path = os.path.join(job_dir, "inventory_policy.csv")
	if os.path.exists(bv_path):
		with open(bv_path) as f:
			results["business_value"] = json.load(f)
	if os.path.exists(hp_path):
		results["predictions"] = pd.read_csv(hp_path, parse_dates=["Date"])
	if os.path.exists(iv_path):
		results["inventory"]   = pd.read_csv(iv_path)
	return results

def list_completed_jobs():
	if not os.path.exists(UPLOADS):
		return []
	jobs = []
	for job_id in os.listdir(UPLOADS):
		bv = os.path.join(UPLOADS, job_id, "business_value.json")
		if os.path.exists(bv):
			jobs.append(job_id)
	return jobs
