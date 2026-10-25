import React, { useState } from 'react';
import { 
  MapPin, Calendar, DollarSign, Users, Sparkles, Heart, 
  Compass, Bed, Gauge, Check, Coffee
} from 'lucide-react';

const QUICK_DESTINATIONS = [
  { label: 'Tokyo, Japan', flag: '🇯🇵', desc: 'Neon, Shrines & Food' },
  { label: 'Paris, France', flag: '🇫🇷', desc: 'Art, Cafes & Seine' },
  { label: 'Rome, Italy', flag: '🇮🇹', desc: 'Colosseum & Dolce Vita' },
  { label: 'Bali, Indonesia', flag: '🇮🇩', desc: 'Beaches, Terraces & Spas' },
  { label: 'New York City, USA', flag: '🇺🇸', desc: 'Skyline & Broadway' },
  { label: 'Barcelona, Spain', flag: '🇪🇸', desc: 'Gaudí, Tapas & Beach' },
  { label: 'Swiss Alps, Switzerland', flag: '🇨🇭', desc: 'Peaks & Alpine Lakes' },
  { label: 'London, UK', flag: '🇬🇧', desc: 'Royal History & West End' },
];

const CURRENCIES = [
  { code: 'USD', symbol: '$' },
  { code: 'EUR', symbol: '€' },
  { code: 'GBP', symbol: '£' },
  { code: 'INR', symbol: '₹' },
  { code: 'JPY', symbol: '¥' },
  { code: 'CAD', symbol: 'CA$' },
  { code: 'AUD', symbol: 'AU$' },
];

const TRAVELER_TYPES = [
  { id: 'Solo', label: 'Solo Explorer', icon: '🎒' },
  { id: 'Couple', label: 'Romantic Couple', icon: '💑' },
  { id: 'Family', label: 'Family with Kids', icon: '👨‍👩‍👧‍👦' },
  { id: 'Friends', label: 'Group of Friends', icon: '🥂' },
];

const ACCOMMODATIONS = [
  'Budget / Hostel',
  'Comfort Hotel (3-Star)',
  'Boutique / 4-Star',
  'Luxury Resort (5-Star)',
  'Vacation Rental / Villa'
];

const PACES = [
  { id: 'Relaxed', label: 'Relaxed & Easy', desc: '1-2 sights/day, leisurely meals' },
  { id: 'Balanced', label: 'Balanced Pace', desc: '2-3 sights/day, optimal flow' },
  { id: 'Fast-Paced', label: 'Action-Packed', desc: '3-4 stops/day, maximum coverage' },
];

const INTEREST_OPTIONS = [
  'Culture & History',
  'Culinary & Dining',
  'Nature & Outdoors',
  'Beaches & Coastal',
  'Art & Architecture',
  'Nightlife & Social',
  'Shopping & Boutiques',
  'Hidden Local Gems',
  'Wellness & Spas',
  'Scenic Photography'
];

