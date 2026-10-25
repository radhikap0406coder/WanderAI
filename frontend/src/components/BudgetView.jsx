import React from 'react';
import { 
  DollarSign, PieChart, TrendingDown, Sparkles, ShieldCheck, 
  Bed, Utensils, Ticket, Bus, AlertCircle
} from 'lucide-react';

export default function BudgetView({ budget, currency = 'USD' }) {
  if (!budget) return null;

  const categories = budget.categories || {};
  const isUnderBudget = budget.variance >= 0;

  const getCategoryIcon = (key) => {
    switch (key) {
      case 'accommodation':
        return <Bed className="w-4 h-4 text-sky-400" />;
      case 'dining':
        return <Utensils className="w-4 h-4 text-amber-400" />;
      case 'activities':
        return <Ticket className="w-4 h-4 text-purple-400" />;
      case 'local_transit':
        return <Bus className="w-4 h-4 text-emerald-400" />;
      default:
        return <ShieldCheck className="w-4 h-4 text-indigo-400" />;
    }
  };

  const getCategoryBarColor = (key) => {
    switch (key) {
      case 'accommodation':
        return 'bg-sky-500';
      case 'dining':
        return 'bg-amber-500';
      case 'activities':
        return 'bg-purple-500';
      case 'local_transit':
        return 'bg-emerald-500';
      default:
        return 'bg-indigo-500';
    }
  };

  return (
    <div className="space-y-6">
      {/* Overview Ledger Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Total Target */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Allocated User Budget</span>
            <DollarSign className="w-3.5 h-3.5 text-slate-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-white">
            {currency} {budget.total_budget?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </p>
          <p className="text-xs text-slate-500 mt-1">Starting target ceiling</p>
        </div>

        {/* Total Estimated Cost */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Estimated Total Spend</span>
            <DollarSign className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-indigo-400">
            {currency} {budget.estimated_total_cost?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </p>
          <p className="text-xs text-slate-500 mt-1">
            ~{currency} {budget.per_person_per_day?.toLocaleString()} / traveler / day
          </p>
        </div>

        {/* Variance Status */}
        <div className={`glass-panel rounded-2xl p-5 border ${
          isUnderBudget ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-amber-500/30 bg-amber-500/5'
        }`}>
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Budget Balance</span>
            <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
              isUnderBudget ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
            }`}>
              {budget.status || (isUnderBudget ? 'Under Budget' : 'Over Budget')}
            </span>
          </div>
          <p className={`text-2xl sm:text-3xl font-extrabold ${
            isUnderBudget ? 'text-emerald-400' : 'text-amber-400'
          }`}>
            {currency} {budget.variance > 0 ? `+${budget.variance.toLocaleString(undefined, { minimumFractionDigits: 2 })}` : budget.variance?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </p>
          <p className="text-xs text-slate-400 mt-1">
            {isUnderBudget ? 'Surplus available for upgrades' : 'Tight budget; follow savings advice'}
          </p>
        </div>
      </div>

      {/* Visual Category Allocation Bar */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <PieChart className="w-5 h-5 text-indigo-400" />
            <h3 className="text-lg font-bold text-white">Expense Distribution Breakdown</h3>
          </div>
          <span className="text-xs text-slate-400">Target Proportions</span>
        </div>

        {/* Multi-segmented Progress Bar */}
        <div className="w-full h-3 rounded-full bg-slate-900 overflow-hidden flex">
          {Object.entries(categories).map(([key, cat]) => (
            <div
              key={key}
              title={`${cat.name}: ${cat.percentage}%`}
              style={{ width: `${cat.percentage}%` }}
              className={`h-full ${getCategoryBarColor(key)} transition-all duration-500`}
            />
          ))}
        </div>

        {/* Category Legend & Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
          {Object.entries(categories).map(([key, cat]) => (
            <div key={key} className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-slate-950 border border-slate-800">
                    {getCategoryIcon(key)}
                  </div>
                  <h4 className="text-xs font-bold text-white">{cat.name}</h4>
                </div>
                <span className="text-xs font-mono font-semibold text-slate-400">
                  {cat.percentage}%
                </span>
              </div>
              <p className="text-lg font-bold text-slate-200">
                {currency} {cat.allocated_amount?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </p>
              <p className="text-[11px] text-slate-400 line-clamp-2">
                {cat.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Savings & Luxury Upgrades Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Cost Savings Tips */}
        {budget.saving_tips && budget.saving_tips.length > 0 && (
          <div className="glass-panel rounded-3xl p-6 border border-emerald-500/20 bg-emerald-500/5 space-y-3">
            <div className="flex items-center gap-2 text-emerald-400">
              <TrendingDown className="w-5 h-5" />
              <h4 className="text-base font-bold text-white">Smart Cost-Saving Strategies</h4>
            </div>
            <ul className="space-y-2">
              {budget.saving_tips.map((tip, idx) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Luxury Upgrades */}
        {budget.luxury_upgrades && budget.luxury_upgrades.length > 0 && (
          <div className="glass-panel rounded-3xl p-6 border border-indigo-500/20 bg-indigo-500/5 space-y-3">
            <div className="flex items-center gap-2 text-indigo-400">
              <Sparkles className="w-5 h-5 text-amber-300" />
              <h4 className="text-base font-bold text-white">Curated Splurges & Upgrades</h4>
            </div>
            <ul className="space-y-2">
              {budget.luxury_upgrades.map((upg, idx) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                  <span>{upg}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
