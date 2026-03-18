"use client";
import { useState, useEffect } from "react";
import KPICards from "@/components/dashboard/KPICards";
import ForecastTimeline from "@/components/dashboard/ForecastTimeline";
import ModelComparisonChart from "@/components/dashboard/ModelComparisonChart";
import { WaterfallChart, SKUWinnersChart } from "@/components/dashboard/MiscCharts";
import { getDashboardSKUList, getDashboardForecasts } from "@/lib/api";

export default function DashboardPage() {
  const [skuList, setSkuList]     = useState([]);
  const [selectedSKU, setSKU]     = useState(null);
  const [selectedWH, setWH]       = useState(null);

  useEffect(() => {
    getDashboardSKUList()
      .then(list => {
        // list is array of {SKU_ID, Warehouse_ID}
        if (Array.isArray(list) && list.length > 0) {
          setSkuList(list);
          setSKU(list[0].SKU_ID);
          setWH(list[0].Warehouse_ID);
        }
        // handle {sku_ids:[...]} shape from pipeline results
        else if (list?.sku_ids?.length > 0) {
          const ids = list.sku_ids.map(s => ({ SKU_ID: s, Warehouse_ID: "" }));
          setSkuList(ids);
          setSKU(ids[0].SKU_ID);
        }
      })
      .catch(console.error);
  }, []);

  // Deduplicated SKU_IDs for dropdown
  const uniqueSKUs = [...new Set(skuList.map(s => s.SKU_ID))];

  return (
    <div className="min-h-screen bg-[#0A0F1E] text-white p-6 space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Supply Chain Dashboard</h1>
          <p className="text-sm text-gray-400 mt-1">Pre-computed results — trained pipeline outputs</p>
        </div>
        <span className="text-xs px-3 py-1 rounded-full bg-green-500/20 text-green-400 border border-green-500/30">
          Live Data
        </span>
      </div>

      {/* KPI Cards */}
      <KPICards />

      {/* Forecast Timeline */}
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <h2 className="text-sm font-semibold text-gray-300">Forecast Timeline</h2>
          {uniqueSKUs.length > 0 && (
            <select
              value={selectedSKU || ""}
              onChange={e => setSKU(e.target.value)}
              className="text-xs bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-gray-300 focus:outline-none focus:border-blue-500/50"
            >
              {uniqueSKUs.map(s => (
                <option key={s} value={s} className="bg-[#0A0F1E]">{s}</option>
              ))}
            </select>
          )}
        </div>
        <ForecastTimeline skuId={selectedSKU} />
      </div>

      {/* Model Comparison */}
      <ModelComparisonChart />

      {/* Waterfall + MAPE by Model */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <WaterfallChart />
        <SKUWinnersChart />
      </div>

    </div>
  );
}
