"use client";
import { useEffect, useState } from "react";
import { getDashboardSKUList, getDashboardSKU } from "@/lib/api";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function SKUPage() {
  const [skuList, setSkuList] = useState([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [skuData, setSkuData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDL] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDashboardSKUList()
      .then(list => {
        const arr = Array.isArray(list) ? list : [];
        setSkuList(arr);
        if (arr.length > 0) selectSKU(arr[0].SKU_ID);
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  function selectSKU(skuId) {
    setSelected(skuId);
    setDL(true);
    getDashboardSKU(skuId)
      .then(setSkuData)
      .catch(console.error)
      .finally(() => setDL(false));
  }

  const uniqueSKUs = [...new Map(skuList.map(s => [s.SKU_ID, s])).values()];
  const filtered = uniqueSKUs.filter(s =>
    s.SKU_ID.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#0A0F1E] text-white p-6">
      <div className="flex gap-6 h-full">

        {/* SKU list sidebar */}
        <div className="w-56 flex-shrink-0 space-y-3">
          <h1 className="text-lg font-bold">SKU Explorer</h1>
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search SKUs..."
            className="w-full text-xs bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-gray-300 placeholder-gray-600 focus:outline-none focus:border-blue-500/50"
          />
          {loading ? (
            <div className="space-y-2">
              {[...Array(8)].map((_,i) => <div key={i} className="h-8 bg-white/5 rounded animate-pulse"/>)}
            </div>
          ) : (
            <div className="space-y-1 max-h-[70vh] overflow-y-auto pr-1">
              {filtered.map(s => (
                <button
                  key={s.SKU_ID}
                  onClick={() => selectSKU(s.SKU_ID)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-colors
                    ${selected === s.SKU_ID
                      ? "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                      : "text-gray-400 hover:bg-white/5 hover:text-gray-200"}`}
                >
                  {s.SKU_ID}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* SKU detail */}
        <div className="flex-1 space-y-6">
          {detailLoading && (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                {[...Array(3)].map((_,i) => <div key={i} className="h-24 bg-white/5 rounded-xl animate-pulse"/>)}
              </div>
              <div className="h-64 bg-white/5 rounded-xl animate-pulse"/>
            </div>
          )}

          {!detailLoading && skuData && (
            <>
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white">{skuData.sku_id}</h2>
                <span className="text-xs text-gray-500 font-mono">{skuData.row_count} rows</span>
              </div>

              {/* Metric cards */}
              <div className="grid grid-cols-3 gap-4">
                {[
                  { label:"MAPE",      value:`${skuData.mape?.toFixed(3)}%`, color:"text-blue-400" },
                  { label:"MAE",       value:skuData.mae?.toFixed(4),        color:"text-purple-400" },
                  { label:"Data Points",value:skuData.row_count,             color:"text-cyan-400" },
                ].map(c => (
                  <div key={c.label} className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <p className="text-xs text-gray-400 mb-1">{c.label}</p>
                    <p className={`text-2xl font-bold font-mono ${c.color}`}>{c.value}</p>
                  </div>
                ))}
              </div>

              {/* Forecast chart */}
              {skuData.forecasts?.length > 0 && (
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                  <h3 className="text-sm font-semibold text-gray-300 mb-4">
                    Forecast vs Actual — {skuData.sku_id}
                  </h3>
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={skuData.forecasts.slice(0, 200)}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)"/>
                      <XAxis dataKey="Date" tick={{ fill:"#9ca3af", fontSize:10 }} tickLine={false}/>
                      <YAxis tick={{ fill:"#9ca3af", fontSize:10 }} tickLine={false} axisLine={false}/>
                      <Tooltip contentStyle={{ background:"#0f172a", border:"1px solid rgba(255,255,255,0.1)", borderRadius:"8px", color:"#f1f5f9" }}/>
                      <Line type="monotone" dataKey="Units_Sold"  stroke="#6366f1" dot={false} strokeWidth={2} name="Actual"/>
                      <Line type="monotone" dataKey="Hybrid_Pred" stroke="#22d3ee" dot={false} strokeWidth={2} name="Hybrid"/>
                      <Line type="monotone" dataKey="XGB_Pred"    stroke="#f59e0b" dot={false} strokeWidth={1} strokeDasharray="3 2" name="XGBoost"/>
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </>
          )}

          {!detailLoading && !skuData && (
            <div className="flex items-center justify-center h-64 text-gray-600">
              Select a SKU from the left panel
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
