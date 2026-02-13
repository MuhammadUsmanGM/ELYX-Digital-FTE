"use client";

import { useEffect, useState, useMemo } from "react";
import { 
  Globe2, 
  Orbit, 
  GitBranch, 
  Zap, 
  Anchor, 
  AlertTriangle, 
  ChevronRight, 
  History,
  Target,
  RefreshCcw,
  Plus,
  ArrowUpRight,
  Loader2,
  Atom,
  Binary,
  Layers,
  Sparkles
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { fetchRealityStatus, fetchRealityScenarios } from "@/lib/api";
import { RealityStatus, RealityScenario } from "@/lib/types";
import LoadingDots from "@/components/LoadingDots";

export default function RealityPage() {
  const [status, setStatus] = useState<RealityStatus | null>(null);
  const [scenarios, setScenarios] = useState<RealityScenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [activeScenario, setActiveScenario] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [resStatus, resScenarios] = await Promise.all([
        fetchRealityStatus(),
        fetchRealityScenarios()
      ]);
      setStatus(resStatus);
      setScenarios(resScenarios);
    } catch (error) {
      console.error("Reality fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const runSimulation = () => {
    setSimulating(true);
    setTimeout(() => {
      setSimulating(false);
      loadData();
    }, 3000);
  };

  const statusColors: Record<string, string> = {
    anchored: 'text-emerald-500 border-emerald-500/20 bg-emerald-500/5',
    simulating: 'text-primary border-primary/20 bg-primary/5',
    diverged: 'text-red-500 border-red-500/20 bg-red-500/5',
    stable: 'text-accent border-accent/20 bg-accent/5',
  };

  const timelineStats = useMemo(() => [
    { label: "Causal Chains", value: "14,822", trend: "+2.4%", color: "text-primary" },
    { label: "Reality Divergence", value: "0.04%", trend: "-8%", color: "text-emerald-500" },
    { label: "Simulated Outcomes", value: "1.2M", trend: "+124", color: "text-purple-500" },
  ], []);

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
        
        {/* Futuristic Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 px-2">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center text-accent">
                <Globe2 size={24} />
              </div>
              <h1 className="text-4xl font-black tracking-tight text-white italic underline decoration-accent/30 underline-offset-8">Reality Simulation Lab</h1>
            </div>
            <p className="text-slate-400 font-medium max-w-2xl">
              Advanced causal modeling and multi-timeline forecasting engine. Control primary continuity and explore divergent business outcomes.
            </p>
          </div>
          <div className="flex gap-4">
             <button 
               onClick={runSimulation}
               disabled={simulating}
               className="group relative px-8 py-4 bg-slate-950 border border-accent/30 rounded-2xl font-black text-xs uppercase tracking-widest text-accent overflow-hidden transition-all hover:border-accent hover:shadow-[0_0_30px_rgba(245,158,11,0.2)] active:scale-95 disabled:opacity-50"
             >
               <span className="relative z-10 flex items-center gap-2">
                 {simulating ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                  {simulating ? <span className="flex items-center">Projecting Timelines<LoadingDots /></span> : "Initiate Causal Projection"}
               </span>
               <div className="absolute inset-0 bg-accent/10 opacity-0 group-hover:opacity-100 transition-opacity" />
             </button>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center p-40 gap-8">
            <div className="relative">
              <Orbit size={80} className="text-accent animate-spin-slow opacity-20" />
              <Atom size={40} className="text-primary absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
            </div>
            <div className="text-center space-y-2">
               <p className="text-slate-200 font-black uppercase tracking-[0.4em] text-sm flex items-center">Synchronizing Reality Anchors<LoadingDots /></p>
               <p className="text-slate-500 text-xs font-mono flex items-center">Collapsing probability waves<LoadingDots /></p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* Sidebar: Integrity & Metrics */}
            <div className="lg:col-span-3 space-y-6">
              <div className="glass-panel p-8 rounded-[2.5rem] border-primary/20 relative overflow-hidden group">
                <div className="absolute -top-12 -right-12 p-4 opacity-[0.03] group-hover:scale-110 transition-transform duration-1000">
                  <Globe2 size={200} />
                </div>
                
                <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-8 flex items-center gap-2">
                  <Layers size={14} className="text-primary" />
                  Primary Continuity
                </h3>
                  
                <div className="space-y-10">
                  <div className="relative">
                    <p className="text-[10px] font-black text-slate-500 uppercase mb-4 tracking-tighter">Stability Index</p>
                    <div className="flex items-baseline gap-2">
                      <h2 className="text-5xl font-black text-white tracking-tighter">{(status?.stability_index || 0).toFixed(2)}</h2>
                      <span className="text-emerald-500 font-black text-[10px] uppercase tracking-widest flex items-center">
                        <ArrowUpRight size={14} /> Stable
                      </span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex justify-between items-end">
                      <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Anchoring Strength</p>
                      <p className="text-[10px] font-black text-primary uppercase">{(status?.anchoring_strength || 0 * 100).toFixed(1)}%</p>
                    </div>
                    <div className="w-full bg-slate-900/80 h-1.5 rounded-full overflow-hidden border border-card-border/50">
                      <div className="bg-primary h-full shadow-[0_0_10px_rgba(6,182,212,0.5)]" style={{ width: `${(status?.anchoring_strength || 0) * 100}%` }} />
                    </div>
                  </div>

                  <div className="p-5 rounded-3xl bg-slate-950/50 border border-card-border/30 backdrop-blur-sm group-hover:border-primary/30 transition-all">
                    <div className="flex items-center gap-2 text-emerald-500 mb-3">
                      <Zap size={14} className="fill-emerald-500/20" />
                      <span className="text-[10px] font-black uppercase tracking-[0.2em]">Core Sync: Active</span>
                    </div>
                    <p className="text-[10px] text-slate-500 leading-relaxed font-medium">
                      Continuous real-time synchronization with 14,822 causal nodes.
                    </p>
                  </div>
                </div>
              </div>

              {/* Boundary Logs */}
              <div className="glass-panel p-6 rounded-[2rem] border-card-border/20">
                <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-6 flex items-center justify-between">
                  Log Diagnostics
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                </h4>
                <div className="space-y-5">
                  <LogItem label="Paradox Risk" value="0.00018%" status="safe" />
                  <LogItem label="Causal Loop" value="None detected" status="safe" />
                  <LogItem label="Timeline Drift" value="0.02mm/dec" status="safe" />
                  <LogItem label="Quantum Flux" value="Optimal" status="safe" />
                </div>
              </div>
            </div>

            {/* Main Area: Timeline Scenarios */}
            <div className="lg:col-span-9 space-y-8">
               
               {/* Metrics Row */}
               <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {timelineStats.map((stat, i) => (
                    <div key={i} className="glass-panel p-6 rounded-3xl border-card-border/30 flex items-center justify-between">
                      <div>
                        <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">{stat.label}</p>
                        <h4 className="text-xl font-black text-slate-100">{stat.value}</h4>
                      </div>
                      <div className={`text-[10px] font-black px-2 py-1 rounded-lg bg-slate-900 border border-card-border ${stat.color}`}>
                        {stat.trend}
                      </div>
                    </div>
                  ))}
               </div>

               {/* Scenario Selection */}
               <div className="space-y-6">
                  <div className="flex items-center justify-between px-2">
                    <h3 className="text-xl font-black text-white flex items-center gap-3">
                      <GitBranch size={22} className="text-primary rotate-180" />
                      Forecasted Scenario Branches
                    </h3>
                    <div className="flex gap-3">
                      <select className="bg-slate-900 border border-card-border rounded-xl px-4 py-2 text-[10px] font-black text-slate-500 uppercase tracking-widest outline-none focus:border-primary transition-all">
                        <option>All Probability Paths</option>
                        <option>High Impact Only</option>
                        <option>Strategic Vectors</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {scenarios.map((s) => (
                      <ScenarioCard 
                        key={s.id} 
                        scenario={s} 
                        active={activeScenario === s.id}
                        onClick={() => setActiveScenario(s.id)}
                      />
                    ))}
                  </div>
               </div>

               {/* Causal Projection Canvas (Interactive look) */}
               <div className="glass-panel rounded-[3rem] p-10 relative overflow-hidden group border-accent/20 bg-accent/[0.01]">
                  <div className="absolute inset-0 bg-gradient-to-br from-accent/[0.03] to-transparent pointer-events-none" />
                  
                  <div className="flex items-center justify-between mb-10 relative z-10">
                    <div>
                      <h3 className="text-xl font-black text-white flex items-center gap-3">
                        <Orbit size={24} className="text-accent group-hover:rotate-180 transition-transform duration-1000" />
                        Interactive Causal Matrix
                      </h3>
                      <p className="text-xs text-slate-500 font-medium mt-1">Simulating multidimensional impact of selected scenario on primary timeline.</p>
                    </div>
                    <div className="px-4 py-2 bg-slate-950 border border-card-border rounded-2xl flex items-center gap-3">
                      <div className="w-2 h-2 rounded-full bg-accent animate-ping" />
                      <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest">Processing Matrix-V4</span>
                    </div>
                  </div>

                  {/* Causal Grid Visualization */}
                  <div className="relative h-[350px] mb-8 bg-slate-950/40 rounded-[2rem] border border-card-border/30 overflow-hidden group/canvas">
                    <div className="absolute inset-0 grid grid-cols-12 grid-rows-6 gap-px opacity-10">
                      {Array.from({ length: 72 }).map((_, i) => (
                        <div key={i} className="border-[0.5px] border-slate-500" />
                      ))}
                    </div>
                    
                    {/* Simulated Causal Points */}
                    <div className="absolute inset-0 flex items-center justify-center">
                       <div className="relative w-full h-full">
                          {Array.from({ length: 8 }).map((_, i) => (
                            <CausalPoint 
                              key={i} 
                              top={`${Math.random() * 80 + 10}%`} 
                              left={`${Math.random() * 80 + 10}%`} 
                              delay={i * 0.5}
                            />
                          ))}
                          <svg className="absolute inset-0 w-full h-full opacity-30 pointer-events-none">
                             <line x1="20%" y1="30%" x2="50%" y2="50%" stroke="currentColor" className="text-accent" strokeWidth="0.5" strokeDasharray="4 4" />
                             <line x1="80%" y1="20%" x2="50%" y2="50%" stroke="currentColor" className="text-primary" strokeWidth="0.5" strokeDasharray="4 4" />
                             <line x1="10%" y1="80%" x2="50%" y2="50%" stroke="currentColor" className="text-purple-500" strokeWidth="0.5" strokeDasharray="4 4" />
                          </svg>
                       </div>
                    </div>

                    <div className="absolute bottom-8 right-8 text-right">
                       <p className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em]">Neural Topology</p>
                       <p className="text-[8px] font-mono text-slate-700">COORDSET: {Math.random().toFixed(4)}, {Math.random().toFixed(4)}</p>
                    </div>
                  </div>

                  {/* Warning Bar */}
                  <div className="p-6 rounded-[2rem] bg-red-500/5 border border-red-500/20 flex items-center justify-between backdrop-blur-sm relative z-10">
                    <div className="flex items-center gap-5">
                      <div className="w-12 h-12 rounded-2xl bg-red-500/10 flex items-center justify-center text-red-500 shadow-[0_0_20px_rgba(239,68,68,0.2)]">
                        <AlertTriangle size={24} />
                      </div>
                      <div>
                        <p className="text-sm font-black text-slate-100 uppercase tracking-tight">Timeline Divergence Detected</p>
                        <p className="text-[10px] text-slate-500 font-medium">Branch "Market Anomaly-G" shows 82% divergence risk in Q3 forecasting.</p>
                      </div>
                    </div>
                    <button className="px-6 py-3 bg-red-500 text-white rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-white hover:text-red-500 transition-all shadow-lg shadow-red-500/20 active:scale-95">
                      Anchor Branch Now
                    </button>
                  </div>
               </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

function LogItem({ label, value, status }: any) {
  return (
    <div className="flex items-center justify-between group">
      <span className="text-[10px] font-bold text-slate-500 group-hover:text-slate-300 transition-colors uppercase tracking-tight">{label}</span>
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-black text-slate-200 uppercase">{value}</span>
        <div className={`w-1 h-1 rounded-full ${status === 'safe' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
      </div>
    </div>
  );
}

function ScenarioCard({ scenario, active, onClick }: { scenario: RealityScenario, active: boolean, onClick: () => void }) {
  const statusColors: Record<string, string> = {
    anchored: 'text-emerald-500 border-emerald-500/20 bg-emerald-500/10',
    simulating: 'text-primary border-primary/20 bg-primary/10',
    diverged: 'text-red-500 border-red-500/20 bg-red-500/10',
    stable: 'text-accent border-accent/20 bg-accent/10',
  };

  return (
    <div 
      onClick={onClick}
      className={`glass-panel p-8 rounded-[2.5rem] transition-all duration-500 cursor-pointer group relative overflow-hidden border-2 ${
        active ? 'border-primary/50 bg-primary/[0.02] shadow-[0_0_40px_rgba(6,182,212,0.1)]' : 'border-card-border/30 hover:border-primary/20'
      }`}
    >
      <div className="absolute top-0 right-0 w-48 h-48 bg-primary/5 blur-[80px] pointer-events-none group-hover:scale-125 transition-transform duration-1000" />
      
      <div className="flex items-start justify-between mb-8 relative z-10">
        <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border ${statusColors[scenario.status] || 'text-slate-500'}`}>
          {scenario.status}
        </span>
        <div className="flex flex-col items-end">
          <p className="text-[10px] font-black text-slate-600 uppercase tracking-tighter">Temporal ID</p>
          <p className="text-[10px] font-mono text-slate-500">{scenario.id}</p>
        </div>
      </div>

      <div className="relative z-10 mb-8">
        <h4 className="text-2xl font-black text-slate-100 mb-3 group-hover:text-primary transition-colors leading-tight">{scenario.name}</h4>
        <p className="text-xs text-slate-500 font-medium leading-relaxed line-clamp-2">{scenario.description}</p>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-8 relative z-10">
        <div className="p-5 rounded-3xl bg-slate-900/60 border border-card-border/50 group-hover:bg-slate-900 transition-colors">
          <p className="text-[10px] font-black text-slate-600 uppercase mb-2 tracking-[0.1em]">Impact Severity</p>
          <div className="flex items-center justify-between">
            <span className="text-xl font-black text-slate-200">{scenario.impact_score}%</span>
            <Target size={18} className="text-primary/40" />
          </div>
        </div>
        <div className="p-5 rounded-3xl bg-slate-900/60 border border-card-border/50 group-hover:bg-slate-900 transition-colors">
          <p className="text-[10px] font-black text-slate-600 uppercase mb-2 tracking-[0.1em]">Probability</p>
          <div className="flex items-center justify-between">
            <span className="text-xl font-black text-slate-200">{(scenario.probability * 100).toFixed(0)}%</span>
            <Orbit size={18} className="text-accent/40" />
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between pt-6 border-t border-card-border/30 relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-slate-900 border border-card-border flex items-center justify-center text-primary">
            <Layers size={14} />
          </div>
          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{scenario.type} Path</span>
        </div>
        <button className="flex items-center gap-2 text-[10px] font-black text-primary uppercase tracking-widest hover:gap-3 transition-all group-hover:text-white">
          Simulate Propagation
          <ChevronRight size={14} />
        </button>
      </div>
    </div>
  );
}

function CausalPoint({ top, left, delay }: any) {
  return (
    <div 
      className="absolute w-2 h-2 rounded-full animate-pulse group-hover/canvas:scale-150 transition-transform duration-500"
      style={{ 
        top, 
        left, 
        backgroundColor: Math.random() > 0.5 ? '#06b6d4' : '#f59e0b',
        boxShadow: `0 0 15px currentColor`,
        animationDelay: `${delay}s`
      }}
    />
  );
}
