"use client";
import { useEffect, useState } from "react";
import { getDashboardWaterfall, getDashboardModels } from "@/lib/api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  Cell, PieChart, Pie, Legend, CartesianGrid
} from "recharts";

export function WaterfallChart({ jobId = null }) {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    const fn = jobId
      ? () => import("@/lib/api").then(m => m.getResultKPI(jobId))
      : getDashboardWaterfall;
    fn().then(d => {
        // handle both shapes
        const flat = d.business_value || d;
        setData(flat);
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [jobId]);

  if (loading) return <div className="h-64 rounded-xl bg-white/5 animate-pulse"/>;
  if (error)   return <div className="text-red-400 text-sm p-4">Failed to load: {error}</div>;
  if (!data)   return null;

  const bars = [
    { label: "Cost Saving",        value: data.cost_saving_vs_original || 0 },
    { label: "Avg Inv Change",     value: data.avg_inventory_change    || 0 },
    { label: "Stockout Reduction", value: data.stockout_days_reduction || 0 },
  ];
  const COLORS = bars.map(b => b.value >= 0 ? "#22d3ee" : "#f87171");

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">Business Value Waterfall</h3>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={bars}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false}/>
          <XAxis dataKey="label" tick={{ fill:"#9ca3af", fontSize:11 }} tickLine={false}/>
          <YAxis tick={{ fill:"#9ca3af", fontSize:11 }} tickLine={false} axisLine={false}/>
          <Tooltip
            contentStyle={{ background:"#0f172a", border:"1px solid rgba(255,255,255,0.1)", borderRadius:"8px", color:"#f1f5f9" }}
            formatter={v => v.toLocaleString()}
          />
          <Bar dataKey="value" radius={[4,4,0,0]}>
            {bars.map((_, i) => <Cell key={i} fill={COLORS[i]}/>)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function SKUWinnersChart() {
  const [data, setData]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    getDashboardModels()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-64 rounded-xl bg-white/5 animate-pulse"/>;
  if (error)   return <div className="text-red-400 text-sm p-4">Failed to load: {error}</div>;
  if (!data.length) return null;

  // Show MAPE per model as pie
  const pieData = data
    .filter(m => m.MAPE < 50) // exclude extreme outliers for readability
    .map(m => ({ name: m.Model, value: parseFloat(m.MAPE.toFixed(3)) }));

  const COLORS = ["#22d3ee","#f59e0b","#a78bfa","#34d399","#f87171","#60a5fa","#fb923c"];

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">MAPE by Model</h3>
      <ResponsiveContainer width="100%" height={240}>
        <PieChart>
          <Pie
            data={pieData} dataKey="value" nameKey="name"
            cx="50%" cy="50%" outerRadius={80}
            label={({ name, value }) => `${value}%`}
            labelLine={false}
          >
            {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]}/>)}
          </Pie>
          <Legend wrapperStyle={{ color:"#9ca3af", fontSize:11 }}/>
          <Tooltip
            contentStyle={{ background:"#0f172a", border:"1px solid rgba(255,255,255,0.1)", borderRadius:"8px" }}
            formatter={v => `${v}%`}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
