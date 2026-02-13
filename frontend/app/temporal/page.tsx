"use client";

import { useEffect, useState } from "react";
import { 
  History, 
  Watch, 
  Calendar, 
  ArrowRight, 
  Clock, 
  ChevronRight, 
  Layers, 
  Play, 
  RotateCcw,
  Loader2,
  Activity,
  Zap,
  CheckCircle2
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { fetchTemporalTasks } from "@/lib/api";
import { TemporalTask } from "@/lib/types";
import LoadingDots from "@/components/LoadingDots";

export default function TemporalPage() {
  const [tasks, setTasks] = useState<TemporalTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'primary' | 'simulated' | 'historical'>('all');

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await fetchTemporalTasks();
      setTasks(data);
    } catch (error) {
      console.error("Temporal fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredTasks = tasks.filter(t => filter === 'all' || t.timeline === filter);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 size={16} className="text-emerald-500" />;
      case 'running': return <Loader2 size={16} className="text-primary animate-spin" />;
      case 'scheduled': return <Clock size={16} className="text-slate-500" />;
      default: return <Zap size={16} className="text-red-500" />;
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-in fade-in duration-700">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-4xl font-black tracking-tight mb-2">Temporal Hub</h1>
            <p className="text-slate-400 font-medium">Coordinate cross-timeline events and historical data synchronization.</p>
          </div>
          <div className="flex gap-3">
             <div className="glass-panel flex p-1 rounded-xl">
               {(['all', 'primary', 'simulated', 'historical'] as const).map((f) => (
                 <button 
                   key={f}
                   onClick={() => setFilter(f)}
                   className={`px-4 py-2 rounded-lg text-[10px] font-black uppercase transition-all ${
                     filter === f ? 'bg-primary text-slate-950' : 'text-slate-500 hover:text-slate-300'
                   }`}
                 >
                   {f}
                 </button>
               ))}
             </div>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center p-40 gap-4">
            <Loader2 size={48} className="text-primary animate-spin" />
            <p className="text-slate-500 font-bold flex items-center">Synchronizing clocks<LoadingDots /></p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Timeline Stream */}
            <div className="lg:col-span-2 space-y-6">
               <div className="glass-panel rounded-3xl p-8">
                  <h3 className="text-lg font-bold mb-8 flex items-center gap-2">
                    <History size={20} className="text-primary" />
                    Event Chronology
                  </h3>

                  <div className="space-y-0 relative">
                     {/* The timeline line */}
                     <div className="absolute left-[21px] top-4 bottom-4 w-0.5 bg-slate-800" />

                     {filteredTasks.map((task, i) => (
                       <div key={task.id} className="relative pl-12 pb-10 group last:pb-0">
                          {/* Timeline Dot */}
                          <div className={`absolute left-0 top-1 w-11 h-11 rounded-full bg-[#020617] border-2 flex items-center justify-center z-10 transition-all ${
                            task.status === 'running' ? 'border-primary shadow-[0_0_15px_rgba(79,209,243,0.3)]' : 'border-slate-800'
                          }`}>
                             {getStatusIcon(task.status)}
                          </div>

                          <div className="glass-panel p-6 rounded-2xl group-hover:border-primary/30 transition-all">
                             <div className="flex items-center justify-between mb-2">
                                <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
                                   {new Date(task.scheduled_time).toLocaleString()}
                                </span>
                                <span className={`px-2 py-0.5 rounded text-[9px] font-black uppercase border ${
                                  task.timeline === 'primary' ? 'text-emerald-500 border-emerald-500/20' : 
                                  task.timeline === 'simulated' ? 'text-primary border-primary/20' : 
                                  'text-slate-500 border-slate-500/20'
                                }`}>
                                   {task.timeline}
                                </span>
                             </div>
                             <h4 className="text-lg font-bold text-slate-200 mb-4">{task.title}</h4>
                             
                             <div className="flex items-center justify-between mt-4 pt-4 border-t border-card-border/50">
                                <div className="flex items-center gap-4">
                                   <div>
                                      <p className="text-[9px] font-black text-slate-600 uppercase mb-1">Impact</p>
                                      <p className="text-xs font-bold text-slate-300">{(task.impact_coefficient * 100).toFixed(0)}%</p>
                                   </div>
                                   <div>
                                      <p className="text-[9px] font-black text-slate-600 uppercase mb-1">Priority</p>
                                      <p className="text-xs font-bold text-slate-300 capitalize">{task.priority}</p>
                                   </div>
                                </div>
                                <button className="p-2 hover:text-primary transition-colors">
                                   <ArrowRight size={18} />
                                </button>
                             </div>
                          </div>
                       </div>
                     ))}
                  </div>
               </div>
            </div>

            {/* Side Modules */}
            <div className="space-y-8">
               {/* Time Drift Module */}
               <div className="glass-panel p-8 rounded-3xl relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-4 opacity-5">
                    <Watch size={80} />
                  </div>
                  <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-6">Chronos Drift</h3>
                  
                  <div className="space-y-6">
                     <div className="text-center py-6">
                        <h2 className="text-5xl font-black text-slate-100 tabular-nums">0.000<span className="text-primary">42</span>s</h2>
                        <p className="text-[10px] font-bold text-slate-500 uppercase mt-2">Divergence from Atomic UTC</p>
                     </div>
                     <button className="w-full py-3 bg-primary/10 border border-primary/20 rounded-xl text-xs font-bold text-primary hover:bg-primary/20 transition-all flex items-center justify-center gap-2">
                        <RotateCcw size={14} />
                        Resync Temporal Anchor
                     </button>
                  </div>
               </div>

               {/* Upcoming Projection */}
               <div className="glass-panel p-8 rounded-3xl">
                  <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-6">Upcoming Eras</h3>
                  <div className="space-y-4">
                     {[
                       { era: "Q3 Expansion", date: "Sep 2026", prob: 0.92 },
                       { era: "Diamond v3.0", date: "Jan 2027", prob: 0.85 },
                       { era: "Global Singularity", date: "Mar 2028", prob: 0.12 },
                     ].map((e, i) => (
                        <div key={i} className="flex flex-col gap-2 p-4 rounded-2xl bg-slate-900/30 border border-card-border hover:bg-slate-900/50 transition-all cursor-pointer">
                           <div className="flex items-center justify-between">
                              <span className="text-sm font-bold text-slate-200">{e.era}</span>
                              <span className="text-[10px] font-black text-slate-600 uppercase">{e.date}</span>
                           </div>
                           <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                              <div className="bg-primary h-full opacity-50" style={{ width: `${e.prob * 100}%` }} />
                           </div>
                        </div>
                     ))}
                  </div>
               </div>

               {/* Archival Access */}
               <div className="glass-panel p-8 rounded-3xl border-slate-800/50">
                  <div className="flex items-center gap-3 mb-6">
                     <div className="p-2 rounded-lg bg-slate-900 text-slate-400">
                        <Layers size={18} />
                     </div>
                     <h3 className="text-lg font-bold">Historical Access</h3>
                  </div>
                  <p className="text-xs text-slate-500 leading-relaxed mb-6">
                     ELYX has preserved all company memory across 4.2TB of immutable causal chains.
                  </p>
                  <button className="w-full py-3 bg-slate-900 border border-card-border rounded-xl text-xs font-bold text-slate-300 hover:text-white transition-all flex items-center justify-center gap-2">
                     <Play size={14} />
                     Replay Past Decision
                  </button>
               </div>
            </div>

          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
