import Link from "next/link";

const TECH = ["Python 3.10","TensorFlow 2.15","XGBoost 2.0","FastAPI","Next.js 14","Recharts","Tailwind CSS"];

const PIPELINE_STEPS = [
  { n:"01", label:"Data Validation",      desc:"Schema checks, null handling, duplicate removal" },
  { n:"02", label:"EDA",                  desc:"Distribution analysis, correlation, stockout patterns" },
  { n:"03", label:"Feature Engineering",  desc:"66 features — lags, rolling stats, cyclic encoding" },
  { n:"04", label:"LSTM Model",           desc:"BiLSTM(128)+LSTM(64), 30-day lookback, Huber loss" },
  { n:"05", label:"XGBoost Model",        desc:"40-iter RandomizedSearch, TimeSeriesSplit CV" },
  { n:"06", label:"Hybrid Blend",         desc:"4 strategies — Simple, Weighted, Meta-Learner, Dynamic" },
  { n:"07", label:"Inventory Optimization",desc:"ROP, EOQ, Safety Stock, 3-policy simulation" },
  { n:"08", label:"Results Dashboard",    desc:"7 interactive charts, business value report" },
];

const STATS = [
  { value:"~90k",  label:"Training Rows"     },
  { value:"50",    label:"Unique SKUs"        },
  { value:"0.74%", label:"Hybrid MAPE"        },
  { value:"0.9998",label:"R² Score"           },
  { value:"$104k", label:"Cost Saving"        },
  { value:"16.8%", label:"MAPE Improvement"   },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0A0F1E] text-white">

      {/* Hero */}
      <div className="relative px-6 pt-16 pb-12 max-w-5xl mx-auto text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-blue-500/30 bg-blue-500/10 text-xs text-blue-400 mb-2">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"/>
          Hybrid LSTM + XGBoost · Production Ready
        </div>
        <h1 className="text-4xl md:text-6xl font-bold leading-tight">
          Intelligent Supply Chain
          <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
            Optimization System
          </span>
        </h1>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
          Two-phase ML system that forecasts demand with a hybrid model
          and converts predictions into dynamic inventory policies —
          reducing costs and eliminating stockouts.
        </p>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
          <Link href="/dashboard"
            className="px-8 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold transition-colors text-sm">
            View Dashboard
          </Link>
          <Link href="/upload"
            className="px-8 py-3 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-white font-semibold transition-colors text-sm">
            Upload New Data →
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="px-6 max-w-5xl mx-auto">
        <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
          {STATS.map(s => (
            <div key={s.label} className="rounded-xl border border-white/10 bg-white/5 p-4 text-center">
              <p className="text-2xl font-bold font-mono text-cyan-400">{s.value}</p>
              <p className="text-xs text-gray-500 mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Pipeline steps */}
      <div className="px-6 py-12 max-w-5xl mx-auto space-y-4">
        <h2 className="text-xl font-bold text-white mb-6">8-Notebook Pipeline</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {PIPELINE_STEPS.map(s => (
            <div key={s.n} className="flex gap-4 rounded-xl border border-white/10 bg-white/5 p-4 hover:bg-white/8 transition-colors">
              <span className="text-2xl font-bold font-mono text-blue-500/40 flex-shrink-0 w-8">{s.n}</span>
              <div>
                <p className="text-sm font-semibold text-gray-200">{s.label}</p>
                <p className="text-xs text-gray-500 mt-0.5">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tech stack */}
      <div className="px-6 pb-8 max-w-5xl mx-auto space-y-4">
        <h2 className="text-xl font-bold text-white">Tech Stack</h2>
        <div className="flex flex-wrap gap-2">
          {TECH.map(t => (
            <span key={t} className="px-3 py-1.5 rounded-lg border border-white/10 bg-white/5 text-xs text-gray-300 font-mono">
              {t}
            </span>
          ))}
        </div>
      </div>

      {/* Team */}
      <div className="px-6 pb-16 max-w-5xl mx-auto">
        <div className="rounded-xl border border-white/10 bg-white/5 p-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <p className="text-xs text-gray-500 mb-2">Built by</p>
            <div className="flex gap-6">
              {[
                { name:"Krish Kunjadiya", role:"Project Lead · ML Architecture · API", github:"Krish-kunjadiya" },
                { name:"Khushi",          role:"Data Analysis · Feature Eng. · Testing", github:"khushi911911" },
              ].map(m => (
                <div key={m.github}>
                  <p className="text-sm font-semibold text-white">{m.name}</p>
                  <p className="text-xs text-gray-500">{m.role}</p>
                  <p className="text-xs text-blue-400 font-mono mt-0.5">@{m.github}</p>
                </div>
              ))}
            </div>
          </div>
          <Link href="/dashboard"
            className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold transition-colors flex-shrink-0">
            Explore System →
          </Link>
        </div>
      </div>

    </div>
  );
}
