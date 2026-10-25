import React, { useState } from 'react';
import { 
  Calendar, Clock, MapPin, DollarSign, Lightbulb, 
  Sun, Sunset, Moon, Navigation, Tag
} from 'lucide-react';

export default function ItineraryView({ itinerary = [], currency = 'USD', onSelectActivity }) {
  const [selectedDayIndex, setSelectedDayIndex] = useState(0); // 0 = Day 1, or -1 for All

  if (!itinerary || itinerary.length === 0) {
    return (
      <div className="text-center py-12 text-slate-500">
        No itinerary days generated yet.
      </div>
    );
  }

  const getTimeIcon = (slot) => {
    switch (slot) {
      case 'Morning':
        return <Sun className="w-4 h-4 text-amber-400" />;
      case 'Afternoon':
        return <Sunset className="w-4 h-4 text-orange-400" />;
      case 'Evening':
        return <Moon className="w-4 h-4 text-indigo-400" />;
      default:
        return <Clock className="w-4 h-4 text-slate-400" />;
    }
  };

  const getCategoryColor = (cat) => {
    switch (cat?.toLowerCase()) {
      case 'culture':
        return 'bg-purple-500/10 text-purple-300 border-purple-500/20';
      case 'dining':
        return 'bg-amber-500/10 text-amber-300 border-amber-500/20';
      case 'sightseeing':
        return 'bg-sky-500/10 text-sky-300 border-sky-500/20';
      case 'nature':
        return 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  const displayedDays = selectedDayIndex === -1 ? itinerary : [itinerary[selectedDayIndex]];

  return (
    <div className="space-y-6">
      {/* Day Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        <button
          onClick={() => setSelectedDayIndex(-1)}
          className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap border transition ${
            selectedDayIndex === -1
              ? 'bg-indigo-600 border-indigo-500 text-white shadow-md shadow-indigo-600/30'
              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'
          }`}
        >
          View All Days ({itinerary.length})
        </button>

        {itinerary.map((day, idx) => (
          <button
            key={day.day_number}
            onClick={() => setSelectedDayIndex(idx)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap border transition ${
              selectedDayIndex === idx
                ? 'bg-indigo-600 border-indigo-500 text-white shadow-md shadow-indigo-600/30'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'
            }`}
          >
            Day {day.day_number}
          </button>
        ))}
      </div>

      {/* Days Schedule List */}
      <div className="space-y-8">
        {displayedDays.map((day) => (
          <div 
            key={day.day_number}
            className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 shadow-xl space-y-6"
          >
            {/* Day Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
              <div>
                <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-1">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>{day.date_label || `Day ${day.day_number}`}</span>
                </div>
                <h3 className="text-xl sm:text-2xl font-bold text-white">
                  {day.theme}
                </h3>
                <p className="text-xs sm:text-sm text-slate-400 mt-1">
                  {day.summary}
                </p>
              </div>

              <div className="text-left sm:text-right shrink-0">
                <span className="text-xs text-slate-500">Day Est. Spend</span>
                <p className="text-lg font-bold text-emerald-400">
                  {currency} {day.day_total_cost?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </p>
              </div>
            </div>

            {/* Activities Timeline */}
            <div className="space-y-4">
              {day.activities?.map((act, actIdx) => (
                <div
                  key={actIdx}
                  className="p-4 sm:p-5 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition space-y-3 group"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center gap-1.5 text-xs font-semibold text-slate-200">
                        {getTimeIcon(act.time_slot)}
                        <span>{act.time_slot}</span>
                      </div>
                      <span className="text-xs text-slate-400 font-mono">
                        {act.time}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${getCategoryColor(act.category)}`}>
                        {act.category}
                      </span>
                      <span className="text-xs font-bold text-slate-300">
                        {currency} {act.estimated_cost?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-base sm:text-lg font-bold text-white group-hover:text-indigo-300 transition">
                      {act.title}
                    </h4>
                    <p className="text-xs sm:text-sm text-slate-300 mt-1 leading-relaxed">
                      {act.description}
                    </p>
                  </div>

                  <div className="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs text-slate-400 border-t border-slate-800/60">
                    <div className="flex items-center gap-1.5 text-slate-300">
                      <MapPin className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                      <span>{act.location}</span>
                    </div>

                    {act.tips && (
                      <div className="flex items-center gap-1.5 text-amber-300/90 text-[11px] bg-amber-500/10 px-2.5 py-1 rounded-lg border border-amber-500/20">
                        <Lightbulb className="w-3 h-3 text-amber-400 shrink-0" />
                        <span>{act.tips}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Day Transit Footer */}
            {day.transit_tips && (
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center gap-2 text-xs text-slate-400">
                <Navigation className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                <span><strong>Transit Route:</strong> {day.transit_tips}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
