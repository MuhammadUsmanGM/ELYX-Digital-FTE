"use client";

import { useEffect, useState } from "react";
import { 
  Activity, 
  BrainCircuit, 
  CheckCircle2,
  Globe2, 
  ShieldCheck, 
  MoreVertical,
  Loader2,
  ArrowUpRight,
  ChevronRight,
  Zap,
  Clock,
  LayoutGrid,
  TrendingUp,
  Cpu,
  RefreshCw,
  Bell
} from "lucide-react";
import { fetchDashboardData, fetchTasks, fetchApprovals } from "@/lib/api";
import { DashboardData, Task, ApprovalRequest } from "@/lib/types";
import DashboardLayout from "@/components/DashboardLayout";
import { toast } from "react-hot-toast";
import LoadingDots from "@/components/LoadingDots";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadDashboard = async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true);
      const [dashData, taskList, approvalList] = await Promise.all([
        fetchDashboardData(),
        fetchTasks(),
        fetchApprovals()
      ]);
      setData(dashData);
      setTasks(taskList);
      setApprovals(approvalList);
      if (isRefresh) {
        toast.success("Neural Core Synchronized", {
          id: 'sync-success',
          icon: '⚡',
        });
      }
    } catch (error) {
      console.error("Dashboard error:", error);
      toast.error("Handshake Failed: Neural Core unreachable");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboard();
    const interval = setInterval(() => loadDashboard(true), 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 px-2">
          <div className="space-y-2">
            <h1 className="text-5xl font-black tracking-tighter text-white">
              Mission <span className="text-primary italic">Control</span>
            </h1>
            <p className="text-slate-500 font-medium max-w-xl">
              Operational oversight for <span className="text-slate-300 font-bold">ELYX-v2</span>. Currently synthesizing {data?.tasks.active_chains || 0} autonomous decision chains across primary timelines.
            </p>
          </div>
          <div className="flex items-center gap-4">
             <div className="hidden lg:flex flex-col items-end px-6 border-r border-card-border/50">
                <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Uptime Strength</span>
                <span className="text-emerald-500 font-black text-sm">{data?.health.status === 'healthy' ? '99.98%' : 'WARNING'}</span>
             </div>
             <button 
               onClick={() => loadDashboard(true)}
               disabled={refreshing}
               className="btn-premium-primary !px-6 !py-4 shadow-[0_0_30px_rgba(6,182,212,0.2)] hover:shadow-[0_0_50px_rgba(6,182,212,0.4)] transition-all group min-w-[200px]"
             >
               {refreshing ? (
                 <div className="flex items-center gap-1">
                   <RefreshCw size={16} className="animate-spin text-white mr-2" />
                   <span className="text-[10px] font-black uppercase tracking-[0.2em] font-outfit flex items-center">
                     Handshake
                     <LoadingDots />
                   </span>
                 </div>
               ) : (
                 <>
                   <Zap size={18} className="group-hover:fill-current transition-colors" />
                   <span className="font-outfit text-xs font-black uppercase tracking-widest">Sync Neural Core</span>
                 </>
               )}
             </button>
          </div>
        </div>

        {/* Top-Level Grid Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard 
            label="Neural Stability" 
            value={`${data?.consciousness.phi.toFixed(1) || "..."}%`}
            icon={<BrainCircuit />}
            trend="+1.2%"
            color="primary"
          />
          <StatCard 
            label="Infinite Tasks" 
            value={data?.tasks.active_chains.toString() || "..."}
            icon={<LayoutGrid />}
            trend="Active Now"
            color="accent"
          />
          <StatCard 
            label="Reality Coherence" 
            value={data?.reality.stability_index.toFixed(3) || "..."}
            icon={<Globe2 />}
            trend="Stable"
            color="emerald"
          />
          <StatCard 
            label="Control Requests" 
            value={data?.tasks.pending_count.toString() || "..."}
            icon={<ShieldCheck />}
            trend="Urgent"
            color="red"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Main Content: Activity & Timeline */}
          <div className="lg:col-span-8 space-y-8">
            
            {/* Consciousness Pulse visualizer (Central Dashboard Piece) */}
            <div className="glass-panel rounded-[2.5rem] p-10 relative overflow-hidden group border-primary/20 bg-primary/[0.01]">
               <div className="absolute inset-0 bg-gradient-to-br from-primary/[0.03] to-transparent pointer-events-none" />
               <div className="flex items-center justify-between mb-8 relative z-10">
                 <div>
                    <h2 className="text-2xl font-black text-white flex items-center gap-3">
                      <Activity className="text-primary animate-pulse" size={24} />
                      Consciousness Pulse
                    </h2>
                    <p className="text-xs text-slate-500 font-bold mt-1 uppercase tracking-widest">Self-Reflective Loop Monitoring</p>
                 </div>
                 <div className="flex items-center gap-4">
                    <div className="text-right">
                       <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Attention Scope</p>
                       <p className="text-xs font-bold text-slate-300">Market Dynamics, Causal Risk</p>
                    </div>
                 </div>
               </div>

               {loading ? (
                 <div className="flex flex-col items-center justify-center h-48 gap-4">
                   <Loader2 size={32} className="text-primary animate-spin" />
                   <p className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] flex items-center">Mapping Neural Topography<LoadingDots /></p>
                 </div>
               ) : (
                 <div className="relative h-32 flex items-end gap-1.5 px-2 mb-6">
                    {Array.from({ length: 48 }).map((_, i) => (
                      <div 
                        key={i} 
                        className="flex-1 bg-primary/20 rounded-full hover:bg-primary transition-all duration-300 group/bar relative"
                        style={{ height: `${20 + Math.random() * 80}%` }}
                      >
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 p-1.5 rounded-md bg-slate-900 border border-card-border opacity-0 group-hover/bar:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                           <p className="text-[8px] font-black text-primary">SIG: {Math.random().toFixed(4)}</p>
                        </div>
                      </div>
                    ))}
                 </div>
               )}

               <div className="flex items-center justify-between pt-8 border-t border-card-border/30 relative z-10">
                  <div className="flex gap-4">
                     <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900/50 border border-card-border">
                        <TrendingUp size={14} className="text-emerald-500" />
                        <span className="text-[10px] font-black text-slate-300 uppercase">Growth Prophecy: Positive</span>
                     </div>
                     <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900/50 border border-card-border">
                        <Cpu size={14} className="text-primary" />
                        <span className="text-[10px] font-black text-slate-300 uppercase">Latency: 42ms</span>
                     </div>
                  </div>
                  <button className="flex items-center gap-2 text-[10px] font-black text-slate-500 uppercase hover:text-primary transition-all group">
                    Full Neuro-Audit <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                  </button>
               </div>
            </div>

            {/* Neural Action Logs (Futuristic Activity Feed) */}
            <div className="glass-panel rounded-[2.5rem] p-10 border-card-border/30">
               <div className="flex items-center justify-between mb-10">
                  <div className="flex items-center gap-3">
                     <div className="w-10 h-10 rounded-2xl bg-slate-900 border border-card-border flex items-center justify-center text-primary">
                        <Clock size={20} />
                     </div>
                     <h3 className="text-xl font-black text-white">Neural Action Logs</h3>
                  </div>
                  <button className="text-[10px] font-black text-slate-500 uppercase tracking-widest hover:text-primary transition-all border-b border-transparent hover:border-primary">View Full Archive</button>
               </div>

               <div className="space-y-6">
                 {loading ? (
                    <div className="flex flex-col items-center justify-center py-10 opacity-30">
                       <Loader2 size={32} className="animate-spin mb-2" />
                       <span className="text-[10px] font-black tracking-widest uppercase flex items-center">Fetching Logs<LoadingDots /></span>
                    </div>
                 ) : (
                    <>
                      <LogItem 
                        type="CAUSAL" 
                        title="Self-Reflection Loop Converged" 
                        desc="Analyzed 4,202 data points to optimize LinkedIn engagement strategy for Q1." 
                        time="Just Now" 
                        status="success"
                      />
                      <LogItem 
                        type="REALITY" 
                        title="Scenario Prophet Sync" 
                        desc="Virtual scenario #882 'Market Volatility' successfully merged with primary business vector." 
                        time="12m ago" 
                        status="success"
                      />
                      <LogItem 
                        type="SECURITY" 
                        title="Causal Chain Encryption" 
                        desc="Rotated quantum keys across all distributed decision nodes. Integrity confirmed." 
                        time="42m ago" 
                        status="success"
                      />
                      <LogItem 
                         type="CONTROL" 
                         title="Manual Override Required" 
                         desc="Large-scale transaction identified on Node-7 requires high-tier human verification." 
                         time="1h ago" 
                         status="warning"
                      />
                    </>
                 )}
               </div>
            </div>
          </div>

          {/* Right Column: Mini-Tools & Quick Access */}
          <div className="lg:col-span-4 space-y-8">
            
            {/* Pending Controls (Integrated Approvals) */}
            <div className="glass-panel p-8 rounded-[2rem] border-red-500/10 bg-red-500/[0.01]">
               <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-black text-white flex items-center gap-3">
                     <ShieldCheck className="text-red-500" size={20} />
                     Control Gate
                  </h3>
                  <span className="px-2 py-1 rounded bg-red-500/10 text-[9px] font-black text-red-500 uppercase tracking-widest">
                     {data?.tasks.pending_count || 0} Pending
                  </span>
               </div>
               
               <div className="space-y-4 mb-6">
                  {approvals.slice(0, 3).map((approval) => (
                    <div key={approval.id} className="p-4 rounded-2xl bg-slate-900/80 border border-card-border/50 group hover:border-red-500/30 transition-all cursor-pointer">
                       <div className="flex items-center justify-between mb-2">
                          <span className="text-[10px] font-black text-red-500 uppercase tracking-widest">{approval.type}</span>
                          <span className="text-[9px] font-bold text-slate-500">{new Date(approval.created).toLocaleTimeString()}</span>
                       </div>
                       <p className="text-xs font-bold text-slate-200 mb-1 group-hover:text-red-400 transition-colors uppercase truncate">{approval.action}</p>
                       <p className="text-[10px] text-slate-500 line-clamp-1">{approval.reason}</p>
                    </div>
                  ))}
                  {approvals.length === 0 && (
                    <div className="text-center py-6 border-2 border-dashed border-card-border/20 rounded-2xl">
                       <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">No Active Blocks</p>
                    </div>
                  )}
               </div>
               
               <button className="w-full py-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-[10px] font-black text-red-500 uppercase tracking-widest hover:bg-red-500 hover:text-white transition-all shadow-lg shadow-red-500/5">
                  Enter Command Interface
               </button>
            </div>

            {/* Quick Actions / Nodes */}
            <div className="glass-panel p-8 rounded-[2rem] border-card-border/30">
               <h3 className="text-lg font-black text-white mb-6">Quick Sync</h3>
               <div className="grid grid-cols-2 gap-4">
                  <QuickTool icon={<Globe2 size={18} />} label="Reality Matrix" link="/reality" />
                  <StatCardSmall icon={<ShieldCheck size={18} />} label="Infra Security" link="/security" />
                  <QuickTool icon={<Bell size={18} />} label="Alert Neural" link="/notifications" />
                  <QuickTool icon={<BrainCircuit size={18} />} label="AI Core" link="/settings" />
               </div>
            </div>

            {/* System Resources */}
            <div className="glass-panel p-8 rounded-[2rem] border-card-border/30">
               <div className="flex items-center justify-between mb-8">
                  <h3 className="text-lg font-black text-white">Neural Load</h3>
                  <div className="w-10 h-10 rounded-full bg-slate-900 border border-card-border flex items-center justify-center text-primary italic font-black text-xs">
                    {(Math.random() * 20 + 70).toFixed(0)}%
                  </div>
               </div>
               
               <div className="space-y-6">
                  <ResourceItem label="Compute Cycles" value={82} color="bg-primary" />
                  <ResourceItem label="Memory Density" value={64} color="bg-accent" />
                  <ResourceItem label="Causal Throughput" value={91} color="bg-emerald-500" />
               </div>
            </div>

          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

function StatCard({ label, value, icon, trend, color }: any) {
  const colorMap: any = {
    primary: "text-primary border-primary/20",
    accent: "text-accent border-accent/20",
    emerald: "text-emerald-500 border-emerald-500/20",
    red: "text-red-500 border-red-500/20",
  };

  return (
    <div className="glass-panel p-8 rounded-[2.5rem] group premium-hover transition-all">
      <div className="flex items-center justify-between mb-6">
        <div className={`p-3 rounded-2xl bg-slate-900 border border-card-border ${colorMap[color].split(' ')[0]} group-hover:shadow-[0_0_20px_rgba(6,182,212,0.1)] transition-all`}>
          {icon}
        </div>
        <div className="text-right">
           <p className={`text-[10px] font-black uppercase tracking-widest ${colorMap[color].split(' ')[0]}`}>{trend}</p>
        </div>
      </div>
      <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1">{label}</p>
      <h3 className={`text-4xl font-black text-slate-100 tracking-tighter`}>{value}</h3>
    </div>
  );
}

function LogItem({ type, title, desc, time, status }: any) {
  return (
    <div className="flex gap-6 group">
      <div className="flex flex-col items-center">
        <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-[10px] font-black border-card-border/30 bg-slate-950 transition-colors ${
          status === 'warning' ? 'text-red-500 group-hover:bg-red-500 group-hover:text-white' : 'text-primary group-hover:bg-primary group-hover:text-slate-950'
        }`}>
          {type[0]}
        </div>
        <div className="w-px flex-1 bg-card-border/20 my-2" />
      </div>
      <div className="flex-1 pb-8">
        <div className="flex items-center justify-between mb-2">
          <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">{type} PROTOCOL</p>
          <p className="text-[10px] font-bold text-slate-600">{time}</p>
        </div>
        <h4 className="text-sm font-black text-slate-100 mb-2 uppercase tracking-wide group-hover:text-primary transition-colors">{title}</h4>
        <p className="text-xs text-slate-500 leading-relaxed font-medium">{desc}</p>
      </div>
    </div>
  );
}

function QuickTool({ icon, label, link }: any) {
  return (
    <a href={link} className="flex flex-col items-center justify-center p-6 rounded-3xl bg-slate-900/50 border border-card-border hover:border-primary/50 hover:bg-slate-900 transition-all group">
      <div className="text-slate-500 group-hover:text-primary transition-colors mb-3">
        {icon}
      </div>
      <span className="text-[9px] font-black text-slate-500 group-hover:text-slate-300 uppercase tracking-widest text-center">{label}</span>
    </a>
  );
}

function StatCardSmall({ icon, label, link }: any) {
  return (
    <a href={link} className="flex flex-col items-center justify-center p-6 rounded-3xl bg-slate-900/50 border border-card-border hover:border-primary/50 hover:bg-slate-900 transition-all group">
      <div className="text-slate-500 group-hover:text-primary transition-colors mb-3">
        {icon}
      </div>
      <span className="text-[9px] font-black text-slate-500 group-hover:text-slate-300 uppercase tracking-widest text-center">{label}</span>
    </a>
  );
}

function ResourceItem({ label, value, color }: any) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-[10px] font-black uppercase tracking-widest text-slate-500">
        <span>{label}</span>
        <span className="text-slate-300">{value}%</span>
      </div>
      <div className="w-full h-1 bg-slate-900 rounded-full overflow-hidden">
        <div className={`h-full ${color} transition-all duration-1000`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}