export default function TripForm({ onSubmit, isLoading }) {
  const [origin, setOrigin] = useState('New York, USA');
  const [destination, setDestination] = useState('Tokyo, Japan');
  const [duration, setDuration] = useState(5);
  const [startDate, setStartDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 14);
    return d.toISOString().split('T')[0];
  });
  const [budgetTotal, setBudgetTotal] = useState(2500);
  const [currency, setCurrency] = useState('USD');
  const [travelersCount, setTravelersCount] = useState(2);
  const [travelerType, setTravelerType] = useState('Couple');
  const [accommodationType, setAccommodationType] = useState('Boutique / 4-Star');
  const [pace, setPace] = useState('Balanced');
  const [selectedInterests, setSelectedInterests] = useState([
    'Culture & History',
    'Culinary & Dining',
    'Hidden Local Gems'
  ]);
  const [notes, setNotes] = useState('');

  const toggleInterest = (interest) => {
    if (selectedInterests.includes(interest)) {
      if (selectedInterests.length > 1) {
        setSelectedInterests(selectedInterests.filter(i => i !== interest));
      }
    } else {
      setSelectedInterests([...selectedInterests, interest]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      origin,
      destination,
      duration_days: Number(duration),
      start_date: startDate,
      budget_total: Number(budgetTotal),
      currency,
      travelers_count: Number(travelersCount),
      traveler_type: travelerType,
      accommodation_type: accommodationType,
      pace,
      interests: selectedInterests,
      notes
    });
  };

  return (
    <div className="w-full max-w-5xl mx-auto">
      {/* Hero Header */}
      <div className="text-center py-6 sm:py-10">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-4">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-spin" style={{ animationDuration: '4s' }} />
          <span>Powered by 7 Autonomous LangGraph AI Agents</span>
        </div>
        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white">
          Design Your Dream Journey in Seconds
        </h1>
        <p className="mt-4 text-base sm:text-lg text-slate-400 max-w-2xl mx-auto">
          Autonomous multi-agent intelligence orchestrates destinations, budgets, pacing, 
          and curated day-by-day itineraries tailored directly to your personal vibe.
        </p>

        {/* Quick Destination Chips */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-2 max-w-3xl mx-auto">
          <span className="text-xs font-medium text-slate-500 mr-1 flex items-center gap-1">
            <Compass className="w-3 h-3" /> Quick Picks:
          </span>
          {QUICK_DESTINATIONS.map((q) => (
            <button
              key={q.label}
              type="button"
              onClick={() => setDestination(q.label)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition flex items-center gap-1.5 ${
                destination === q.label
                  ? 'bg-indigo-600/30 border-indigo-500 text-white shadow-sm'
                  : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700 hover:text-white'
              }`}
            >
              <span>{q.flag}</span>
              <span>{q.label.split(',')[0]}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Form Container */}
      <form onSubmit={handleSubmit} className="mt-4 glass-panel rounded-3xl p-6 sm:p-10 shadow-2xl space-y-8">
        
        {/* Row 1: Origin & Destination */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Origin */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              <span>Departing From (Origin)</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. New York, London, Mumbai"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              className="w-full px-4 py-3 rounded-2xl bg-slate-900 border border-slate-800 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition text-sm sm:text-base font-medium"
            />
          </div>

          {/* Destination */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5 text-indigo-400" />
              <span>Target Destination or Dream Region</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Tokyo, Paris, Bali, Swiss Alps, Iceland"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              className="w-full px-4 py-3 rounded-2xl bg-slate-900 border border-indigo-500/50 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400 transition text-sm sm:text-base font-semibold"
            />
          </div>
        </div>

        {/* Row 2: Duration, Dates, and Budget */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {/* Duration */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                <span>Trip Duration</span>
              </label>
              <span className="text-sm font-bold text-indigo-400 px-2 py-0.5 rounded bg-indigo-500/10">
                {duration} Days
              </span>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="range"
                min="1"
                max="14"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
            </div>
            <div className="flex justify-between text-[11px] text-slate-500 font-mono">
              <span>1 Day</span>
              <span>7 Days</span>
              <span>14 Days</span>
            </div>
          </div>

          {/* Start Date */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              <span>Estimated Departure Date</span>
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-2.5 rounded-2xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-indigo-500 text-sm font-medium"
            />
          </div>

          {/* Budget & Currency */}
          <div className="space-y-2 sm:col-span-2 lg:col-span-1">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
              <span>Total Travel Budget</span>
            </label>
            <div className="flex items-center gap-2">
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="px-3 py-2.5 rounded-2xl bg-slate-900 border border-slate-800 text-white font-semibold text-sm focus:outline-none focus:border-indigo-500"
              >
                {CURRENCIES.map(c => (
                  <option key={c.code} value={c.code}>{c.code} ({c.symbol})</option>
                ))}
              </select>
              <input
                type="number"
                min="200"
                step="50"
                value={budgetTotal}
                onChange={(e) => setBudgetTotal(e.target.value)}
                className="w-full px-4 py-2.5 rounded-2xl bg-slate-900 border border-slate-800 text-white text-sm font-bold focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Row 3: Traveler Makeup & Type */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5 text-slate-400" />
              <span>Who is Traveling?</span>
            </label>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span>Count:</span>
              <input
                type="number"
                min="1"
                max="12"
                value={travelersCount}
                onChange={(e) => setTravelersCount(Math.max(1, Number(e.target.value)))}
                className="w-14 px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-center text-white font-bold"
              />
              <span>Person{travelersCount > 1 ? 's' : ''}</span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {TRAVELER_TYPES.map((t) => (
              <button
                type="button"
                key={t.id}
                onClick={() => setTravelerType(t.id)}
                className={`p-3 rounded-2xl border text-left transition flex items-center gap-3 ${
                  travelerType === t.id
                    ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-md'
                    : 'bg-slate-900/50 border-slate-800/80 text-slate-400 hover:border-slate-700 hover:text-white'
                }`}
              >
                <span className="text-2xl">{t.icon}</span>
                <div>
                  <p className="text-xs font-bold leading-tight">{t.label}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Row 4: Accommodation Style & Pacing */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Accommodation */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Bed className="w-3.5 h-3.5 text-slate-400" />
              <span>Preferred Accommodation Style</span>
            </label>
            <select
              value={accommodationType}
              onChange={(e) => setAccommodationType(e.target.value)}
              className="w-full px-4 py-3 rounded-2xl bg-slate-900 border border-slate-800 text-white font-medium text-sm focus:outline-none focus:border-indigo-500"
            >
              {ACCOMMODATIONS.map(acc => (
                <option key={acc} value={acc}>{acc}</option>
              ))}
            </select>
          </div>

          {/* Travel Pace */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Gauge className="w-3.5 h-3.5 text-slate-400" />
              <span>Sightseeing Pace</span>
            </label>
            <div className="grid grid-cols-3 gap-2">
              {PACES.map(p => (
                <button
                  type="button"
                  key={p.id}
                  onClick={() => setPace(p.id)}
                  className={`p-2.5 rounded-xl border text-center transition ${
                    pace === p.id
                      ? 'bg-indigo-600/20 border-indigo-500 text-white font-bold'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <p className="text-xs font-semibold">{p.label}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Row 5: Tailored Interests */}
        <div className="space-y-3">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Heart className="w-3.5 h-3.5 text-rose-400" />
              <span>Travel Interests & Themes</span>
            </span>
            <span className="text-[11px] text-slate-500">Pick any combination</span>
          </label>
          <div className="flex flex-wrap gap-2">
            {INTEREST_OPTIONS.map((interest) => {
              const isSelected = selectedInterests.includes(interest);
              return (
                <button
                  type="button"
                  key={interest}
                  onClick={() => toggleInterest(interest)}
                  className={`px-3.5 py-2 rounded-xl text-xs font-semibold border transition flex items-center gap-1.5 ${
                    isSelected
                      ? 'bg-gradient-to-r from-indigo-600 to-violet-600 border-indigo-400 text-white shadow-md shadow-indigo-600/20'
                      : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700 hover:text-white'
                  }`}
                >
                  {isSelected && <Check className="w-3.5 h-3.5 text-white" />}
                  <span>{interest}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Row 6: Custom Notes */}
        <div className="space-y-2">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Coffee className="w-3.5 h-3.5 text-amber-400" />
            <span>Special Requests, Dietary Wishes or Bucket-List Items (Optional)</span>
          </label>
          <textarea
            rows="2"
            placeholder="e.g. Vegetarian dining, anniversary celebration on Day 2, wheelchair accessible paths, early risers..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full px-4 py-2.5 rounded-2xl bg-slate-900 border border-slate-800 text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 text-sm"
          />
        </div>

        {/* Submit Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-4 px-6 rounded-2xl font-bold text-white text-base sm:text-lg bg-gradient-to-r from-indigo-600 via-violet-600 to-amber-500 hover:from-indigo-500 hover:via-violet-500 hover:to-amber-400 active:scale-[0.99] transition shadow-xl shadow-indigo-600/25 flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Orchestrating 7 Multi-Agent LangGraph Workflows...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 text-amber-300 group-hover:rotate-12 transition-transform duration-300" />
                <span>Generate Autonomous Multi-Agent Trip Plan</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
