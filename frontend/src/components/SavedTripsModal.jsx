import React, { useState, useEffect } from 'react';
import { X, History, Trash2, Calendar, MapPin, DollarSign, ArrowRight, Loader2 } from 'lucide-react';

export default function SavedTripsModal({ isOpen, onClose, onLoadTrip, currentTripId }) {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchTrips();
    }
  }, [isOpen]);

  const fetchTrips = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/trips');
      if (!res.ok) throw new Error('Failed to load trips');
      const data = await res.json();
      setTrips(data.trips || []);
    } catch (err) {
      console.error(err);
      setError('Could not connect to database backend.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e, tripId) => {
    e.stopPropagation();
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/trips/${tripId}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        setTrips(prev => prev.filter(t => t.id !== tripId));
      }
    } catch (err) {
      console.error('Failed to delete trip:', err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden p-6 text-slate-200 max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
              <History className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Saved AI Travel Dossiers</h3>
              <p className="text-xs text-slate-400">Persisted locally in SQLite repository</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto py-4 space-y-3 pr-1">
          {loading && (
            <div className="flex items-center justify-center py-12 text-slate-400 gap-2">
              <Loader2 className="w-5 h-5 animate-spin text-indigo-400" />
              <span>Fetching saved dossiers...</span>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs text-center">
              {error}
            </div>
          )}

          {!loading && trips.length === 0 && !error && (
            <div className="text-center py-12 text-slate-500 space-y-2">
              <History className="w-10 h-10 mx-auto text-slate-600" />
              <p className="text-sm">No saved trips found yet.</p>
              <p className="text-xs text-slate-500">Generate your first trip to save it automatically to SQLite!</p>
            </div>
          )}

          {!loading && trips.map((trip) => {
            const isCurrent = trip.id === currentTripId;
            return (
              <div
                key={trip.id}
                onClick={() => {
                  onLoadTrip(trip);
                  onClose();
                }}
                className={`p-4 rounded-2xl border transition cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                  isCurrent
                    ? 'bg-indigo-950/40 border-indigo-500 ring-1 ring-indigo-500'
                    : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-base">
                      {trip.title || trip.destination}
                    </span>
                    {isCurrent && (
                      <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                        Active Plan
                      </span>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-indigo-400" />
                      {trip.destination}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5 text-emerald-400" />
                      {trip.duration_days} Days
                    </span>
                    <span className="flex items-center gap-1">
                      <DollarSign className="w-3.5 h-3.5 text-amber-400" />
                      {trip.currency || 'USD'} {trip.budget_breakdown?.estimated_total_cost?.toLocaleString() || trip.budget_total?.toLocaleString()}
                    </span>
                  </div>
                  {trip.created_at && (
                    <p className="text-[10px] text-slate-500">
                      Generated: {new Date(trip.created_at).toLocaleString()}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-2 self-end sm:self-center">
                  <button
                    onClick={(e) => handleDelete(e, trip.id)}
                    className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition"
                    title="Delete saved dossier"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                  <button
                    className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1 transition"
                  >
                    <span>View Plan</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
