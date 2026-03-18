"use client";
import { useEffect, useState } from "react";
import { getDashboardModels } from "@/lib/api";

const METRICS = ["MAPE","MAE","RMSE","R2"];

export default function ModelsPage() {
  const [data, setData] = useState([]);
  const [sortBy, setSortBy] = useState("MAPE");
  const [sortAsc, setSortAsc] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDashboardModels()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  function toggleSort(col) {
    if (sortBy === col) setSortAsc(a => !a);
    else { setSortBy(col); setSortAsc(true); }
  }

  const sorted = [...data].sort((a, b) => {
    const diff = (a[sortBy] || 0) - (b[sortBy] || 0);
    return sortAsc ? diff : -diff;
  });

  // Best value per metric
  const best = {};
  METRICS.forEach(m => {
    const vals = data.map(r => r[m]).filter(v => v != null);
    best[m] = m === "R2" ? Math.max(...vals) : Math.min(...vals);
  });

  if (loading) return (
    <div className="min-h-screen bg-[#0A0F1E] p-6">
      <div className="h-96 bg-white/5 rounded-xl animate-pulse"/>
    </div>
  );
  if (error) return (
    <div className="min-h-screen bg-[#0A0F1E] p-6">
      <p className="text-red-400">Failed to load models: {error}</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#0A0F1E] text-white p-6 space-y-6">

      <div>
        <h1 className="text-2xl font-bold">Model Comparison</h1>
        <p className="text-sm text-gray-400 mt-1">
          All 7 models ranked by performance — click column headers to sort
        </p>
      </div>

      {/* Best model callout */}
      {data.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {METRICS.map(m => {
            const winner = data.find(r => r[m] === best[m]);
            return (
              <div key={m} className="rounded-xl border border-white/10 bg-white/5 p-4">
                <p className="text-xs text-gray-400 mb-1">Best {m}</p>
                <p className="text-lg font-bold font-mono text-green-400">
                  {best[m]?.toFixed(4)}
                </p>
                <p className="text-xs text-gray-500 mt-1">{winner?.Model}</p>
              </div>
            );
          })}
        </div>
      )}

      {/* Sortable table */}
      <div className="rounded-xl border border-white/10 bg-white/5 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/10 bg-white/5">
              <th className="text-left px-4 py-3 text-xs text-gray-400 font-medium">Model</th>
              {METRICS.map(m => (
                <th key={m}
                  onClick={() => toggleSort(m)}
                  className="text-left px-4 py-3 text-xs text-gray-400 font-medium cursor-pointer hover:text-white transition-colors select-none"
                >
                  {m} {sortBy === m ? (sortAsc ? "↑" : "↓") : ""}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((r, i) => (
              <tr key={i} className={`border-b border-white/5 hover:bg-white/5 transition-colors
                ${i % 2 === 0 ? "" : "bg-white/[0.02]"}`}>
                <td className="px-4 py-3 font-medium text-gray-200">{r.Model}</td>
                {METRICS.map(m => (
                  <td key={m} className={`px-4 py-3 font-mono text-xs
                    ${r[m] === best[m] ? "text-green-400 font-bold" : "text-gray-300"}`}>
                    {r[m]?.toFixed(4)}
                    {r[m] === best[m] && (
                      <span className="ml-1 text-[10px] bg-green-500/20 text-green-400 px-1 rounded">best</span>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Strategy explanation */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          { name:"Hybrid Simple Avg",    desc:"Equal 50/50 weight between LSTM and XGBoost predictions." },
          { name:"Hybrid Weighted",      desc:"Fixed weights optimized on validation set per SKU group." },
          { name:"Hybrid Meta-Learner",  desc:"Ridge regression trained on LSTM+XGB outputs to learn optimal blend." },
          { name:"Hybrid Dynamic",       desc:"Per-SKU inverse-MAE weights — better model gets higher weight automatically." },
        ].map(s => (
          <div key={s.name} className="rounded-xl border border-white/10 bg-white/5 p-4">
            <p className="text-sm font-semibold text-blue-300 mb-1">{s.name}</p>
            <p className="text-xs text-gray-400">{s.desc}</p>
          </div>
        ))}
      </div>

    </div>
  );
}
