"use client";
import { useEffect, useState } from "react";
import { getDashboardInventory, getDashboardSKUList } from "@/lib/api";

const POLICIES = ["Original", "Baseline", "Hybrid"];
const POLICY_COLORS = {
  Original: "text-gray-400",
  Baseline: "text-yellow-400",
  Hybrid:   "text-green-400",
};

export default function InventoryPage() {
  const [rows, setRows]         = useState([]);
  const [skuList, setSkuList]   = useState([]);
  const [selectedSKU, setSKU]   = useState("ALL");
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);

  useEffect(() => {
    Promise.all([getDashboardInventory(), getDashboardSKUList()])
      .then(([inv, skus]) => {
        // inv is array of policy comparison rows
        const invArr = Array.isArray(inv) ? inv : [];
        setRows(invArr);
        const unique = [...new Set(
          (Array.isArray(skus) ? skus : []).map(s => s.SKU_ID)
        )];
        setSkuList(unique);
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  // Filter rows by selected SKU
  const filtered = Array.isArray(rows)
    ? (selectedSKU === "ALL" ? rows : rows.filter(r => r.SKU_ID === selectedSKU))
    : [];

  // Summary: total cost per policy across filtered rows
  const policySummary = POLICIES.map(p => {
    const pRows = filtered.filter(r => r.Policy === p);
    const total = pRows.reduce((a, r) => a + (r.Total_Cost || 0), 0);
    const stockouts = pRows.reduce((a, r) => a + (r.Stockout_Days || 0), 0);
    return { policy: p, total_cost: total, stockout_days: stockouts, count: pRows.length };
  });

  if (loading) return (
    <div className="min-h-screen bg-[#0A0F1E] p-6 space-y-4">
      <div className="h-8 w-64 bg-white/5 rounded animate-pulse"/>
      <div className="h-96 bg-white/5 rounded-xl animate-pulse"/>
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-[#0A0F1E] p-6">
      <p className="text-red-400">Failed to load inventory: {error}</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#0A0F1E] text-white p-6 space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Inventory Policy</h1>
          <p className="text-sm text-gray-400 mt-1">
            3-policy simulation — Original vs Baseline vs Hybrid per SKU × Warehouse
          </p>
        </div>
        <select
          value={selectedSKU}
          onChange={e => setSKU(e.target.value)}
          className="text-xs bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-gray-300 focus:outline-none focus:border-blue-500/50"
        >
          <option value="ALL" className="bg-[#0A0F1E]">All SKUs</option>
          {skuList.map(s => (
            <option key={s} value={s} className="bg-[#0A0F1E]">{s}</option>
          ))}
        </select>
      </div>

      {/* Policy summary cards */}
      <div className="grid grid-cols-3 gap-4">
        {policySummary.map(p => (
          <div key={p.policy} className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-2">
            <p className={`text-sm font-semibold ${POLICY_COLORS[p.policy]}`}>{p.policy} Policy</p>
            <div>
              <p className="text-xs text-gray-500">Total Cost</p>
              <p className="text-xl font-bold font-mono text-white">
                ${p.total_cost.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </p>
            </div>
            <div className="flex gap-4">
              <div>
                <p className="text-xs text-gray-500">Stockout Days</p>
                <p className="text-sm font-mono text-red-400">{p.stockout_days}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">SKU×WH rows</p>
                <p className="text-sm font-mono text-gray-300">{p.count}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Table */}
      <div className="rounded-xl border border-white/10 bg-white/5 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 bg-white/5">
                {["SKU_ID","Warehouse_ID","Policy","Stockout_Days",
                  "Avg_Inventory","Total_Orders","Holding_Cost",
                  "Ordering_Cost","Stockout_Cost","Total_Cost"].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-xs text-gray-400 font-medium whitespace-nowrap">
                    {h.replace(/_/g," ")}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((r, i) => (
                <tr key={i} className={`border-b border-white/5 hover:bg-white/5 transition-colors
                  ${i % 2 === 0 ? "" : "bg-white/[0.02]"}`}>
                  <td className="px-4 py-2.5 font-mono text-xs text-blue-300">{r.SKU_ID}</td>
                  <td className="px-4 py-2.5 font-mono text-xs text-gray-300">{r.Warehouse_ID}</td>
                  <td className={`px-4 py-2.5 font-mono text-xs font-semibold ${POLICY_COLORS[r.Policy] || "text-gray-300"}`}>
                    {r.Policy}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-xs text-red-400">{r.Stockout_Days}</td>
                  <td className="px-4 py-2.5 font-mono text-xs text-gray-300">
                    {r.Avg_Inventory?.toFixed(1)}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-xs text-gray-300">{r.Total_Orders}</td>
                  <td className="px-4 py-2.5 font-mono text-xs text-yellow-400">
                    ${r.Holding_Cost?.toFixed(2)}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-xs text-gray-300">
                    ${r.Ordering_Cost?.toFixed(2)}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-xs text-red-400">
                    ${r.Stockout_Cost?.toFixed(2)}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-xs text-green-400 font-semibold">
                    ${r.Total_Cost?.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-2 border-t border-white/5 text-xs text-gray-500">
          Showing {filtered.length} of {rows.length} rows
        </div>
      </div>

    </div>
  );
}
