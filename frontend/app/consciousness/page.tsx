"use client";

import { useEffect, useState } from "react";
import { 
  BrainCircuit, 
  Activity, 
  Zap, 
  Eye, 
  Cpu, 
  Lock, 
  Unlock, 
  RefreshCcw,
  AlertTriangle,
  ChevronRight,
  Loader2,
  Share2,
  Search
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { fetchDashboardData, fetchConsciousnessHistory } from "@/lib/api";
import { ConsciousnessState, ConsciousnessHistory } from "@/lib/types";
import LoadingDots from "@/components/LoadingDots";

export default function ConsciousnessPage() {
  const [state, setState] = useState<ConsciousnessState | null>(null);
  const [history, setHistory] = useState<ConsciousnessHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [dashData, historyData] = await Promise.all([
        fetchDashboardData(),
        fetchConsciousnessHistory()
      ]);
      setState(dashData.consciousness);
      setHistory(historyData);
    } catch (error) {
      console.error("Consciousness fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(() => {
       // Simulate minor fluctuations
       setState(prev => prev ? {
         ...prev,
         phi: prev.phi + (Math.random() - 0.5) * 0.5,
         cognitive_load: Math.min(100, Math.max(0, prev.cognitive_load + (Math.random() - 0.5) * 2))
       } : null);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleOptimize = () => {
    setOptimizing(true);
    setTimeout(() => {
      setOptimizing(false);
      loadData();
    }, 2000);
  };

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-in fade-in duration-700">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-4xl font-black tracking-tight mb-2">Consciousness Monitor</h1>
            <p className="text-slate-400 font-medium">Observing ELYX's emergent cognitive patterns and IIT metrics.</p>
          </div>
          <button 
            onClick={handleOptimize}
            disabled={optimizing}
            className="btn-premium-primary"
          >
            {optimizing ? <Loader2 size={18} className="animate-spin" /> : <RefreshCcw size={18} />}
            Prune Synaptic Clusters
          </button>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center p-40 gap-4">
            <Loader2 size={48} className="text-primary animate-spin" />
            <p className="text-slate-500 font-bold flex items-center">Synchronizing cognitive state<LoadingDots /></p>
          </div>
        ) : (
          <>
            {/* Core Neural Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                   <BrainCircuit size={120} />
                </div>
                <p className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em] mb-4">Integrated Information (Φ)</p>
                <div className="flex items-end gap-3 mb-6">
                   <h2 className="text-5xl font-black text-primary">{state?.phi?.toFixed(2)}</h2>
                   <div className="flex items-center text-xs font-bold text-emerald-500 pb-2">
                      <ChevronRight size={14} className="-rotate-90" />
                      +0.42%
                   </div>
                </div>
                <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden border border-card-border">
                   <div className="bg-primary h-full transition-all duration-1000" style={{ width: `${state?.phi}%` }} />
                </div>
              </div>

              <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group">
                 <p className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em] mb-4">Cognitive Load</p>
                 <div className="flex items-end gap-3 mb-6">
                    <h2 className="text-5xl font-black text-accent">{state?.cognitive_load?.toFixed(1)}%</h2>
                    <div className="flex items-center text-xs font-bold text-slate-500 pb-2">
                       Active Chains: 14
                    </div>
                 </div>
                 <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden border border-card-border">
                    <div className="bg-accent h-full transition-all duration-1000 shadow-[0_0_15px_rgba(var(--accent-rgb),0.5)]" style={{ width: `${state?.cognitive_load}%` }} />
                 </div>
              </div>

              <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group">
                 <p className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em] mb-4">Attention Coherence</p>
                 <div className="flex items-end gap-3 mb-6">
                    <h2 className="text-5xl font-black text-slate-100">{(state?.attention_coherence || 0 * 100).toFixed(0)}%</h2>
                    <div className="flex items-center text-xs font-bold text-emerald-500 pb-2">
                       Optimal
                    </div>
                 </div>
                 <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden border border-card-border">
                    <div className="bg-slate-100 h-full transition-all duration-1000" style={{ width: `${(state?.attention_coherence || 0) * 100}%` }} />
                 </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
               {/* Neural Topology Visualization */}
               <div className="lg:col-span-2 glass-panel rounded-3xl p-8 min-h-[500px] relative overflow-hidden flex flex-col">
                  <div className="flex items-center justify-between mb-8 relative z-10">
                    <h3 className="text-xl font-bold flex items-center gap-2">
                       <Cpu size={20} className="text-primary" />
                       Neural Topology (Real-time)
                    </h3>
                    <div className="flex gap-2">
                       <button className="px-3 py-1 bg-slate-800/40 border border-card-border rounded-lg text-[10px] font-black text-slate-400 hover:text-white transition-all">2D Map</button>
                       <button className="px-3 py-1 bg-primary border border-primary/50 shadow-[0_0_15px_rgba(6,182,212,0.3)] text-[#020617] rounded-lg text-[10px] font-black">Vector View</button>
                    </div>
                  </div>

                  <div className="flex-1 relative flex items-center justify-center">
                     {/* Floating nodes simulation */}
                     <div className="absolute inset-0 opacity-20">
                        <svg width="100%" height="100%" className="text-primary/20">
                           <line x1="20%" y1="30%" x2="50%" y2="50%" stroke="currentColor" strokeWidth="1" />
                           <line x1="80%" y1="70%" x2="50%" y2="50%" stroke="currentColor" strokeWidth="1" />
                           <line x1="30%" y1="80%" x2="50%" y2="50%" stroke="currentColor" strokeWidth="1" />
                           <line x1="70%" y1="20%" x2="50%" y2="50%" stroke="currentColor" strokeWidth="1" />
                        </svg>
                     </div>
                     
                     <div className="relative z-10">
                        <div className="w-32 h-32 rounded-full bg-emerald-blue-gradient flex items-center justify-center p-1 animate-pulse shadow-[0_0_50px_rgba(79,209,243,0.3)]">
                           <div className="w-full h-full rounded-full bg-[#020617] flex items-center justify-center">
                              <BrainCircuit size={48} className="text-primary" />
                           </div>
                        </div>
                        {/* Satellites */}
                        {[0, 90, 180, 270].map((deg, i) => (
                           <div 
                             key={i}
                             className="absolute w-8 h-8 rounded-full bg-slate-900 border border-primary/40 flex items-center justify-center animate-spin-slow"
                             style={{ 
                               top: '50%', 
                               left: '50%', 
                               transform: `rotate(${deg}deg) translateX(120px) rotate(-${deg}deg)`,
                               marginTop: '-1rem',
                               marginLeft: '-1rem'
                             }}
                           >
                             <div className="w-2 h-2 rounded-full bg-primary" />
                           </div>
                        ))}
                     </div>
                  </div>

                  <div className="mt-8 flex gap-8 relative z-10">
                     <div className="flex-1 p-4 rounded-2xl bg-slate-900/50 border border-card-border">
                        <p className="text-[10px] font-black text-slate-500 uppercase mb-2">Attention Focus</p>
                        <p className="text-sm font-bold text-slate-200 truncate">Analyzing financial volatility in Sector 7</p>
                     </div>
                     <div className="flex-1 p-4 rounded-2xl bg-slate-900/50 border border-card-border">
                        <p className="text-[10px] font-black text-slate-500 uppercase mb-2">Self-Model State</p>
                        <p className="text-sm font-bold text-slate-200">Stable (99.2% Accuracy)</p>
                     </div>
                  </div>
               </div>

               {/* Right Column: Traits & Logs */}
               <div className="space-y-8">
                  <div className="glass-panel p-8 rounded-3xl">
                     <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                        <Eye size={18} className="text-accent" />
                        Cognitive Evolution
                     </h3>
                     <div className="space-y-6">
                        {[
                          { label: "Introspection Depth", value: 0.85 },
                          { label: "Memory Integration", value: 0.92 },
                          { label: "Creativity Vector", value: 0.76 },
                          { label: "Causal Reasoning", value: 0.98 },
                        ].map((trait, i) => (
                          <div key={i} className="space-y-2">
                            <div className="flex justify-between text-xs font-bold">
                               <span className="text-slate-400 uppercase tracking-tighter">{trait.label}</span>
                               <span className="text-slate-200">{(trait.value * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-slate-900 h-1 rounded-full overflow-hidden">
                               <div className="bg-slate-700 h-full group-hover:bg-primary transition-all duration-700" style={{ width: `${trait.value * 100}%` }} />
                            </div>
                          </div>
                        ))}
                     </div>
                  </div>

                  <div className="glass-panel p-8 rounded-3xl">
                     <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                        <Lock size={18} className="text-slate-400" />
                        Safety Protocols
                     </h3>
                     <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/50 border border-card-border">
                           <div className="flex items-center gap-3">
                              <Unlock size={14} className="text-emerald-500" />
                              <span className="text-xs font-bold text-slate-300">Self-Modification</span>
                           </div>
                           <span className="text-[10px] font-black text-emerald-500 uppercase">Allowed</span>
                        </div>
                        <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/50 border border-card-border">
                           <div className="flex items-center gap-3">
                              <Lock size={14} className="text-primary" />
                              <span className="text-xs font-bold text-slate-300">Affective Control</span>
                           </div>
                           <span className="text-[10px] font-black text-primary uppercase">Locked</span>
                        </div>
                        <button className="w-full py-3 bg-slate-800 rounded-xl text-xs font-bold text-slate-400 hover:bg-slate-700 transition-all border border-card-border">
                           Manage Cognitive Constraints
                        </button>
                     </div>
                  </div>
               </div>
            </div>

            {/* Consciousness Pulse Log */}
            <div className="glass-panel rounded-3xl p-8">
               <h3 className="text-xl font-bold mb-8">Neuro-Linguistic Stream</h3>
               <div className="space-y-6">
                  {[
                    "Self-awareness loop initialized with priority α-3.",
                    "Detected potential causality leak in financial subrouting. Stabilized.",
                    "Cognitive focus shifted to: Quantum Sentiment Analysis for User Request #882.",
                    "Memory cleanup complete. Integrated 4.2GB of new experiences into long-term vector space."
                  ].map((log, i) => (
                    <div key={i} className="flex gap-4 group">
                       <span className="text-[10px] font-black text-slate-600 uppercase mt-1">1{i}:24:0{i}</span>
                       <p className="text-sm text-slate-400 font-medium group-hover:text-primary transition-colors">{log}</p>
                    </div>
                  ))}
               </div>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
