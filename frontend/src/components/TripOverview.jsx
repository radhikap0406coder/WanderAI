import React from 'react';
import { 
  Compass, Calendar, Users, DollarSign, CloudSun, 
  Download, FileText, Printer, CheckCircle
} from 'lucide-react';

export default function TripOverview({ plan, onExportMarkdown, onDownloadJson }) {
  if (!plan) return null;

  const budget = plan.budget_breakdown || {};
  const currency = plan.currency || 'USD';

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="w-full max-w-5xl mx-auto glass-panel rounded-3xl p-6 sm:p-10 border border-slate-800 shadow-2xl space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-800">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center gap-1">
              <Compass className="w-3 h-3" />
              {plan.duration_days} Days Trip
            </span>
            <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              {budget.status || 'Optimal Plan'}
            </span>
          </div>

          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            {plan.title || `${plan.destination} Itinerary`}
          </h2>
          <p className="text-sm sm:text-base text-slate-400 mt-2 max-w-2xl">
            {plan.vibe_summary}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <button
            onClick={onExportMarkdown}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white text-xs sm:text-sm font-medium transition"
            title="Download as Markdown file"
          >
            <FileText className="w-4 h-4 text-indigo-400" />
            <span>Export .md</span>
          </button>

          <button
            onClick={onDownloadJson}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white text-xs sm:text-sm font-medium transition"
            title="Download structured JSON"
          >
            <Download className="w-4 h-4 text-emerald-400" />
            <span>Download JSON</span>
          </button>

          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-indigo-600/30 transition"
            title="Print or Save to PDF"
          >
            <Printer className="w-4 h-4" />
            <span>Print / PDF</span>
          </button>
        </div>
      </div>

      {/* Highlights Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium mb-1">
            <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
            <span>Est. Total Cost</span>
          </div>
          <p className="text-xl sm:text-2xl font-bold text-white">
            {currency} {budget.estimated_total_cost?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0'}
          </p>
          <p className="text-[11px] text-slate-500 mt-0.5">
            Budget: {currency} {budget.total_budget?.toLocaleString() || '0'}
          </p>
        </div>

        {/* Metric 2 */}
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium mb-1">
            <DollarSign className="w-3.5 h-3.5 text-indigo-400" />
            <span>Spend / Person / Day</span>
          </div>
          <p className="text-xl sm:text-2xl font-bold text-white">
            {currency} {budget.per_person_per_day?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0'}
          </p>
          <p className="text-[11px] text-slate-500 mt-0.5">
            {plan.travelers_count} travelers
          </p>
        </div>

        {/* Metric 3 */}
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium mb-1">
            <Users className="w-3.5 h-3.5 text-rose-400" />
            <span>Traveler Party</span>
          </div>
          <p className="text-lg sm:text-xl font-bold text-white truncate">
            {plan.traveler_type}
          </p>
          <p className="text-[11px] text-slate-500 mt-0.5">
            {plan.travelers_count} person{plan.travelers_count > 1 ? 's' : ''}
          </p>
        </div>

        {/* Metric 4 */}
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium mb-1">
            <CloudSun className="w-3.5 h-3.5 text-amber-400" />
            <span>Climate Insight</span>
          </div>
          <p className="text-xs font-medium text-slate-300 line-clamp-2">
            {plan.climate_guide || 'Favorable conditions'}
          </p>
        </div>
      </div>
    </div>
  );
}
