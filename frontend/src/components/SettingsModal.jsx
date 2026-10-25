import React, { useState } from 'react';
import { X, Key, Cpu, ShieldCheck, Check } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose, userConfig, onSaveConfig, providerInfo }) {
  if (!isOpen) return null;

  const [provider, setProvider] = useState(userConfig.provider || 'auto');
  const [apiKey, setApiKey] = useState(userConfig.apiKey || '');
  const [savedNotice, setSavedNotice] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    onSaveConfig({ provider, apiKey });
    setSavedNotice(true);
    setTimeout(() => {
      setSavedNotice(false);
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden p-6 text-slate-200">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <h3 className="text-lg font-bold text-white">AI Engine & Model Settings</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSave} className="mt-4 space-y-5">
          {/* Active Server Status */}
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Server Backend Status:</span>
              <span className="text-emerald-400 font-semibold flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                Connected
              </span>
            </div>
            <div className="flex items-center justify-between mt-1 pt-1 border-t border-slate-800/50">
              <span className="text-slate-400">Active Server Provider:</span>
              <span className="text-indigo-300 font-medium">{providerInfo?.provider || 'Demo Engine'}</span>
            </div>
          </div>

          {/* Model Provider Option */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Select LLM Provider Mode
            </label>
            <div className="grid grid-cols-2 gap-2">
              {[
                { id: 'auto', name: 'Auto / Demo Engine', note: 'Works out-of-the-box' },
                { id: 'gemini', name: 'Google Gemini', note: 'Fast & Rich Context' },
                { id: 'openai', name: 'OpenAI GPT-4o', note: 'Official OpenAI' },
                { id: 'groq', name: 'Groq Cloud', note: 'Ultra-low latency' },
              ].map((opt) => (
                <button
                  type="button"
                  key={opt.id}
                  onClick={() => setProvider(opt.id)}
                  className={`p-2.5 rounded-xl text-left border transition ${
                    provider === opt.id
                      ? 'bg-indigo-600/20 border-indigo-500 text-white'
                      : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <p className="text-sm font-semibold">{opt.name}</p>
                  <p className="text-[10px] text-slate-400 mt-0.5">{opt.note}</p>
                </button>
              ))}
            </div>
          </div>

          {/* API Key */}
          {provider !== 'auto' && (
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-indigo-400" />
                <span>Client API Key (Optional)</span>
              </label>
              <input
                type="password"
                placeholder={
                  provider === 'gemini'
                    ? 'AIzaSy...'
                    : provider === 'openai'
                    ? 'sk-proj-...'
                    : 'gsk_...'
                }
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
              />
              <p className="text-[11px] text-slate-500 mt-1">
                Your key is stored only in your local browser session and passed securely via headers. You can also configure server-side keys in <code className="text-indigo-300">backend/.env</code>.
              </p>
            </div>
          )}

          <div className="pt-2 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-sm font-medium text-slate-400 hover:text-white transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex items-center gap-2 px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold shadow-lg shadow-indigo-600/30 transition"
            >
              {savedNotice ? (
                <>
                  <Check className="w-4 h-4 text-emerald-300" />
                  Saved!
                </>
              ) : (
                'Save Preferences'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
