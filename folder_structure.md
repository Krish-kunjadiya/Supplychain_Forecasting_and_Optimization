# Project Folder Structure

```text
Supplychain_Forecasting_and_Optimization/
├── app
│   ├── dashboard
│   │   └── page.js
│   ├── inventory
│   │   └── page.js
│   ├── models
│   │   └── page.js
│   ├── predict
│   │   └── page.js
│   ├── results
│   │   └── [jobId]
│   │       └── page.js
│   ├── sku
│   │   └── page.js
│   ├── upload
│   │   └── page.js
│   └── page.js
├── backend
│   ├── app
│   │   ├── routers
│   │   │   ├── dashboard.py
│   │   │   └── pipeline.py
│   │   ├── services
│   │   │   ├── data_service.py
│   │   │   ├── job_service.py
│   │   │   ├── pipeline_service.py
│   │   │   └── test_data_service.py
│   │   └── main.py
│   ├── test_dashboard_router.py
│   ├── test_job_service.py
│   └── test_pipeline_router.py
├── components
│   ├── dashboard
│   │   ├── ForecastTimeline.js
│   │   ├── KPICards.js
│   │   ├── MiscCharts.js
│   │   └── ModelComparisonChart.js
│   └── upload
│       ├── DropZone.js
│       ├── JobProgressBar.js
│       └── SchemaValidator.js
├── data
│   └── supply_chain_dataset1.csv
├── frontend
│   ├── app
│   │   ├── dashboard
│   │   │   └── page.js
│   │   ├── inventory
│   │   │   └── page.js
│   │   ├── models
│   │   │   └── page.js
│   │   ├── predict
│   │   │   └── page.js
│   │   ├── results
│   │   │   └── [jobId]
│   │   │       └── page.js
│   │   ├── sku
│   │   │   └── page.js
│   │   ├── upload
│   │   │   └── page.js
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.js
│   │   └── page.js
│   ├── components
│   │   └── layout
│   │       ├── Navbar.js
│   │       └── Sidebar.js
│   ├── lib
│   │   └── api.js
│   ├── public
│   │   ├── next.svg
│   │   └── vercel.svg
│   ├── store
│   │   └── dashboardStore.js
│   ├── .gitignore
│   ├── README.md
│   ├── build_dashboard.py
│   ├── build_pages.py
│   ├── build_upload.py
│   ├── jsconfig.json
│   ├── next.config.mjs
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.mjs
│   ├── scaffold.py
│   └── tailwind.config.js
├── uploads
│   └── f09258ac-de99-426f-9fa0-b996ff73a5de
│       ├── business_value.json
│       ├── dummy.csv
│       ├── features_lstm.csv
│       ├── features_xgb.csv
│       ├── hybrid_predictions.csv
│       └── input.csv
├── .gitattributes
├── .gitignore
├── 01_data_loading_and_validation.ipynb
├── 02_eda.ipynb
├── 03_feature_engineering.ipynb
├── 04_lstm_model.ipynb
├── 05_xgboost_model.ipynb
├── 06_hybrid_model.ipynb
├── 07_inventory_optimization.ipynb
├── 08_results_dashboard.ipynb
├── LICENSE
├── README.md
├── all_model_comparison.csv
├── business_value.json
├── dashboard_architecture.png
├── dashboard_hybrid_deepdive.png
├── dashboard_inventory_impact.png
├── dashboard_kpi.png
├── dashboard_model_comparison.png
├── dashboard_sku_winners.png
├── dashboard_waterfall.png
├── dummy.csv
├── feature_registry.json
├── features_lstm.csv
├── features_xgboost.csv
├── generate_tree.py
├── hybrid_meta_model.pkl
├── hybrid_meta_scaler.pkl
├── hybrid_metrics.json
├── hybrid_predictions.csv
├── inventory_policy.csv
├── lstm_best_model.keras
├── lstm_final_model.keras
├── lstm_metrics.json
├── lstm_scaler.pkl
├── lstm_sku_performance.csv
├── lstm_test_predictions.csv
├── policy_comparison.csv
├── simulation_results.csv
├── sku_dynamic_weights.csv
├── supply_chain_dashboard.html
├── supply_chain_eda_ready.csv
├── supply_chain_validated.csv
├── xgb_best_params.json
├── xgb_feature_importance.csv
├── xgb_final_model.pkl
├── xgb_metrics.json
├── xgb_permutation_importance.csv
├── xgb_sku_performance.csv
└── xgb_test_predictions.csv
```
