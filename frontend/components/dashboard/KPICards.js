"use client";
import { useEffect, useState } from "react";
import { getDashboardKPI } from "@/lib/api";

export default function KPICards({ jobId = null }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fn = jobId
      ? () => import("@/lib/api").then(m => m.getResultKPI(jobId))
      : getDashboardKPI;
    fn().then(setData).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, [jobId]);

  if (loading) return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[...Array(4)].map((_,i) => <div key={i} className="h-28 rounded-xl bg-white/5 animate-pulse"/>)}
    </div>
  );
  if (error) return <div className="text-red-400 text-sm p-4">Failed to load KPIs: {error}</div>;
  if (!data)  return null;

  // Handle both dashboard shape {business_value, hybrid_metrics}
  // and pipeline shape {hybrid_mape, r2, ...}
  const bv = data.business_value || data;
  const hm = data.hybrid_metrics || data;

  const cards = [
    {
      label: "Hybrid MAPE",
      value: `${(hm.MAPE || hm.hybrid_mape || 0).toFixed(3)}%`,
      sub:   `Baseline: ${(bv.hybrid_forecast_mape || bv.baseline_mape || 0).toFixed(3)}%`,
      color: "text-blue-400"
    },
    {
      label: "Cost Saving",
      value: `$${((bv.cost_saving_vs_original || 0)).toLocaleString()}`,
      sub:   `${(bv.pct_cost_saving || 0).toFixed(1)}% vs original`,
      color: "text-green-400"
    },
    {
      label: "R² Score",
      value: (hm.R2 || hm.r2 || 0).toFixed(4),
      sub:   "hybrid model accuracy",
      color: "text-purple-400"
    },
    {
      label: "Best Strategy",
      value: bv.best_strategy || hm.best_strategy || "Hybrid",
      sub:   `Service level: ${((bv.service_level_target || 0.95) * 100).toFixed(0)}%`,
      color: "text-cyan-400"
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map((c) => (
        <div key={c.label} className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4">
          <p className="text-xs text-gray-400 mb-1">{c.label}</p>
          <p className={`text-2xl font-bold font-mono ${c.color}`}>{c.value}</p>
          <p className="text-xs text-gray-500 mt-1">{c.sub}</p>
        </div>
      ))}
    </div>
  );
}
