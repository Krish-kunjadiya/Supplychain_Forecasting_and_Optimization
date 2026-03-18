"use client";
import { useState } from "react";
import { predictSingle, inventoryPolicy } from "@/lib/api";

const DEFAULT_FORM = {
  sku_id: "SKU_1",
  warehouse_id: "WH_1",
  units_sold_lag_1: 45,
  units_sold_lag_7: 42,
  units_sold_lag_30: 40,
  rolling_mean_7d: 43,
  rolling_mean_30d: 41,
  rolling_std_7d: 3.2,
  inventory_level: 320,
  supplier_lead_time_days: 7,
  reorder_point: 100,
  unit_cost: 25,
  unit_price: 45,
  promotion_flag: 0,
  demand_forecast: 44,
  blend_strategy: "meta",
};

const FIELD_META = [
  { key:"sku_id",                   label:"SKU ID",               type:"text"   },
  { key:"warehouse_id",             label:"Warehouse ID",          type:"text"   },
  { key:"units_sold_lag_1",         label:"Units Sold (lag 1d)",   type:"number" },
  { key:"units_sold_lag_7",         label:"Units Sold (lag 7d)",   type:"number" },
  { key:"units_sold_lag_30",        label:"Units Sold (lag 30d)",  type:"number" },
  { key:"rolling_mean_7d",          label:"Rolling Mean 7d",       type:"number" },
  { key:"rolling_mean_30d",         label:"Rolling Mean 30d",      type:"number" },
  { key:"rolling_std_7d",           label:"Rolling Std 7d",        type:"number" },
  { key:"inventory_level",          label:"Inventory Level",       type:"number" },
  { key:"supplier_lead_time_days",  label:"Lead Time (days)",      type:"number" },
  { key:"reorder_point",            label:"Reorder Point",         type:"number" },
  { key:"unit_cost",                label:"Unit Cost ($)",         type:"number" },
  { key:"unit_price",               label:"Unit Price ($)",        type:"number" },
  { key:"promotion_flag",           label:"Promotion Flag (0/1)",  type:"number" },
  { key:"demand_forecast",          label:"Demand Forecast",       type:"number" },
];

const STRATEGIES = [
  { value:"meta",     label:"Meta-Learner (default)" },
  { value:"dynamic",  label:"Dynamic Per-SKU"        },
  { value:"simple",   label:"Simple Average"         },
  { value:"weighted", label:"Weighted Blend"         },
];

