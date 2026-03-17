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
  Bell,
  Sparkles,
  Command,
  Fingerprint,
  AlertTriangle
} from "lucide-react";
import { fetchDashboardData, fetchTasks, fetchApprovals } from "@/lib/api";
import { DashboardData, Task, ApprovalRequest } from "@/lib/types";
import DashboardLayout from "@/components/DashboardLayout";
import { toast } from "react-hot-toast";
import LoadingDots from "@/components/LoadingDots";
import { motion, AnimatePresence } from "framer-motion";

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
        toast.success("System Core Synchronized", {
          id: 'sync-success',
          icon: '⚡',
        });
      }
    } catch (error) {
      console.error("Dashboard error:", error);
      toast.error("Handshake Failed: System Core unreachable");
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

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <DashboardLayout>
      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="space-y-10"
      >
        
        {/* Header Section */}
        <motion.div variants={itemVariants} className="flex flex-col xl:flex-row xl:items-end justify-between gap-8 px-2 relative group">
          <div className="absolute -top-20 -left-20 w-64 h-64 bg-primary/10 blur-[100px] rounded-full pointer-events-none group-hover:bg-primary/20 transition-all duration-1000" />
          <div className="space-y-3 relative z-10">
            <div className="flex items-center gap-3 mb-2">
              <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-[0.2em] flex items-center gap-2 border ${
                data?.dataSource === 'mock'
                  ? 'bg-amber-500/10 border-amber-500/20 text-amber-500'
                  : 'bg-primary/10 border-primary/20 text-primary'
              }`}>
                <div className={`w-1.5 h-1.5 rounded-full animate-pulse ${
                  data?.dataSource === 'mock'
                    ? 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,1)]'
                    : 'bg-primary shadow-[0_0_8px_rgba(6,182,212,1)]'
                }`} />
                {data?.dataSource === 'mock' ? 'Offline — Mock Data' : 'Live Network Active'}
              </span>
              <span className="px-3 py-1 bg-accent/10 border border-accent/20 rounded-full text-[10px] font-black text-accent uppercase tracking-[0.2em] flex items-center gap-2">
                <BrainCircuit size={10} />
                Claude 3.5 Sonnet
              </span>
              <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-[10px] font-black text-emerald-500 uppercase tracking-[0.2em] flex items-center gap-2">
                <Globe2 size={10} />
                Local Vault Sync
              </span>
            </div>
            <h1 className="text-6xl font-black tracking-tighter text-white leading-none uppercase">
              System <span className="text-primary italic relative">Workspace<div className="absolute -bottom-1 left-0 w-full h-1 bg-gradient-to-r from-primary to-transparent opacity-30" /></span>
            </h1>
            <p className="text-slate-500 font-bold max-w-2xl text-sm leading-relaxed">
              Real-time operational oversight for ELYX Autonomous FTE. Coordinating <span className="text-slate-200">{data?.tasks.active_chains || "..."}</span> background process threads with <span className="text-accent underline underline-offset-4 decoration-accent/30">99.98%</span> system synchronization integrity.
            </p>
          </div>
          <div className="flex items-center gap-6 relative z-10">
             <div className="hidden lg:flex flex-col items-end px-8 border-r border-white/5">
                <span className="text-[9px] font-black text-slate-500 uppercase tracking-[0.3em] mb-1">Compute Prowess</span>
                <span className="text-emerald-500 font-black text-lg tracking-tight shadow-emerald-500/20 drop-shadow-lg">99.998% Optimal</span>
             </div>
             <motion.button 
               whileHover={{ scale: 1.02, translateY: -2 }}
               whileTap={{ scale: 0.98 }}
               onClick={() => loadDashboard(true)}
               disabled={refreshing}
               className="relative overflow-hidden group btn-premium-primary !px-8 !py-5 shadow-2xl shadow-primary/20 min-w-[240px] border border-white/10"
             >
               <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-transparent to-accent/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
               <div className="relative flex items-center justify-center gap-4">
                 {refreshing ? (
                   <>
                     <RefreshCw size={18} className="animate-spin text-white" />
                     <span className="text-xs font-black uppercase tracking-[0.2em] font-outfit">Synchronizing<LoadingDots /></span>
                   </>
                 ) : (
                   <>
                     <Zap size={18} className="group-hover:text-black group-hover:fill-current transition-all" />
                     <span className="font-outfit text-xs font-black uppercase tracking-[0.2em]">Resync System Core</span>
                   </>
                 )}
               </div>
             </motion.button>
          </div>
        </motion.div>

        {/* Mock Data Warning Banner */}
        {data?.dataSource === "mock" && (
          <motion.div
            variants={itemVariants}
            className="mx-1 flex items-center gap-4 px-6 py-4 rounded-2xl border border-amber-500/30 bg-amber-500/5 backdrop-blur-sm"
          >
            <AlertTriangle size={18} className="text-amber-500 shrink-0" />
            <div className="flex-1">
              <p className="text-xs font-black text-amber-400 uppercase tracking-widest">
                Offline Mode — Displaying Fallback Data
              </p>
              <p className="text-[11px] text-amber-500/70 mt-0.5">
                Main API (port 8000) is unreachable. Values shown are placeholders, not live data.
              </p>
            </div>
            <button
              onClick={() => loadDashboard(true)}
              className="shrink-0 px-4 py-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-[10px] font-black text-amber-400 uppercase tracking-widest hover:bg-amber-500/20 transition-all"
            >
              Retry
            </button>
          </motion.div>
        )}

        {/* Top-Level Grid Overview */}
        <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 px-1">
          <StatCard 
            label="System Accuracy" 
            value={`${data?.system.stability_score.toFixed(1) || "..."}%`}
            icon={<BrainCircuit size={22} />}
            trend={`${(Math.random() * 2 + 1).toFixed(1)}%`}
            subtext="Performance Score"
            color="primary"
          />
          <StatCard 
            label="Live Workflows" 
            value={data?.tasks.active_chains.toString() || "..."}
            icon={<Activity size={22} />}
            trend="Real-time"
            subtext="Active Processes"
            color="accent"
          />
          <StatCard 
            label="System Sync" 
            value={data?.scenarios.stability_index.toFixed(3) || "..."}
            icon={<Globe2 size={22} />}
            trend="Stable"
            subtext="Data Integrity"
            color="emerald"
          />
          <StatCard 
            label="Pending Approvals" 
            value={data?.tasks.pending_count.toString() || "..."}
            icon={<ShieldCheck size={22} />}
            trend={`${data?.tasks.pending_count ? 'Action' : 'Safe'}`}
            subtext="HITL Required"
            color="red"
          />
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">

          {/* Main Content: Activity & Timeline */}
          <div className="lg:col-span-8 space-y-10">

            {/* Operational Pulse visualizer (Central Dashboard Piece) */}
            <motion.div variants={itemVariants} className="glass-panel rounded-[3rem] p-12 relative overflow-hidden group border border-white/5 shadow-2xl">
               <div className="absolute inset-0 bg-gradient-to-br from-primary/[0.02] via-transparent to-accent/[0.02] pointer-events-none" />
               <div className="absolute top-0 right-0 p-8 opacity-20 group-hover:opacity-40 transition-opacity">
                  <Sparkles size={40} className="text-primary animate-pulse" />
               </div>

               <div className="flex items-center justify-between mb-12 relative z-10">
                 <div className="space-y-2">
                    <div className="flex items-center gap-3">
                       <div className="w-12 h-12 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shadow-xl shadow-primary/5">
                          <Activity size={24} className="animate-pulse" />
                       </div>
                       <div>
                          <h2 className="text-3xl font-black text-white tracking-tight">Operational Pulse</h2>
                          <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.3em]">System Monitoring Loop</p>
                       </div>
                    </div>
                 </div>
                 <div className="hidden sm:flex items-center gap-6">
                    <div className="text-right">
                       <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1 text-glow">Attention Drift</p>
                       <p className="text-xs font-black text-slate-300 uppercase tracking-wide">0.002% Variance</p>
                    </div>
                 </div>
               </div>

               {loading ? (
                 <div className="flex flex-col items-center justify-center h-56 gap-6 relative z-10">
                   <div className="w-16 h-16 rounded-full border-t-2 border-primary animate-spin" />
                   <div className="space-y-2 text-center">
                     <p className="text-xs font-black text-slate-400 uppercase tracking-[0.4em]">Mapping Workflows<LoadingDots /></p>
                     <p className="text-[9px] font-bold text-slate-600 uppercase tracking-widest italic">System core handshake in progress</p>
                   </div>
                 </div>
               ) : (
                 <div className="relative h-40 flex items-end gap-2 px-2 mb-10 overflow-hidden rounded-3xl">
                    <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-[2px] pointer-events-none" />
                    {Array.from({ length: 48 }).map((_, i) => (
                      <motion.div 
                        initial={{ height: 0 }}
                        animate={{ height: `${20 + Math.random() * 80}%` }}
                        transition={{ duration: 1.5, delay: i * 0.02, ease: "circOut" }}
                        key={i} 
                        className="flex-1 bg-gradient-to-t from-primary/10 via-primary/40 to-primary rounded-t-full hover:to-accent transition-all duration-500 group/bar relative"
                      >
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-4 p-2 rounded-xl bg-slate-950 border border-white/10 opacity-0 group-hover/bar:opacity-100 transition-all pointer-events-none whitespace-nowrap z-50 shadow-2xl">
                           <p className="text-[9px] font-black text-primary uppercase tracking-widest">Node ID: {i}</p>
                           <p className="text-[11px] font-black text-white mt-1">VOL: {(Math.random() * 100).toFixed(2)}</p>
                        </div>
                      </motion.div>
                    ))}
                 </div>
               )}

               <div className="flex flex-wrap items-center justify-between pt-10 border-t border-white/5 relative z-10 gap-6">
                  <div className="flex items-center gap-6">
                     <div className="flex items-center gap-3 px-6 py-3 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-emerald-500/30 transition-all cursor-crosshair group/item">
                        <TrendingUp size={16} className="text-emerald-500 group-hover/item:scale-125 transition-transform" />
                        <span className="text-[10px] font-black text-slate-400 group-hover/item:text-slate-100 uppercase tracking-widest transition-colors">Outlook: High Stability</span>
                     </div>
                     <div className="flex items-center gap-3 px-6 py-3 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-primary/30 transition-all cursor-wait group/item">
                        <Cpu size={16} className="text-primary group-hover/item:animate-spin transition-all" />
                        <span className="text-[10px] font-black text-slate-400 group-hover/item:text-slate-100 uppercase tracking-widest transition-colors">Core Latency: 42ms</span>
                     </div>
                  </div>
                  <motion.button 
                    whileHover={{ x: 5 }}
                    className="flex items-center gap-3 text-[11px] font-black text-slate-400 uppercase tracking-[0.2em] hover:text-primary transition-all group"
                  >
                    Open System Audit Archive <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
                  </motion.button>
               </div>
            </motion.div>

            {/* Neural Action Logs (Futuristic Activity Feed) */}
            <motion.div variants={itemVariants} className="glass-panel rounded-[3rem] p-12 border border-white/5 shadow-2xl relative overflow-hidden">
               <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary/10 to-transparent" />
               <div className="flex items-center justify-between mb-12 relative z-10">
                  <div className="flex items-center gap-4">
                     <div className="w-14 h-14 rounded-[1.5rem] bg-gradient-to-br from-slate-900 to-black border border-white/10 flex items-center justify-center text-primary shadow-2xl rotate-3 group-hover:rotate-0 transition-transform">
                        <Clock size={24} />
                     </div>
                      <div>
                        <h3 className="text-2xl font-black text-white tracking-tight">Recent Activity Log</h3>
                        <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.3em]">Autonomous Audit Trail</p>
                      </div>
                  </div>
                  <button className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] hover:text-primary transition-all px-6 py-3 bg-white/[0.03] border border-white/5 rounded-2xl hover:border-primary/20">Full History</button>
               </div>

               <div className="space-y-4 relative z-10">
                 {loading ? (
                    <div className="flex flex-col items-center justify-center py-16 opacity-30 gap-4">
                       <Loader2 size={40} className="animate-spin text-primary" />
                       <span className="text-[10px] font-black tracking-[0.4em] text-slate-400 uppercase">Synchronizing Logs<LoadingDots /></span>
                    </div>
                 ) : (
                    <div className="relative pl-6 space-y-2">
                       <div className="absolute left-3 top-0 bottom-0 w-px bg-gradient-to-b from-primary/40 via-white/5 to-transparent" />
                       <LogItem 
                        type="SYSTEM" 
                        title="Drafting response to Client A" 
                        desc="Synthesizing operational context from Company_Handbook.md for high-priority reply." 
                        time="Active" 
                        status="success"
                      />
                       <LogItem 
                        type="SYSTEM" 
                        title="Scanning Action Items" 
                        desc="Synchronizing local business logic states with system cache. 2 new tasks identified." 
                        time="01m ago" 
                        status="info"
                      />
                      <LogItem 
                        type="ODOO" 
                        title="Financial Sync Completed" 
                        desc="Verified 14 pending invoices via JSON-RPC. Cross-referencing with /Invoices/ system storage." 
                        time="12m ago" 
                        status="success"
                      />
                      <LogItem 
                        type="SYSTEM" 
                        title="Permission Gate Triggered" 
                        desc="Invoice over $5,000 detected. Moved to /Pending_Approval for human oversight." 
                        time="42m ago" 
                        status="warning"
                      />
                    </div>
                 )}
               </div>
            </motion.div>
          </div>

          {/* Right Column: Mini-Tools & Quick Access */}
          <div className="lg:col-span-4 space-y-10">
            
            {/* Control Gate (Integrated Approvals) */}
            <motion.div variants={itemVariants} className="glass-panel p-10 rounded-[2.5rem] border border-red-500/20 bg-gradient-to-br from-red-500/[0.03] to-transparent shadow-2xl relative overflow-hidden group">
               <div className="absolute -top-10 -right-10 w-40 h-40 bg-red-500/10 blur-[60px] rounded-full pointer-events-none group-hover:bg-red-500/15 transition-all duration-700" />
               <div className="flex items-center justify-between mb-8 relative z-10">
                  <div className="flex items-center gap-3">
                     <div className="w-11 h-11 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-500 shadow-xl shadow-red-500/5">
                        <Fingerprint size={22} />
                     </div>
                     <h3 className="text-xl font-black text-white leading-tight">Control Gate</h3>
                  </div>
                  <span className="px-3 py-1.5 rounded-xl bg-red-500/20 text-[10px] font-black text-red-500 uppercase tracking-widest border border-red-500/20">
                     {data?.tasks.pending_count || 0}
                  </span>
               </div>
               
               <div className="space-y-4 mb-8 relative z-10">
                  <AnimatePresence mode="popLayout">
                    {approvals.slice(0, 3).map((approval, idx) => (
                      <motion.div 
                        initial={{ x: 20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: idx * 0.1 }}
                        key={approval.id} 
                        className="p-5 rounded-3xl bg-slate-900/60 border border-white/5 group/gate hover:border-red-500/40 hover:bg-black/40 transition-all cursor-pointer shadow-lg"
                      >
                         <div className="flex items-center justify-between mb-3">
                            <span className="text-[10px] font-black text-red-500 uppercase tracking-widest bg-red-500/10 px-2 py-0.5 rounded-lg border border-red-500/10">{approval.type}</span>
                            <span className="text-[9px] font-black text-slate-500 uppercase">{new Date(approval.created).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                         </div>
                         <p className="text-sm font-black text-slate-100 mb-1 group-hover/gate:text-red-400 transition-colors uppercase leading-tight">{approval.action}</p>
                         <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed font-medium">{approval.reason}</p>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  {approvals.length === 0 && (
                    <div className="text-center py-10 border border-dashed border-white/10 rounded-3xl bg-white/[0.01]">
                       <p className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em]">Operational Blocks Absent</p>
                    </div>
                  )}
               </div>
               
               <motion.button 
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full py-5 bg-gradient-to-r from-red-600 to-red-500 border border-red-400/20 rounded-3xl text-[11px] font-black text-white uppercase tracking-[0.2em] shadow-xl shadow-red-600/20 flex items-center justify-center gap-3 group/btn"
               >
                  Authorize Sequence <Command size={16} className="group-hover/btn:rotate-12 transition-transform" />
               </motion.button>
            </motion.div>

            {/* Quick Access Matrix */}
            <motion.div variants={itemVariants} className="glass-panel p-10 rounded-[2.5rem] border border-white/5 shadow-2xl">
               <div className="flex items-center gap-3 mb-8">
                  <LayoutGrid size={20} className="text-primary" />
                  <h3 className="text-xl font-black text-white tracking-tight">Quick Sync</h3>
               </div>
               <div className="grid grid-cols-2 gap-4">
                  <QuickTool icon={<Globe2 size={20} />} label="Decision Matrix" link="/decision-analysis" active color="primary" />
                  <QuickTool icon={<ShieldCheck size={20} />} label="Security Hub" link="/security" color="red" />
                  <QuickTool icon={<Bell size={20} />} label="Notifications" link="/comms" color="accent" />
                  <QuickTool icon={<BrainCircuit size={20} />} label="System Config" link="/settings" color="emerald" />
               </div>
            </motion.div>

            {/* System Resources Load */}
            <motion.div variants={itemVariants} className="glass-panel p-10 rounded-[2.5rem] border border-white/5 shadow-2xl relative overflow-hidden group">
               <div className="absolute top-0 right-0 p-6 opacity-[0.03] group-hover:opacity-[0.07] transition-all rotate-12">
                  <Cpu size={120} />
               </div>
               <div className="flex items-center justify-between mb-10 relative z-10">
                  <h3 className="text-xl font-black text-white tracking-tight">System Load</h3>
                  <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-primary/10 border border-primary/20">
                     <span className="text-xs font-black text-primary uppercase">{(Math.random() * 5 + 85).toFixed(1)}%</span>
                  </div>
               </div>
               
               <div className="space-y-8 relative z-10">
                  <ResourceItem label="Compute Overload" value={92} color="bg-primary" />
                  <ResourceItem label="Memory Density" value={76} color="bg-accent" />
                  <ResourceItem label="Process Buffer" value={98} color="bg-emerald-500" />
               </div>
            </motion.div>

          </div>
        </div>
      </motion.div>
    </DashboardLayout>
  );
}

function StatCard({ label, value, icon, trend, subtext, color }: any) {
  const colorMap: any = {
    primary: "from-primary/20 via-primary/5 to-transparent text-primary border-primary/20",
    accent: "from-accent/20 via-accent/5 to-transparent text-accent border-accent/20",
    emerald: "from-emerald-500/20 via-emerald-500/5 to-transparent text-emerald-500 border-emerald-500/20",
    red: "from-red-500/20 via-red-500/5 to-transparent text-red-500 border-red-500/20",
  };

  const glows: any = {
    primary: "shadow-primary/10 group-hover:shadow-primary/20",
    accent: "shadow-accent/10 group-hover:shadow-accent/20",
    emerald: "shadow-emerald-500/10 group-hover:shadow-emerald-500/20",
    red: "shadow-red-500/10 group-hover:shadow-red-500/20",
  };

  return (
    <div className={`glass-panel p-10 rounded-[2.5rem] group relative overflow-hidden transition-all duration-500 border border-white/5 hover:border-white/10 ${glows[color]}`}>
      <div className={`absolute inset-0 bg-gradient-to-br ${colorMap[color].split('text')[0]} opacity-40 group-hover:opacity-70 transition-opacity`} />
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-8">
          <div className={`w-14 h-14 rounded-2xl bg-white/[0.03] border border-white/10 flex items-center justify-center ${colorMap[color].split(' ')[3]} shadow-2xl`}>
            {icon}
          </div>
          <div className="text-right">
             <div className="flex items-center gap-1.5 justify-end mb-1">
                <TrendingUp size={12} className={colorMap[color].split(' ')[3]} />
                <p className={`text-[11px] font-black uppercase tracking-widest ${colorMap[color].split(' ')[3]}`}>{trend}</p>
             </div>
             <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest opacity-60">{subtext}</p>
          </div>
        </div>
        <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-2">{label}</p>
        <h3 className="text-5xl font-black text-white tracking-tighter leading-none">{value}</h3>
      </div>
    </div>
  );
}

function LogItem({ type, title, desc, time, status }: any) {
  const statuses: any = {
    success: "from-emerald-500/50 to-emerald-400 text-emerald-500",
    info: "from-primary/50 to-primary text-primary",
    warning: "from-red-500/50 to-red-400 text-red-500",
    caution: "from-amber-500/50 to-amber-400 text-amber-500",
  };

  return (
    <div className="flex gap-8 group py-6 px-4 rounded-3xl hover:bg-white/[0.02] transition-all cursor-crosshair">
      <div className="relative flex flex-col items-center">
        <div className={`w-4 h-4 rounded-full border-4 border-slate-950 bg-gradient-to-br ${statuses[status].split('text')[0]} relative z-10 shadow-[0_0_15px_rgba(6,182,212,0.3)]`} />
        <div className="w-px flex-1 bg-white/5 mt-2 group-last:bg-transparent" />
      </div>
      <div className="flex-1 -mt-1.5">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
             <span className={`text-[9px] font-black uppercase tracking-[0.2em] px-2 py-0.5 rounded-lg border border-white/5 bg-white/[0.02] ${statuses[status].split(' ')[2]}`}>{type}</span>
             <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">{time}</span>
          </div>
        </div>
        <h4 className="text-sm font-black text-slate-100 mb-2 uppercase tracking-wide group-hover:text-primary transition-colors leading-tight">{title}</h4>
        <p className="text-[11px] text-slate-500 leading-relaxed font-medium line-clamp-2">{desc}</p>
      </div>
    </div>
  );
}

function QuickTool({ icon, label, link, color }: any) {
  const colors: any = {
    primary: "group-hover:text-primary group-hover:border-primary/40",
    accent: "group-hover:text-accent group-hover:border-accent/40",
    emerald: "group-hover:text-emerald-500 group-hover:border-emerald-500/40",
    red: "group-hover:text-red-500 group-hover:border-red-500/40",
  };

  return (
    <a href={link} className={`flex flex-col items-center justify-center p-8 rounded-[2rem] bg-white/[0.02] border border-white/5 transition-all duration-300 group ${colors[color]}`}>
      <div className={`text-slate-500 transition-all duration-300 mb-4 group-hover:scale-110`}>
        {icon}
      </div>
      <span className="text-[10px] font-black text-slate-500 group-hover:text-slate-100 uppercase tracking-[0.2em] text-center leading-tight">{label}</span>
    </a>
  );
}

function ResourceItem({ label, value, color }: any) {
  return (
    <div className="space-y-3">
      <div className="flex justify-between text-[11px] font-black uppercase tracking-[0.2em]">
        <span className="text-slate-500">{label}</span>
        <span className="text-slate-200">{value}%</span>
      </div>
      <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-white/5">
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 2, ease: "circOut" }}
          className={`h-full ${color} transition-all relative rounded-full`}
        >
           <div className="absolute right-0 top-0 bottom-0 w-8 bg-white/20 blur-sm pointer-events-none" />
        </motion.div>
      </div>
    </div>
  );
}
