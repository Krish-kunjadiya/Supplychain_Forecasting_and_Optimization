"use client";
import { useEffect, useState } from "react";
import { getDashboardModels } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from "recharts";

export default function ModelComparisonChart() {
  const [data, setData] = useState([]);
  const [metric, setMetric] = useState("MAPE");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDashboardModels()
      .then(d => {
        const clean = (Array.isArray(d) ? d : []).map(r => ({
          ...r,
          MAPE : r.MAPE  ?? 0,
          MAE  : r.MAE   ?? 0,
          RMSE : r.RMSE  ?? 0,
          R2   : r.R2    ?? 0,
        }));
        setData(clean);
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-72 rounded-xl bg-white/5 animate-pulse" />;
  if (error) return <div className="text-red-400 text-sm">Failed to load model comparison: {error}</div>;
  if (!data.length) return null;

  const metrics = ["MAPE", "MAE", "RMSE", "R2"];

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-300">Model Comparison</h3>
        <div className="flex gap-2">
          {metrics.map(m => (
            <button key={m} onClick={() => setMetric(m)}
              className={`text-xs px-2 py-1 rounded-md transition-colors ${metric === m ? "bg-blue-500/30 text-blue-300" : "text-gray-500 hover:text-gray-300"}`}>
              {m}
            </button>
          ))}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
          <XAxis type="number" tick={{ fill: "#9ca3af", fontSize: 11 }} tickLine={false} axisLine={false} />
          <YAxis type="category" dataKey="Model" tick={{ fill: "#9ca3af", fontSize: 11 }} tickLine={false} width={90} />
          <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px", color: "#f1f5f9" }} />
          <Bar dataKey={metric} fill="#22d3ee" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
