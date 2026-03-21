"use client";

import { useEffect, useState, useMemo } from "react";
import {
  Activity,
  TrendingUp,
  Clock,
  BarChart3,
  PieChart,
  ArrowUpRight,
  ArrowDownRight,
  MessageSquare,
  Users,
  Zap,
  Target,
  Download,
  Filter,
  RefreshCw,
  Loader2,
  ChevronRight,
  Mail,
  Smartphone,
  Linkedin,
  Sparkles,
  Brain,
  TrendingDown,
  Gauge,
  AlertTriangle
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { fetchAnalytics } from "@/lib/api";
import LoadingDots from "@/components/LoadingDots";
import { motion, AnimatePresence } from "framer-motion";

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState("week");
  const [refreshing, setRefreshing] = useState(false);

  const loadAnalytics = async () => {
    try {
      setRefreshing(true);
      const res = await fetchAnalytics(timeframe);
      setData(res);
    } catch (error) {
      console.error("Analytics fetch error:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, [timeframe]);

  const communicationChannels = useMemo(() => [
    { label: "Email Protocols", value: data?.metrics.communication_stats.email || 0, icon: <Mail size={18} />, color: "text-blue-500", bg: "bg-blue-500/10", border: "border-blue-500/20" },
    { label: "WhatsApp Secure", value: data?.metrics.communication_stats.whatsapp || 0, icon: <Smartphone size={18} />, color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/20" },
    { label: "LinkedIn Direct", value: data?.metrics.communication_stats.linkedin || 0, icon: <Linkedin size={18} />, color: "text-primary", bg: "bg-primary/10", border: "border-primary/20" },
  ], [data]);

  return (
    <DashboardLayout>
      <div className="space-y-10">
        
        {/* Header Section */}
        <div className="flex flex-col xl:flex-row xl:items-end justify-between gap-8 px-2 relative group">
          <div className="absolute -top-20 -left-20 w-72 h-72 bg-accent/10 blur-[120px] rounded-full pointer-events-none group-hover:bg-accent/15 transition-all duration-1000" />
          <div className="space-y-3 relative z-10">
            <div className="flex items-center gap-3 mb-2">
              <span className="px-3 py-1 bg-accent/10 border border-accent/20 rounded-full text-[10px] font-black text-accent uppercase tracking-[0.2em] flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse shadow-[0_0_8px_rgba(16,185,129,1)]" />
                System Active
              </span>
              <span className="text-[10px] font-black text-slate-600 uppercase tracking-[0.2em]">Timeframe: {timeframe.toUpperCase()}</span>
            </div>
            <h1 className="text-6xl font-black tracking-tighter text-white leading-none uppercase">
              Performance <span className="text-accent italic relative">Analytics<div className="absolute -bottom-1 left-0 w-full h-1 bg-gradient-to-r from-accent to-transparent opacity-30" /></span>
            </h1>
            <p className="text-slate-500 font-bold max-w-2xl text-sm leading-relaxed">
              Advanced performance analytics and engagement metrics synthesized from <span className="text-slate-200">{data?.metrics.tasks_processed.toLocaleString() || "..."}</span> autonomous operations with <span className="text-accent underline underline-offset-4 decoration-accent/30">{data?.metrics.success_rate || "..."}%</span> execution accuracy.
            </p>
          </div>
          <div className="flex items-center gap-6 relative z-10 flex-wrap">
            <div className="flex bg-white/[0.03] border border-white/10 rounded-2xl p-1.5 shadow-2xl backdrop-blur-xl">
              {['today', 'week', 'month', 'year'].map((t) => (
                <motion.button
                  key={t}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setTimeframe(t)}
                  className={`px-6 py-3 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] transition-all ${
                    timeframe === t 
                      ? 'bg-gradient-to-r from-accent to-primary text-black shadow-[0_0_20px_rgba(16,185,129,0.4)]' 
                      : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
                  }`}
                >
                  {t}
                </motion.button>
              ))}
            </div>
            <motion.button 
              whileHover={{ scale: 1.05, rotate: refreshing ? 0 : 180 }}
              whileTap={{ scale: 0.95 }}
              onClick={loadAnalytics}
              disabled={refreshing}
              className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl text-slate-400 hover:text-accent hover:border-accent/30 transition-all flex items-center justify-center min-w-[60px] shadow-xl"
            >
              <RefreshCw size={20} className={refreshing ? 'animate-spin' : ''} />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02, translateY: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => {
                if (!data) return;
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url; a.download = `elyx-analytics-${timeframe}-${new Date().toISOString().slice(0, 10)}.json`;
                a.click(); URL.revokeObjectURL(url);
              }}
              className="btn-premium-primary !px-8 !py-5 shadow-2xl shadow-primary/20 border border-white/10 group"
            >
              <Download size={18} className="group-hover:translate-y-0.5 transition-transform" />
              <span className="font-outfit text-xs font-black uppercase tracking-[0.2em]">Export Analytics</span>
            </motion.button>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center p-40 gap-8">
            <div className="relative">
              <div className="absolute inset-0 bg-accent/20 blur-3xl animate-pulse" />
              <div className="w-20 h-20 rounded-full border-t-4 border-accent animate-spin relative" />
            </div>
            <div className="space-y-2 text-center">
              <p className="text-sm font-black text-slate-400 uppercase tracking-[0.4em]">Synthesizing Data Streams<LoadingDots /></p>
              <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest italic">Performance data compilation in progress</p>
            </div>
          </div>
        ) : (
          <div className="space-y-10">
          {data?._dataSource === "mock" && (
            <div className="flex items-center gap-4 px-6 py-4 rounded-2xl border border-amber-500/30 bg-amber-500/5 backdrop-blur-sm">
              <AlertTriangle size={18} className="text-amber-500 shrink-0" />
              <div className="flex-1">
                <p className="text-xs font-black text-amber-400 uppercase tracking-widest">Offline Mode — Displaying Fallback Data</p>
                <p className="text-[11px] text-amber-500/70 mt-0.5">Analytics API is unreachable. Values shown are placeholders, not live data.</p>
              </div>
              <button onClick={loadAnalytics} className="shrink-0 px-4 py-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-[10px] font-black text-amber-400 uppercase tracking-widest hover:bg-amber-500/20 transition-all">Retry</button>
            </div>
          )}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
            
            {/* Top Row: Hero Metrics */}
            <div className="lg:col-span-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <AnalyticsStatCard 
                label="Tasks Processed" 
                value={data.metrics.tasks_processed.toLocaleString()}
                trend={`${data.trends.percentage_change}%`}
                isUp={data.trends.improving}
                icon={<Zap size={22} />}
                subtext="System Operations"
                color="primary"
              />
              <AnalyticsStatCard 
                label="Response Latency" 
                value={`${data.metrics.average_response_time}s`}
                trend="-2.4s"
                isUp={true}
                icon={<Clock size={22} />}
                subtext="Average Latency"
                color="emerald"
              />
              <AnalyticsStatCard 
                label="Success Rate" 
                value={`${data.metrics.success_rate}%`}
                trend="+0.8%"
                isUp={true}
                icon={<Target size={22} />}
                subtext="Execution Quality"
                color="blue"
              />
              <AnalyticsStatCard 
                label="User Satisfaction" 
                value={`${data.metrics.user_satisfaction}%`}
                trend="+1.2%"
                isUp={true}
                icon={<Users size={22} />}
                subtext="Engagement Index"
                color="emerald"
              />
            </div>

            {/* Middle Row: Charts & Breakdowns */}
            <div className="lg:col-span-8 space-y-10">
              
              {/* Main Performance Chart */}
              <div className="glass-panel rounded-[3rem] p-12 border border-white/5 shadow-2xl relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-br from-accent/[0.02] via-transparent to-primary/[0.02] pointer-events-none" />
                <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
                  <BarChart3 size={80} className="text-accent" />
                </div>
                
                <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-12 gap-6 relative z-10">
                  <div className="space-y-2">
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 rounded-2xl bg-accent/10 border border-accent/20 flex items-center justify-center text-accent shadow-xl shadow-accent/5">
                        <BarChart3 size={24} />
                      </div>
                      <div>
                        <h3 className="text-3xl font-black text-white tracking-tight">Engagement Pulse</h3>
                        <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.3em]">24-Hour Activity Density</p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 px-6 py-3 bg-accent/10 border border-accent/20 rounded-2xl">
                    <Brain size={16} className="text-accent animate-pulse" />
                    <span className="text-[10px] font-black text-accent uppercase tracking-[0.2em]">Deep Learning Active</span>
                  </div>
                </div>

                <div className="relative h-[320px] flex items-end gap-2 px-2 mb-8 rounded-3xl overflow-hidden">
                  <div className="absolute inset-0 bg-slate-900/20 backdrop-blur-[1px] pointer-events-none" />
                  {data.metrics.engagement_by_hour.map((h: any, i: number) => (
                    <motion.div 
                      initial={{ height: 0 }}
                      animate={{ height: `${h.engagement}%` }}
                      transition={{ duration: 1.2, delay: i * 0.03, ease: "circOut" }}
                      key={i} 
                      className="flex-1 group/bar relative"
                    >
                      <div 
                        className="w-full bg-gradient-to-t from-accent/20 via-accent/50 to-accent rounded-t-2xl group-hover/bar:to-primary transition-all duration-500 relative"
                      >
                        <div className="absolute inset-0 bg-gradient-to-t from-transparent to-white/10 opacity-0 group-hover/bar:opacity-100 transition-opacity" />
                      </div>
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-4 p-3 rounded-2xl bg-slate-950 border border-white/10 opacity-0 group-hover/bar:opacity-100 transition-all pointer-events-none z-50 whitespace-nowrap shadow-2xl">
                        <p className="text-[10px] font-black text-accent uppercase tracking-widest">{h.engagement.toFixed(1)}% Engagement</p>
                        <p className="text-[9px] text-slate-500 uppercase tracking-wider mt-1">{h.hour}:00 UTC</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
                
                <div className="flex justify-between px-2 text-[10px] font-black text-slate-600 uppercase tracking-[0.2em] relative z-10">
                  <span>00:00</span>
                  <span>06:00</span>
                  <span>12:00</span>
                  <span>18:00</span>
                  <span>23:59</span>
                </div>
              </div>

              {/* Task Category Distribution */}
              <div className="glass-panel rounded-[3rem] p-12 border border-white/5 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary/20 to-transparent" />
                
                <div className="flex items-center justify-between mb-12 relative z-10">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 rounded-[1.5rem] bg-gradient-to-br from-slate-900 to-black border border-white/10 flex items-center justify-center text-primary shadow-2xl">
                      <PieChart size={24} />
                    </div>
                    <div>
                      <h3 className="text-2xl font-black text-white tracking-tight">Task Distribution</h3>
                      <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.3em]">Operational Breakdown</p>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center relative z-10">
                  <div className="relative flex items-center justify-center">
                    <div className="absolute inset-0 bg-primary/5 blur-3xl rounded-full" />
                    <svg className="w-56 h-56 transform -rotate-90" viewBox="0 0 200 200">
                      <circle cx="100" cy="100" r="80" fill="none" stroke="rgba(15, 23, 42, 0.8)" strokeWidth="20" />
                      <circle cx="100" cy="100" r="80" fill="none" stroke="url(#gradient1)" strokeWidth="20" strokeDasharray="226 502" strokeLinecap="round" className="transition-all duration-1000" />
                      <circle cx="100" cy="100" r="80" fill="none" stroke="url(#gradient2)" strokeWidth="20" strokeDasharray="125 502" strokeDashoffset="-226" strokeLinecap="round" className="transition-all duration-1000" />
                      <circle cx="100" cy="100" r="80" fill="none" stroke="url(#gradient3)" strokeWidth="20" strokeDasharray="90 502" strokeDashoffset="-351" strokeLinecap="round" className="transition-all duration-1000" />
                      <circle cx="100" cy="100" r="80" fill="none" stroke="url(#gradient4)" strokeWidth="20" strokeDasharray="60 502" strokeDashoffset="-441" strokeLinecap="round" className="transition-all duration-1000" />
                      <defs>
                        <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#06b6d4" />
                          <stop offset="100%" stopColor="#0891b2" />
                        </linearGradient>
                        <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#10b981" />
                          <stop offset="100%" stopColor="#059669" />
                        </linearGradient>
                        <linearGradient id="gradient3" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#3b82f6" />
                          <stop offset="100%" stopColor="#2563eb" />
                        </linearGradient>
                        <linearGradient id="gradient4" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#a855f7" />
                          <stop offset="100%" stopColor="#9333ea" />
                        </linearGradient>
                      </defs>
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-4xl font-black text-white tracking-tight">45%</span>
                      <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Communication</span>
                    </div>
                  </div>
                  <div className="space-y-6">
                    <CategoryProgress label="Communication (Email/WA)" value={45} color="bg-primary" />
                    <CategoryProgress label="Operational Sync" value={25} color="bg-emerald-500" />
                    <CategoryProgress label="CRM & Analytics" value={18} color="bg-blue-500" />
                    <CategoryProgress label="Custom Modules" value={12} color="bg-accent" />
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Mini Stats & Reports */}
            <div className="lg:col-span-4 space-y-10">
              
              {/* Communication Breakdown */}
              <div className="glass-panel p-10 rounded-[2.5rem] border border-white/5 shadow-2xl">
                <div className="flex items-center gap-3 mb-10">
                  <div className="w-11 h-11 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shadow-xl shadow-primary/5">
                    <MessageSquare size={20} />
                  </div>
                  <h3 className="text-xl font-black text-white tracking-tight">Channels</h3>
                </div>
                <div className="space-y-5">
                  <AnimatePresence mode="popLayout">
                    {communicationChannels.map((channel, i) => (
                      <motion.div 
                        initial={{ x: 20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: i * 0.1 }}
                        key={i} 
                        className={`p-6 rounded-3xl bg-white/[0.02] border ${channel.border} group hover:bg-white/[0.04] transition-all shadow-lg`}
                      >
                        <div className="flex items-center justify-between mb-4">
                          <div className={`p-3 rounded-2xl ${channel.bg} ${channel.color} shadow-xl`}>
                            {channel.icon}
                          </div>
                          <div className="text-right">
                            <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1">{channel.label}</p>
                            <p className="text-2xl font-black text-slate-100">{channel.value.toLocaleString()}</p>
                          </div>
                        </div>
                        <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-white/5">
                          <motion.div 
                            initial={{ width: 0 }}
                            animate={{ width: `${(channel.value / 1200) * 100}%` }}
                            transition={{ duration: 1.5, ease: "circOut" }}
                            className={`h-full ${channel.color.replace('text', 'bg')} relative`}
                          >
                            <div className="absolute right-0 top-0 bottom-0 w-8 bg-white/20 blur-sm pointer-events-none" />
                          </motion.div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              </div>

              {/* Performance Reports List */}
              <div className="glass-panel p-10 rounded-[2.5rem] border border-white/5 shadow-2xl">
                <div className="flex items-center gap-3 mb-10">
                  <div className="w-11 h-11 rounded-2xl bg-accent/10 border border-accent/20 flex items-center justify-center text-accent shadow-xl shadow-accent/5">
                    <Activity size={20} />
                  </div>
                  <h3 className="text-xl font-black text-white tracking-tight">Reports</h3>
                </div>
                <div className="space-y-4">
                  <ReportItem title="Weekly Performance Audit" date="Feb 06, 2026" score="98.4" />
                  <ReportItem title="Comm Engagement Report" date="Feb 05, 2026" score="96.2" />
                  <ReportItem title="Workflow Logic Review" date="Feb 03, 2026" score="94.8" />
                </div>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    if (!data) return;
                    const lines = [
                      `ELYX Performance Report — ${timeframe.toUpperCase()}`,
                      `Generated: ${new Date().toLocaleString()}`,
                      ``,
                      `Tasks Processed: ${data.metrics.tasks_processed}`,
                      `Success Rate: ${data.metrics.success_rate}%`,
                      `Average Response Time: ${data.metrics.average_response_time}s`,
                      `User Satisfaction: ${data.metrics.user_satisfaction}%`,
                      ``,
                      `Communication Stats:`,
                      `  Email: ${data.metrics.communication_stats.email}`,
                      `  WhatsApp: ${data.metrics.communication_stats.whatsapp}`,
                      `  LinkedIn: ${data.metrics.communication_stats.linkedin}`,
                      ``,
                      `Trend: ${data.trends.improving ? "Improving" : "Declining"} (${data.trends.percentage_change}%)`,
                    ];
                    const blob = new Blob([lines.join("\n")], { type: "text/plain" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url; a.download = `elyx-report-${timeframe}-${new Date().toISOString().slice(0, 10)}.txt`;
                    a.click(); URL.revokeObjectURL(url);
                  }}
                  className="w-full mt-8 py-5 bg-white/[0.03] border border-white/10 rounded-3xl text-[11px] font-black text-slate-400 uppercase tracking-[0.2em] hover:text-white hover:border-primary/30 transition-all flex items-center justify-center gap-3 group shadow-xl"
                >
                  Generate Complete Report
                  <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
                </motion.button>
              </div>

              {/* Efficiency Metric */}
              <div className="glass-panel p-10 rounded-[2.5rem] bg-gradient-to-br from-emerald-500/[0.05] to-transparent border border-emerald-500/20 shadow-2xl relative overflow-hidden group">
                <div className="absolute -top-10 -right-10 w-40 h-40 bg-emerald-500/10 blur-[60px] rounded-full pointer-events-none group-hover:bg-emerald-500/15 transition-all duration-700" />
                <div className="flex items-center justify-between mb-8 relative z-10">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-500 shadow-xl shadow-emerald-500/5">
                      <Gauge size={22} />
                    </div>
                    <h3 className="text-xl font-black text-white tracking-tight">Efficiency Gain</h3>
                  </div>
                  <span className="text-3xl font-black text-emerald-500 tracking-tight">+14.2%</span>
                </div>
                <p className="text-xs text-slate-500 font-medium leading-relaxed relative z-10">
                  System workflow efficiency has improved by <span className="text-emerald-500 font-bold">14.2%</span> compared to the previous cycle through autonomous optimization and systematic workflow corrections.
                </p>
              </div>
            </div>
          </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

function AnalyticsStatCard({ label, value, trend, isUp, icon, color, subtext }: any) {
  const colorMap: any = {
    primary: "from-primary/20 via-primary/5 to-transparent text-primary border-primary/20",
    emerald: "from-emerald-500/20 via-emerald-500/5 to-transparent text-emerald-500 border-emerald-500/20",
    blue: "from-blue-500/20 via-blue-500/5 to-transparent text-blue-500 border-blue-500/20",
    accent: "from-accent/20 via-accent/5 to-transparent text-accent border-accent/20",
  };

  const glows: any = {
    primary: "shadow-primary/10 group-hover:shadow-primary/20",
    emerald: "shadow-emerald-500/10 group-hover:shadow-emerald-500/20",
    blue: "shadow-blue-500/10 group-hover:shadow-blue-500/20",
    accent: "shadow-accent/10 group-hover:shadow-accent/20",
  };

  return (
    <div className={`glass-panel p-10 rounded-[2.5rem] group relative overflow-hidden transition-all duration-500 border border-white/5 hover:border-white/10 ${glows[color]}`}>
      <div className={`absolute inset-0 bg-gradient-to-br ${colorMap[color].split('text')[0]} opacity-40 group-hover:opacity-70 transition-opacity`} />
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-8">
          <div className={`w-14 h-14 rounded-2xl bg-white/[0.03] border border-white/10 flex items-center justify-center ${colorMap[color].split(' ')[3]} shadow-2xl`}>
            {icon}
          </div>
          <div className={`flex items-center gap-2 text-[11px] font-black px-3 py-1.5 rounded-xl ${isUp ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-red-500/10 text-red-500 border border-red-500/20'}`}>
            {isUp ? <ArrowUpRight size={14} /> : <TrendingDown size={14} />}
            {trend}
          </div>
        </div>
        <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-2">{label}</p>
        <h3 className="text-5xl font-black text-white tracking-tighter leading-none mb-2">{value}</h3>
        <p className="text-[9px] font-black text-slate-600 uppercase tracking-widest opacity-60">{subtext}</p>
      </div>
    </div>
  );
}

function CategoryProgress({ label, value, color }: any) {
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
          transition={{ duration: 1.5, ease: "circOut" }}
          className={`h-full ${color} relative rounded-full`}
        >
          <div className="absolute right-0 top-0 bottom-0 w-8 bg-white/20 blur-sm pointer-events-none" />
        </motion.div>
      </div>
    </div>
  );
}

function ReportItem({ title, date, score }: any) {
  return (
    <motion.div 
      whileHover={{ scale: 1.02, x: 4 }}
      className="flex items-center justify-between p-5 rounded-3xl bg-white/[0.02] border border-white/5 group hover:border-accent/20 hover:bg-white/[0.04] transition-all cursor-pointer shadow-lg"
    >
      <div className="flex items-center gap-4">
        <div className="w-11 h-11 rounded-2xl bg-slate-900 border border-white/5 flex items-center justify-center text-slate-500 group-hover:text-accent transition-colors shadow-xl">
          <Download size={18} />
        </div>
        <div>
          <p className="text-sm font-bold text-slate-100 group-hover:text-accent transition-colors leading-tight">{title}</p>
          <p className="text-[9px] text-slate-600 font-black uppercase tracking-widest mt-1">{date}</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">Conf. Score</p>
        <p className="text-sm font-black text-slate-200">{score}</p>
      </div>
    </motion.div>
  );
}
