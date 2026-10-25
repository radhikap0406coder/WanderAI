import React from 'react';
import { 
  Compass, DollarSign, Heart, Search, Calendar, 
  Calculator, CheckCircle2, Loader2, Sparkles, Terminal
} from 'lucide-react';

const AGENT_NODES = [
  { id: 'destination_agent', label: 'Destination Agent', icon: Compass, color: 'text-sky-400', border: 'border-sky-500/40', bg: 'bg-sky-500/10' },
  { id: 'budget_agent', label: 'Budget Agent', icon: DollarSign, color: 'text-emerald-400', border: 'border-emerald-500/40', bg: 'bg-emerald-500/10' },
  { id: 'preferences_agent', label: 'Preferences Agent', icon: Heart, color: 'text-rose-400', border: 'border-rose-500/40', bg: 'bg-rose-500/10' },
  { id: 'research_agent', label: 'Research / Search', icon: Search, color: 'text-amber-400', border: 'border-amber-500/40', bg: 'bg-amber-500/10' },
  { id: 'itinerary_generator', label: 'Itinerary Generator', icon: Calendar, color: 'text-indigo-400', border: 'border-indigo-500/40', bg: 'bg-indigo-500/10' },
  { id: 'budget_calculator', label: 'Budget Calculator', icon: Calculator, color: 'text-teal-400', border: 'border-teal-500/40', bg: 'bg-teal-500/10' },
  { id: 'final_planner', label: 'Final Planner', icon: Sparkles, color: 'text-purple-400', border: 'border-purple-500/40', bg: 'bg-purple-500/10' },
];

export default function AgentPipelineTracker({ logs = [], isRunning, activeNode }) {
  // Determine status for each agent from logs or active node
  const getAgentStatus = (agentName) => {
    const agentLogs = logs.filter(l => l.agent && l.agent.toLowerCase().includes(agentName.toLowerCase().replace(/agent/g, '').trim()));
    const hasCompleted = agentLogs.some(l => l.status === 'completed');
    const isWorking = agentLogs.some(l => l.status === 'running') && !hasCompleted;

    if (hasCompleted) return 'completed';
    if (isWorking || (activeNode && activeNode.toLowerCase().includes(agentName.toLowerCase().slice(0, 5)))) return 'running';
    return isRunning ? 'pending' : 'completed';
  };

  return (
    <div className="w-full max-w-5xl mx-auto my-8 glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 shadow-2xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-400 animate-spin" style={{ animationDuration: '6s' }} />
            <h3 className="text-lg font-bold text-white">LangGraph Multi-Agent Orchestration</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time execution of the 7-node collaborative state graph
          </p>
        </div>

        <div className="flex items-center gap-2">
          {isRunning ? (
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              Agents Collaborating...
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5" />
              All 7 Agents Succeeded
            </span>
          )}
        </div>
      </div>

      {/* Visual Pipeline Layout matching Architecture Diagram */}
      <div className="space-y-4">
        {/* Level 1: Concurrent Trio (Destination, Budget, Preferences) */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[AGENT_NODES[0], AGENT_NODES[1], AGENT_NODES[2]].map((node) => {
            const status = getAgentStatus(node.label);
            const Icon = node.icon;
            return (
              <div
                key={node.id}
                className={`p-3.5 rounded-2xl border transition ${
                  status === 'running'
                    ? 'bg-slate-900 border-indigo-500 shadow-lg shadow-indigo-500/20 ring-1 ring-indigo-500 animate-pulse'
                    : status === 'completed'
                    ? 'bg-slate-900/80 border-slate-700/80'
                    : 'bg-slate-950/40 border-slate-800/60 opacity-60'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className={`p-2 rounded-xl ${node.bg} ${node.color}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-white">{node.label}</h4>
                      <p className="text-[10px] text-slate-400">Phase 1 (Fan-out)</p>
                    </div>
                  </div>
                  <div>
                    {status === 'running' && <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />}
                    {status === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                    {status === 'pending' && <span className="w-2 h-2 rounded-full bg-slate-700" />}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Down Arrow separator */}
        <div className="flex justify-center text-slate-600 text-xs font-mono">
          ↓ Fan-In Synthesis ↓
        </div>

        {/* Level 2: Downstream Sequential Pipeline */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[AGENT_NODES[3], AGENT_NODES[4], AGENT_NODES[5], AGENT_NODES[6]].map((node, i) => {
            const status = getAgentStatus(node.label);
            const Icon = node.icon;
            return (
              <div
                key={node.id}
                className={`p-3.5 rounded-2xl border transition ${
                  status === 'running'
                    ? 'bg-slate-900 border-indigo-500 shadow-lg shadow-indigo-500/20 ring-1 ring-indigo-500 animate-pulse'
                    : status === 'completed'
                    ? 'bg-slate-900/80 border-slate-700/80'
                    : 'bg-slate-950/40 border-slate-800/60 opacity-60'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`p-1.5 rounded-lg ${node.bg} ${node.color}`}>
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-white truncate max-w-[90px] sm:max-w-none">{node.label}</h4>
                      <p className="text-[10px] text-slate-400">Step {i + 2}</p>
                    </div>
                  </div>
                  <div>
                    {status === 'running' && <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />}
                    {status === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                    {status === 'pending' && <span className="w-2 h-2 rounded-full bg-slate-700" />}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Terminal Live Output Feed */}
      {logs.length > 0 && (
        <div className="mt-4 rounded-2xl bg-slate-950/90 border border-slate-800/90 p-4 font-mono text-xs">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-slate-400">
            <div className="flex items-center gap-2">
              <Terminal className="w-3.5 h-3.5 text-indigo-400" />
              <span>Multi-Agent Thought & Log Stream</span>
            </div>
            <span className="text-[10px] text-slate-500">{logs.length} events emitted</span>
          </div>

          <div className="mt-3 max-h-48 overflow-y-auto space-y-2 pr-1">
            {logs.map((log, idx) => (
              <div key={idx} className="flex items-start gap-2.5 text-slate-300">
                <span className="text-slate-500 text-[10px] shrink-0">{log.timestamp || '00:00'}</span>
                <span className="font-semibold text-indigo-300 shrink-0">[{log.agent}]:</span>
                <span className="text-slate-300 break-words">{log.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
