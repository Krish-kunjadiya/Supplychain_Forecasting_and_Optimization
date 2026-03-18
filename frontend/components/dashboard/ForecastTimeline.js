"use client";
import { useEffect, useState } from "react";
import { getDashboardForecasts, getResultForecasts } from "@/lib/api";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from "recharts";

export default function ForecastTimeline({ jobId = null, skuId = null }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fn = jobId
      ? () => getResultForecasts(jobId, skuId)
      : () => getDashboardForecasts(skuId);
    fn().then(d => {
      const clean = (Array.isArray(d) ? d : []).filter(
        r => r.Date && r.Units_Sold != null
      );
      setData(clean);
    }).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, [jobId, skuId]);

  if (loading) return <div className="h-72 rounded-xl bg-white/5 animate-pulse" />;
  if (error) return <div className="text-red-400 text-sm">Failed to load forecasts: {error}</div>;
  if (!data.length) return <div className="text-gray-500 text-sm">No forecast data available.</div>;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">Forecast Timeline</h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="Date" tick={{ fill: "#9ca3af", fontSize: 11 }} tickLine={false} />
          <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} tickLine={false} axisLine={false} />
          <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px", color: "#f1f5f9" }} />
          <Legend wrapperStyle={{ color: "#9ca3af", fontSize: 12 }} />
          <Line type="monotone" dataKey="Units_Sold" stroke="#6366f1" dot={false} strokeWidth={2} name="Actual" />
          <Line type="monotone" dataKey="Hybrid_Pred" stroke="#22d3ee" dot={false} strokeWidth={2} name="Hybrid" />
          <Line type="monotone" dataKey="XGB_Pred" stroke="#f59e0b" dot={false} strokeWidth={1} strokeDasharray="4 2" name="XGBoost" />
          <Line type="monotone" dataKey="LSTM_Pred" stroke="#a78bfa" dot={false} strokeWidth={1} strokeDasharray="4 2" name="LSTM" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
