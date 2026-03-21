import streamlit as st
import sys, os, uuid, tempfile, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from streamlit_app.utils.pipeline_runner import run_pipeline_sync

REQUIRED_COLUMNS = [
	"Date","SKU_ID","Warehouse_ID","Supplier_ID","Region",
	"Units_Sold","Inventory_Level","Supplier_Lead_Time_Days",
	"Reorder_Point","Order_Quantity","Unit_Cost","Unit_Price",
	"Promotion_Flag","Stockout_Flag","Demand_Forecast"
]

st.set_page_config(page_title="Upload Pipeline", layout="wide")
st.title("Upload Pipeline")
st.caption("Upload a new CSV and run it through the trained models")
st.markdown("---")

uploaded = st.file_uploader("Upload supply chain CSV", type=["csv"])

if uploaded:
	import pandas as pd
	df_preview = pd.read_csv(uploaded)
	uploaded.seek(0)

	# Schema validation
	st.subheader("Schema Validation")
	missing = [c for c in REQUIRED_COLUMNS if c not in df_preview.columns]
	found   = [c for c in REQUIRED_COLUMNS if c in df_preview.columns]

	col1, col2 = st.columns(2)
	with col1:
		st.write("**Found columns**")
		for c in found:
			st.success(c)
	with col2:
		if missing:
			st.write("**Missing columns**")
			for c in missing:
				st.error(c)

	if missing:
		st.error(f"Cannot run pipeline — {len(missing)} required columns missing.")
		st.stop()

	st.success(f"Schema valid — all 15 columns found. Dataset has {len(df_preview):,} rows.")
	st.dataframe(df_preview.head(5), use_container_width=True)

	st.markdown("---")

	if st.button("Run Pipeline", type="primary"):
		job_id  = str(uuid.uuid4())
		job_dir = os.path.join(
			os.path.abspath(os.path.join(os.path.dirname(__file__), "../../uploads")),
			job_id
		)
		os.makedirs(job_dir, exist_ok=True)
		csv_path = os.path.join(job_dir, "input.csv")

		with open(csv_path, "wb") as f:
			f.write(uploaded.read())

		st.info(f"Job ID: {job_id}")
		st.warning("Pipeline is running — this takes 5 to 15 minutes depending on dataset size. Do not close this page.")

		progress_bar  = st.progress(0)
		status_text   = st.empty()
		steps = [
			(10,  "Validating schema and cleaning data"),
			(40,  "Engineering 66 features"),
			(55,  "Running XGBoost inference"),
			(75,  "Running LSTM inference"),
			(85,  "Blending predictions"),
			(95,  "Computing inventory policy"),
			(100, "Computing business value metrics"),
		]

		# Run synchronously — updates progress bar at each step
		# Since run_pipeline_sync is blocking, show intermediate steps via a thread
		import threading

		result_holder = {}

		def run():
			result_holder["result"] = run_pipeline_sync(csv_path, job_id)

		thread = threading.Thread(target=run)
		thread.start()

		# Poll job_service while pipeline runs
		from backend.app.services.job_service import get_job
		while thread.is_alive():
			job = get_job(job_id)
			if job:
				pct  = max(0, job["progress"])
				step = job["current_step"]
				progress_bar.progress(min(pct, 100))
				status_text.text(step)
			time.sleep(2)

		thread.join()
		job = result_holder.get("result") or get_job(job_id)

		if job and job.get("status") == "done":
			progress_bar.progress(100)
			status_text.text("Pipeline complete.")
			st.success("Pipeline complete. Navigate to the Results page to view outputs.")
			st.info(f"Your Job ID: {job_id}")
			st.session_state["last_job_id"] = job_id
		else:
			error = job.get("error", "Unknown error") if job else "Unknown error"
			st.error(f"Pipeline failed: {error}")

