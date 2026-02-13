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
  Linkedin
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { fetchAnalytics } from "@/lib/api";
import LoadingDots from "@/components/LoadingDots";

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
    { label: "Email Protocols", value: data?.metrics.communication_stats.email || 0, icon: <Mail size={18} />, color: "text-blue-500", bg: "bg-blue-500/10" },
    { label: "WhatsApp Secure", value: data?.metrics.communication_stats.whatsapp || 0, icon: <Smartphone size={18} />, color: "text-emerald-500", bg: "bg-emerald-500/10" },
    { label: "LinkedIn Direct", value: data?.metrics.communication_stats.linkedin || 0, icon: <Linkedin size={18} />, color: "text-primary", bg: "bg-primary/10" },
  ], [data]);

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 px-2">
          <div className="space-y-2">
            <h1 className="text-5xl font-black tracking-tighter text-white">
              Neural <span className="text-primary italic">Intelligence</span>
            </h1>
            <p className="text-slate-500 font-medium max-w-xl">
              Advanced performance analytics and engagement metrics for <span className="text-slate-300 font-bold">ELYX Neural Core</span>.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex bg-slate-900/80 border border-card-border/50 rounded-2xl p-1">
              {['today', 'week', 'month', 'year'].map((t) => (
                <button
                  key={t}
                  onClick={() => setTimeframe(t)}
                  className={`px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${
                    timeframe === t ? 'bg-primary text-slate-950 shadow-[0_0_20px_rgba(6,182,212,0.3)]' : 'text-slate-500 hover:text-slate-300'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
            <button 
              onClick={loadAnalytics}
              disabled={refreshing}
              className="p-4 bg-slate-900 border border-card-border rounded-2xl text-slate-400 hover:text-primary transition-all active:scale-95 flex items-center justify-center min-w-[50px]"
            >
              {refreshing ? <Loader2 size={18} className="animate-spin" /> : <RefreshCw size={18} />}
            </button>
            <button className="btn-premium-primary !px-6 !py-4 shadow-lg group">
              <Download size={18} className="group-hover:translate-y-0.5 transition-transform" />
              Export Intelligence
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center p-40 gap-6">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-3xl animate-pulse" />
              <Activity size={64} className="text-primary animate-pulse relative" />
            </div>
            <p className="text-slate-500 font-black tracking-[0.3em] uppercase flex items-center">Synthesizing Data Streams<LoadingDots /></p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* Top Row: Hero Metrics */}
            <div className="lg:col-span-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <AnalyticsStatCard 
                label="Total Tasks Managed" 
                value={data.metrics.tasks_processed.toLocaleString()}
                trend={`${data.trends.percentage_change}%`}
                isUp={data.trends.improving}
                icon={<Zap className="text-primary" />}
                color="primary"
              />
              <AnalyticsStatCard 
                label="Avg Response Latency" 
                value={`${data.metrics.average_response_time}s`}
                trend="-2.4s"
                isUp={true}
                icon={<Clock className="text-emerald-500" />}
                color="emerald"
              />
              <AnalyticsStatCard 
                label="Success Coefficient" 
                value={`${data.metrics.success_rate}%`}
                trend="+0.8%"
                isUp={true}
                icon={<Target className="text-blue-500" />}
                color="blue"
              />
              <AnalyticsStatCard 
                label="User Engagement" 
                value={`${data.metrics.user_satisfaction}%`}
                trend="+1.2%"
                isUp={true}
                icon={<Users className="text-purple-500" />}
                color="purple"
              />
            </div>

            {/* Middle Row: Charts & Breakdowns */}
            <div className="lg:col-span-8 space-y-8">
              
              {/* Main Performance Chart */}
              <div className="glass-panel rounded-[3rem] p-10 border-primary/20 bg-primary/[0.01]">
                <div className="flex items-center justify-between mb-10">
                  <div>
                    <h3 className="text-2xl font-black text-white flex items-center gap-3">
                      <BarChart3 className="text-primary" size={24} />
                      Neural Engagement Pulse
                    </h3>
                    <p className="text-xs text-slate-500 font-bold mt-1 uppercase tracking-widest">Temporal engagement density over 24h</p>
                  </div>
                  <div className="flex gap-2">
                    <div className="px-4 py-1.5 bg-primary/10 border border-primary/20 rounded-full text-[10px] font-black text-primary uppercase tracking-widest">
                       Deep Learning Active
                    </div>
                  </div>
                </div>

                <div className="relative h-[300px] flex items-end gap-2 px-2">
                   {data.metrics.engagement_by_hour.map((h: any, i: number) => (
                     <div key={i} className="flex-1 group relative">
                        <div 
                          className="w-full bg-primary/20 rounded-t-xl group-hover:bg-primary transition-all duration-500 relative"
                          style={{ height: `${h.engagement}%` }}
                        >
                          <div className="absolute inset-0 bg-gradient-to-t from-transparent to-primary/30 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 p-2 rounded-lg bg-slate-900 border border-card-border opacity-0 group-hover:opacity-100 transition-all pointer-events-none z-20 whitespace-nowrap">
                           <p className="text-[10px] font-black text-primary">{h.engagement.toFixed(1)}% Engagement</p>
                           <p className="text-[8px] text-slate-500 uppercase">{h.hour}:00 PST</p>
                        </div>
                     </div>
                   ))}
                </div>
                <div className="flex justify-between mt-6 px-2 text-[10px] font-black text-slate-600 uppercase tracking-widest">
                   <span>00:00</span>
                   <span>06:00</span>
                   <span>12:00</span>
                   <span>18:00</span>
                   <span>23:59</span>
                </div>
              </div>

              {/* Task Category Distribution */}
              <div className="glass-panel rounded-[3rem] p-10 border-card-border/30">
                 <div className="flex items-center justify-between mb-10">
                    <h3 className="text-xl font-black text-white flex items-center gap-3">
                      <PieChart className="text-primary" size={22} />
                      Category Intelligence Distribution
                    </h3>
                 </div>
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
                    <div className="relative flex items-center justify-center">
                       <div className="w-48 h-48 rounded-full border-[16px] border-slate-900 border-t-primary border-r-emerald-500 border-b-blue-500 animate-spin-slow" />
                       <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className="text-3xl font-black text-white">42%</span>
                          <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Email Dominance</span>
                       </div>
                    </div>
                    <div className="space-y-4">
                       <CategoryProgress label="Communication (Email/WA)" value={45} color="bg-primary" />
                       <CategoryProgress label="Operational Sync" value={25} color="bg-emerald-500" />
                       <CategoryProgress label="CRM & Intelligence" value={18} color="bg-blue-500" />
                       <CategoryProgress label="Custom Paradigms" value={12} color="bg-purple-500" />
                    </div>
                 </div>
              </div>
            </div>

            {/* Right Column: Mini Stats & Reports */}
            <div className="lg:col-span-4 space-y-8">
               
               {/* Communication Breakdown */}
               <div className="glass-panel p-8 rounded-[2.5rem] border-card-border/30">
                  <h3 className="text-lg font-black text-white mb-8 flex items-center gap-3">
                     <MessageSquare size={20} className="text-primary" />
                     Engagement Channels
                  </h3>
                  <div className="space-y-4">
                     {communicationChannels.map((channel, i) => (
                       <div key={i} className="p-5 rounded-3xl bg-slate-900/50 border border-card-border group hover:border-primary/30 transition-all">
                          <div className="flex items-center justify-between mb-3">
                             <div className={`p-3 rounded-2xl ${channel.bg} ${channel.color}`}>
                                {channel.icon}
                             </div>
                             <div className="text-right">
                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{channel.label}</p>
                                <p className="text-lg font-black text-slate-200">{channel.value.toLocaleString()}</p>
                             </div>
                          </div>
                          <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                             <div className={`h-full ${channel.color.replace('text', 'bg')} transition-all duration-1000`} style={{ width: `${(channel.value / 1200) * 100}%` }} />
                          </div>
                       </div>
                     ))}
                  </div>
               </div>

               {/* Performance Reports List */}
               <div className="glass-panel p-8 rounded-[2.5rem] border-card-border/30">
                  <div className="flex items-center justify-between mb-8">
                     <h3 className="text-lg font-black text-white flex items-center gap-3">
                        <Activity size={20} className="text-primary" />
                        Intelligence Reports
                     </h3>
                  </div>
                  <div className="space-y-4">
                     <ReportItem title="Weekly Neural Performance" date="Feb 06, 2026" score="98.4" />
                     <ReportItem title="Comm Engagement Audit" date="Feb 05, 2026" score="96.2" />
                     <ReportItem title="Causal Logic Review" date="Feb 03, 2026" score="94.8" />
                  </div>
                  <button className="w-full mt-6 py-4 bg-slate-900 border border-card-border rounded-2xl text-[10px] font-black text-slate-400 uppercase tracking-widest hover:text-white hover:border-primary/50 transition-all flex items-center justify-center gap-2 group">
                     Compile Full Intelligence Dossier
                     <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                  </button>
               </div>

               {/* Efficiency Metric */}
               <div className="glass-panel p-8 rounded-[2.5rem] bg-emerald-500/[0.02] border-emerald-500/10">
                  <div className="flex items-center justify-between mb-6">
                     <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 flex items-center justify-center text-emerald-500">
                           <TrendingUp size={20} />
                        </div>
                        <h3 className="text-lg font-black text-white">Logic Gain</h3>
                     </div>
                     <span className="text-2xl font-black text-emerald-500">+14.2%</span>
                  </div>
                  <p className="text-xs text-slate-500 font-medium leading-relaxed">
                     Neural logic efficiency has improved by <span className="text-emerald-500 font-bold">14.2%</span> compared to the previous cycle through self-reflection and temporal prophecy correction.
                  </p>
               </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

function AnalyticsStatCard({ label, value, trend, isUp, icon, color }: any) {
  const colorMap: any = {
    primary: "text-primary border-primary/20",
    emerald: "text-emerald-500 border-emerald-500/20",
    blue: "text-blue-500 border-blue-500/20",
    purple: "text-purple-500 border-purple-500/20",
  };

  return (
    <div className="glass-panel p-8 rounded-[2.5rem] group premium-hover transition-all border border-card-border/30 h-full">
      <div className="flex items-center justify-between mb-6">
        <div className={`p-4 rounded-2xl bg-slate-900 border border-card-border group-hover:emerald-blue-glow transition-all`}>
          {icon}
        </div>
        <div className={`flex items-center gap-1 text-[10px] font-black px-2 py-1 rounded-lg ${isUp ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
          {isUp ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
          {trend}
        </div>
      </div>
      <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1">{label}</p>
      <h3 className="text-3xl font-black text-slate-100 tracking-tighter">{value}</h3>
    </div>
  );
}

function CategoryProgress({ label, value, color }: any) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-[10px] font-black text-slate-500 uppercase tracking-widest">
         <span>{label}</span>
         <span className="text-slate-200">{value}%</span>
      </div>
      <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
         <div className={`h-full ${color} transition-all duration-1000`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

function ReportItem({ title, date, score }: any) {
  return (
    <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-900/40 border border-card-border/50 group hover:border-primary/20 transition-all cursor-pointer">
       <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-slate-800 border border-card-border flex items-center justify-center text-slate-500 group-hover:text-primary transition-colors">
             <Download size={18} />
          </div>
          <div>
             <p className="text-xs font-bold text-slate-100 group-hover:text-primary transition-colors">{title}</p>
             <p className="text-[9px] text-slate-600 font-bold uppercase tracking-widest">{date}</p>
          </div>
       </div>
       <div className="text-right">
          <p className="text-[10px] font-black text-emerald-500 uppercase">Q-Score</p>
          <p className="text-xs font-black text-slate-300">{score}</p>
       </div>
    </div>
  );
}
