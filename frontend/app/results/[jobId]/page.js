"use client";
import { useParams } from "next/navigation";
import KPICards from "@/components/dashboard/KPICards";
import ForecastTimeline from "@/components/dashboard/ForecastTimeline";
import ModelComparisonChart from "@/components/dashboard/ModelComparisonChart";
import { WaterfallChart } from "@/components/dashboard/MiscCharts";
import { getResultSKUList } from "@/lib/api";
import { useState, useEffect } from "react";
import Link from "next/link";

export default function ResultsPage() {
  const { jobId } = useParams();
  const [skuList, setSkuList] = useState([]);
  const [selectedSKU, setSKU] = useState(null);

  useEffect(() => {
    if (!jobId) return;
    getResultSKUList(jobId)
      .then(d => {
        const ids = d.sku_ids || [];
        setSkuList(ids);
        if (ids.length > 0) setSKU(ids[0]);
      })
      .catch(console.error);
  }, [jobId]);

  if (!jobId) return <div className="p-6 text-gray-400">No job ID provided.</div>;

  return (
    <div className="min-h-screen bg-[#0A0F1E] text-white p-6 space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <Link href="/dashboard"
              className="text-xs text-gray-500 hover:text-gray-300 transition-colors">
              ← Back to Dashboard
            </Link>
            <span className="text-gray-600">|</span>
            <Link href="/upload"
              className="text-xs text-gray-500 hover:text-gray-300 transition-colors">
              New Upload
            </Link>
          </div>
          <h1 className="text-2xl font-bold text-white">Pipeline Results</h1>
          <p className="text-xs text-gray-500 font-mono mt-1">Job: {jobId}</p>
        </div>
        <span className="text-xs px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
          Fresh Inference
        </span>
      </div>

      {/* KPI Cards — jobId prop makes it read from pipeline results */}
      <KPICards jobId={jobId} />

      {/* Forecast Timeline */}
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <h2 className="text-sm font-semibold text-gray-300">Forecast Timeline</h2>
          {skuList.length > 0 && (
            <select
              value={selectedSKU || ""}
              onChange={e => setSKU(e.target.value)}
              className="text-xs bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-gray-300 focus:outline-none focus:border-blue-500/50"
            >
              {skuList.map(s => (
                <option key={s} value={s} className="bg-[#0A0F1E]">{s}</option>
              ))}
            </select>
          )}
        </div>
        <ForecastTimeline jobId={jobId} skuId={selectedSKU} />
      </div>

      {/* Model Comparison — always reads from /dashboard/models (same trained models) */}
      <ModelComparisonChart />

      {/* Waterfall — jobId makes it read from pipeline results */}
      <WaterfallChart jobId={jobId} />

    </div>
  );
}
