import React, { useState } from 'react';
import { CheckSquare, Square, Luggage, CheckCircle2, RotateCcw } from 'lucide-react';

export default function PackingChecklist({ checklist = [] }) {
  const [checkedItems, setCheckedItems] = useState({});

  if (!checklist || checklist.length === 0) return null;

  const totalItems = checklist.reduce((acc, cat) => acc + (cat.items?.length || 0), 0);
  const checkedCount = Object.values(checkedItems).filter(Boolean).length;
  const progressPercent = totalItems > 0 ? Math.round((checkedCount / totalItems) * 100) : 0;

  const toggleItem = (itemKey) => {
    setCheckedItems(prev => ({
      ...prev,
      [itemKey]: !prev[itemKey]
    }));
  };

  const resetAll = () => {
    setCheckedItems({});
  };

  return (
    <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 shadow-xl space-y-6">
      {/* Header & Progress */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <Luggage className="w-5 h-5 text-indigo-400" />
            <h3 className="text-xl font-bold text-white">Smart Destination Packing Checklist</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Tailored to your duration, forecast, and planned activities
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <span className="text-xs text-slate-400">Packed:</span>
            <p className="text-sm font-bold text-indigo-400">
              {checkedCount} / {totalItems} items ({progressPercent}%)
            </p>
          </div>
          {checkedCount > 0 && (
            <button
              onClick={resetAll}
              className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 text-xs flex items-center gap-1 transition"
              title="Reset all checkmarks"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
        <div
          style={{ width: `${progressPercent}%` }}
          className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 transition-all duration-300"
        />
      </div>

      {/* Checklist Categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {checklist.map((group, groupIdx) => (
          <div key={groupIdx} className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-300 flex items-center justify-between">
              <span>{group.category}</span>
              <span className="text-[10px] text-slate-500">{group.items?.length || 0} items</span>
            </h4>

            <div className="space-y-2">
              {group.items?.map((item, itemIdx) => {
                const itemKey = `${groupIdx}_${itemIdx}`;
                const isChecked = !!checkedItems[itemKey];
                return (
                  <div
                    key={itemIdx}
                    onClick={() => toggleItem(itemKey)}
                    className={`flex items-start gap-2.5 p-2 rounded-xl cursor-pointer select-none transition ${
                      isChecked
                        ? 'bg-emerald-500/10 text-slate-400 line-through'
                        : 'hover:bg-slate-850 text-slate-200'
                    }`}
                  >
                    <button type="button" className="mt-0.5 shrink-0">
                      {isChecked ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <Square className="w-4 h-4 text-slate-500" />
                      )}
                    </button>
                    <span className="text-xs leading-relaxed">{item}</span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