export default function PredictPage() {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [result, setResult] = useState(null);
  const [invResult, setInv] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function handleChange(key, val) {
    setForm(f => ({ ...f, [key]: key === "sku_id" || key === "warehouse_id" ? val : parseFloat(val) || val }));
  }

  async function handleSubmit() {
    setLoading(true);
    setError(null);
    setResult(null);
    setInv(null);

    try {
      // Build request matching existing /predict/single schema
      const predBody = {
        sku_id          : form.sku_id,
        warehouse_id    : form.warehouse_id,
        features        : {
          units_sold_lag_1        : form.units_sold_lag_1,
          units_sold_lag_7        : form.units_sold_lag_7,
          units_sold_lag_30       : form.units_sold_lag_30,
          rolling_mean_7d         : form.rolling_mean_7d,
          rolling_mean_30d        : form.rolling_mean_30d,
          rolling_std_7d          : form.rolling_std_7d,
          inventory_level         : form.inventory_level,
          supplier_lead_time_days : form.supplier_lead_time_days,
          reorder_point           : form.reorder_point,
          unit_cost               : form.unit_cost,
          unit_price              : form.unit_price,
          promotion_flag          : form.promotion_flag,
          demand_forecast         : form.demand_forecast,
        },
        blend_strategy: form.blend_strategy,
      };

      const predRes = await predictSingle(predBody);
      setResult(predRes);

      // Auto-fetch inventory policy for this SKU
      const invBody = {
        sku_id                  : form.sku_id,
        warehouse_id            : form.warehouse_id,
        avg_daily_demand        : form.rolling_mean_30d,
        std_daily_demand        : form.rolling_std_7d,
        avg_lead_time           : form.supplier_lead_time_days,
        std_lead_time           : 1.5,
        avg_unit_cost           : form.unit_cost,
        service_level           : 0.95,
        ordering_cost           : 50,
        holding_rate            : 0.25,
      };
      const invRes = await inventoryPolicy(invBody);
      setInv(invRes);

    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#0A0F1E] text-white p-6 space-y-6 max-w-4xl mx-auto">

      <div>
        <h1 className="text-2xl font-bold">Live Inference</h1>
        <p className="text-sm text-gray-400 mt-1">
          Enter feature values to get a real-time prediction from the trained models.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Form */}
        <div className="rounded-xl border border-white/10 bg-white/5 p-5 space-y-4">
          <h2 className="text-sm font-semibold text-gray-300">Input Features</h2>

          {/* Blend strategy */}
          <div>
            <label className="text-xs text-gray-400 block mb-1">Blend Strategy</label>
            <select
              value={form.blend_strategy}
              onChange={e => handleChange("blend_strategy", e.target.value)}
              className="w-full text-xs bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-gray-300 focus:outline-none focus:border-blue-500/50"
            >
              {STRATEGIES.map(s => (
                <option key={s.value} value={s.value} className="bg-[#0A0F1E]">{s.label}</option>
              ))}
            </select>
          </div>

          {/* Feature inputs */}
          <div className="grid grid-cols-2 gap-3">
            {FIELD_META.map(f => (
              <div key={f.key}>
                <label className="text-xs text-gray-400 block mb-1">{f.label}</label>
                <input
                  type={f.type}
                  value={form[f.key]}
                  onChange={e => handleChange(f.key, e.target.value)}
                  className="w-full text-xs bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:border-blue-500/50 font-mono"
                />
              </div>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900 disabled:text-blue-700 text-white font-semibold transition-colors text-sm"
          >
            {loading ? "Running inference..." : "Run Prediction"}
          </button>

          {error && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/5 p-3">
              <p className="text-red-400 text-xs">{error}</p>
            </div>
          )}
        </div>

        {/* Results */}
        <div className="space-y-4">

          {/* Prediction result */}
          {result && (
            <div className="rounded-xl border border-blue-500/30 bg-blue-500/5 p-5 space-y-4">
              <h2 className="text-sm font-semibold text-blue-300">Prediction Results</h2>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label:"Hybrid Prediction", value: result.hybrid_prediction?.toFixed(2),  color:"text-cyan-400",   big:true },
                  { label:"XGBoost Prediction",value: result.xgb_prediction?.toFixed(2),     color:"text-yellow-400", big:false },
                  { label:"LSTM Prediction",   value: result.lstm_prediction?.toFixed(2),    color:"text-purple-400", big:false },
                  { label:"Blend Strategy",    value: result.blend_strategy,                 color:"text-gray-300",   big:false },
                ].map(c => (
                  <div key={c.label} className={`rounded-lg bg-white/5 p-3 ${c.big ? "col-span-2" : ""}`}>
                    <p className="text-xs text-gray-400 mb-1">{c.label}</p>
                    <p className={`font-bold font-mono ${c.big ? "text-3xl" : "text-lg"} ${c.color}`}>
                      {c.value ?? "—"}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Inventory policy result */}
          {invResult && (
            <div className="rounded-xl border border-green-500/30 bg-green-500/5 p-5 space-y-3">
              <h2 className="text-sm font-semibold text-green-300">Computed Inventory Policy</h2>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label:"Safety Stock", value: invResult.safety_stock?.toFixed(1), color:"text-yellow-400" },
                  { label:"Reorder Point",value: invResult.rop?.toFixed(1),          color:"text-blue-400"   },
                  { label:"EOQ",          value: invResult.eoq?.toFixed(0),          color:"text-purple-400" },
                ].map(c => (
                  <div key={c.label} className="rounded-lg bg-white/5 p-3">
                    <p className="text-xs text-gray-400 mb-1">{c.label}</p>
                    <p className={`text-xl font-bold font-mono ${c.color}`}>{c.value ?? "—"}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty state */}
          {!result && !loading && (
            <div className="rounded-xl border border-white/10 bg-white/5 p-8 flex items-center justify-center h-64">
              <p className="text-gray-600 text-sm">Results will appear here after running prediction</p>
            </div>
          )}

          {loading && (
            <div className="rounded-xl border border-white/10 bg-white/5 p-8 flex items-center justify-center h-64">
              <div className="space-y-2 text-center">
                <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"/>
                <p className="text-gray-500 text-xs">Running inference...</p>
              </div>
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
