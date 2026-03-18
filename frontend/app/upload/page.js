"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { uploadCSV, getJobStatus } from "@/lib/api";

const REQUIRED_COLUMNS = [
  "Date","SKU_ID","Warehouse_ID","Supplier_ID","Region",
  "Units_Sold","Inventory_Level","Supplier_Lead_Time_Days",
  "Reorder_Point","Order_Quantity","Unit_Cost","Unit_Price",
  "Promotion_Flag","Stockout_Flag","Demand_Forecast"
];

const STEP_LABELS = [
  "Queued...",
  "Validating schema and cleaning data...",
  "Engineering features...",
  "Saving feature sets...",
  "Feature engineering complete.",
  "Running XGBoost inference...",
  "XGBoost inference complete.",
  "Running LSTM inference...",
  "LSTM inference complete.",
  "Blending predictions...",
  "Hybrid blend complete.",
  "Computing inventory policy...",
  "Inventory policy computed.",
  "Computing business value metrics...",
  "Pipeline complete.",
];

export default function UploadPage() {
  const router = useRouter();
  const fileInputRef = useRef(null);
  const pollRef = useRef(null);

  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [validation, setValidation] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => () => clearInterval(pollRef.current), []);

  function handleFile(f) {
    if (!f || !f.name.endsWith(".csv")) {
      setError("Only CSV files are accepted.");
      return;
    }
    setFile(f);
    setError(null);
    validateColumns(f);
  }

  function validateColumns(f) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const firstLine = e.target.result.split("\n")[0];
      const headers = firstLine.split(",").map(h => h.trim().replace(/"/g, ""));
      const missing = REQUIRED_COLUMNS.filter(c => !headers.includes(c));
      setValidation({ ok: missing.length === 0, missing, headers });
    };
    reader.readAsText(f);
  }

  function onDrop(e) {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  }

  async function handleUpload() {
    if (!file || !validation?.ok) return;
    setUploading(true);
    setError(null);
    try {
      const { job_id } = await uploadCSV(file);
      setJob({ job_id, status: "queued", progress: 0, current_step: "Queued..." });
      pollRef.current = setInterval(async () => {
        try {
          const j = await getJobStatus(job_id);
          setJob(j);
          if (j.status === "done") {
            clearInterval(pollRef.current);
            setTimeout(() => router.push(`/results/${job_id}`), 800);
          }
          if (j.status === "failed") {
            clearInterval(pollRef.current);
            setError(`Pipeline failed: ${j.error}`);
            setUploading(false);
          }
        } catch {
          clearInterval(pollRef.current);
          setError("Lost connection to backend.");
          setUploading(false);
        }
      }, 2000);
    } catch (e) {
      setError(`Upload failed: ${e.message}`);
      setUploading(false);
    }
  }

  const isProcessing = uploading && job?.status !== "done";

  return (
    <div className="min-h-screen bg-[#0A0F1E] text-white p-6 max-w-2xl mx-auto space-y-6">

      <div>
        <h1 className="text-2xl font-bold text-white">Upload New Dataset</h1>
        <p className="text-sm text-gray-400 mt-1">
          Run your own CSV through the trained models to generate fresh predictions.
        </p>
      </div>

      {!isProcessing && (
        <div
          onDragOver={e => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all
            ${dragging
              ? "border-blue-400 bg-blue-500/10"
              : file
              ? "border-green-500/50 bg-green-500/5"
              : "border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/8"
            }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={e => handleFile(e.target.files[0])}
          />
          {file ? (
            <div className="space-y-1">
              <p className="text-green-400 font-semibold">{file.name}</p>
              <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-gray-300 font-medium">Drop your CSV here</p>
              <p className="text-xs text-gray-500">or click to browse</p>
            </div>
          )}
        </div>
      )}

      {validation && !isProcessing && (
        <div className={`rounded-xl border p-4 space-y-3
          ${validation.ok
            ? "border-green-500/30 bg-green-500/5"
            : "border-red-500/30 bg-red-500/5"}`}
        >
          <p className={`text-sm font-semibold ${validation.ok ? "text-green-400" : "text-red-400"}`}>
            {validation.ok ? "✓ Schema valid — all 15 columns found" : "✗ Schema invalid — missing columns"}
          </p>
          {!validation.ok && (
            <div className="flex flex-wrap gap-2">
              {validation.missing.map(c => (
                <span key={c} className="text-xs px-2 py-0.5 rounded-md bg-red-500/20 text-red-300 font-mono">
                  {c}
                </span>
              ))}
            </div>
          )}
          <div className="grid grid-cols-3 gap-1">
            {REQUIRED_COLUMNS.map(c => (
              <span key={c} className={`text-xs px-2 py-0.5 rounded font-mono
                ${validation.headers?.includes(c)
                  ? "bg-green-500/10 text-green-400"
                  : "bg-red-500/10 text-red-400"}`}
              >
                {validation.headers?.includes(c) ? "✓" : "✗"} {c}
              </span>
            ))}
          </div>
        </div>
      )}

      {file && validation?.ok && !isProcessing && (
        <button
          onClick={handleUpload}
          className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold transition-colors"
        >
          Run Pipeline
        </button>
      )}

      {isProcessing && job && (
        <div className="rounded-xl border border-white/10 bg-white/5 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-white">Processing...</p>
            <span className="text-xs font-mono text-blue-400">{job.progress}%</span>
          </div>
          <div className="w-full bg-white/10 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${Math.max(0, job.progress)}%` }}
            />
          </div>
          <p className="text-xs text-gray-400">{job.current_step}</p>
          <div className="space-y-1">
            {STEP_LABELS.map((label, i) => {
              const stepPct = (i / STEP_LABELS.length) * 100;
              const done = job.progress > stepPct;
              const active = job.current_step === label;
              return (
                <div key={i} className={`flex items-center gap-2 text-xs transition-colors
                  ${active ? "text-blue-400" : done ? "text-green-400" : "text-gray-600"}`}
                >
                  <span>{done ? "✓" : active ? "▶" : "○"}</span>
                  <span>{label}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {job?.status === "done" && (
        <div className="rounded-xl border border-green-500/30 bg-green-500/5 p-4 text-center">
          <p className="text-green-400 font-semibold">Pipeline complete — redirecting to results...</p>
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-4">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

    </div>
  );
}
