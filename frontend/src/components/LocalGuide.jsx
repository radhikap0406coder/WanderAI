import React from 'react';
import { Shield, PhoneCall, BookOpen, Sun, AlertTriangle } from 'lucide-react';

export default function LocalGuide({ plan }) {
  if (!plan) return null;

  const customs = plan.local_customs || [];
  const emergencies = plan.emergency_contacts || {};

  return (
    <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 shadow-xl space-y-6">
      <div className="pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-indigo-400" />
          <h3 className="text-xl font-bold text-white">Local Culture, Customs & Emergency Guide</h3>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Essential survival knowledge, etiquette, and contacts for {plan.destination}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Cultural Etiquette */}
        <div className="space-y-4">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Shield className="w-4 h-4 text-indigo-400" />
            <span>Cultural Etiquette & Etiquette Dos and Don'ts</span>
          </h4>
          <div className="space-y-2.5">
            {customs.map((custom, idx) => (
              <div key={idx} className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800 flex items-start gap-3">
                <span className="w-5 h-5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 font-bold text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <p className="text-xs text-slate-300 leading-relaxed">{custom}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Emergency Contacts & Weather */}
        <div className="space-y-6">
          {/* Emergency Numbers */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
              <PhoneCall className="w-4 h-4 text-rose-400" />
              <span>Emergency Help Lines</span>
            </h4>
            <div className="grid grid-cols-2 gap-2.5">
              {Object.entries(emergencies).map(([service, number]) => (
                <div key={service} className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block capitalize">
                    {service.replace(/_/g, ' ')}
                  </span>
                  <p className="text-sm font-bold text-rose-400 mt-0.5 font-mono">
                    {number}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Climate & Weather Brief */}
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center gap-2 text-amber-400 text-xs font-bold">
              <Sun className="w-4 h-4" />
              <span>Climate Overview</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {plan.climate_guide}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
