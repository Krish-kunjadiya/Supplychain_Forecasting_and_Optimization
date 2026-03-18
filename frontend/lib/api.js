const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const get = (url) => fetch(url).then(r => { if (!r.ok) throw new Error(`GET ${url} → ${r.status}`); return r.json(); });
const post = (url, body) => fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
  .then(r => { if (!r.ok) throw new Error(`POST ${url} → ${r.status}`); return r.json(); });

export const getDashboardKPI = () => get(`${BASE}/dashboard/kpi`);
export const getDashboardForecasts = (sku) => get(`${BASE}/dashboard/forecasts${sku ? `?sku_id=${encodeURIComponent(sku)}` : ""}`);
export const getDashboardModels = () => get(`${BASE}/dashboard/models`);
export const getDashboardInventory = () => get(`${BASE}/dashboard/inventory`);
export const getDashboardSKUList = () => get(`${BASE}/dashboard/sku-list`);
export const getDashboardSKU = (id) => get(`${BASE}/dashboard/sku/${encodeURIComponent(id)}`);
export const getDashboardWaterfall = () => get(`${BASE}/dashboard/waterfall`);

export const uploadCSV = (file) => {
  const fd = new FormData();
  fd.append("file", file);
  return fetch(`${BASE}/pipeline/upload`, { method: "POST", body: fd })
    .then(r => { if (!r.ok) throw new Error(`Upload failed → ${r.status}`); return r.json(); });
};
export const getJobStatus = (jobId) => get(`${BASE}/pipeline/job/${jobId}`);

export const getResultKPI = (id) => get(`${BASE}/pipeline/results/${id}/kpi`);
export const getResultForecasts = (id, sku) => get(`${BASE}/pipeline/results/${id}/forecasts${sku ? `?sku_id=${encodeURIComponent(sku)}` : ""}`);
export const getResultInventory = (id) => get(`${BASE}/pipeline/results/${id}/inventory`);
export const getResultSKUList = (id) => get(`${BASE}/pipeline/results/${id}/sku-list`);
export const getResultSKU = (id, sku) => get(`${BASE}/pipeline/results/${id}/sku/${encodeURIComponent(sku)}`);

export const predictSingle = (body) => post(`${BASE}/predict/single`, body);
export const inventoryPolicy = (body) => post(`${BASE}/inventory/policy`, body);
