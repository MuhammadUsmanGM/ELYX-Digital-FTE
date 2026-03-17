"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  Zap,
  Cpu,
  RefreshCcw,
  AlertTriangle,
  Loader2,
  Server,
  HardDrive,
  Network,
  CheckCircle2,
  TrendingUp,
  Clock
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import LoadingDots from "@/components/LoadingDots";
import { fetchActivityLog } from "@/lib/api";

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  active_watchers: number;
  tasks_processed: number;
  uptime_hours: number;
  last_sync: string;
  health_status: 'healthy' | 'degraded' | 'critical';
}

export default function SystemMonitorPage() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [activity, setActivity] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      // Simulated metrics - replace with actual API call
      const simulatedMetrics: SystemMetrics = {
        cpu_usage: 23.5,
        memory_usage: 42.8,
        disk_usage: 15.2,
        active_watchers: 5,
        tasks_processed: 1247,
        uptime_hours: 72.3,
        last_sync: new Date().toISOString(),
        health_status: 'healthy'
      };
      setMetrics(simulatedMetrics);

      const recent = await fetchActivityLog(10);
      setActivity(recent);
    } catch (error) {
      console.error("System metrics fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMetrics();
    const interval = setInterval(() => {
      // Simulate minor fluctuations
      setMetrics(prev => prev ? {
        ...prev,
        cpu_usage: Math.min(100, Math.max(0, prev.cpu_usage + (Math.random() - 0.5) * 5)),
        memory_usage: Math.min(100, Math.max(0, prev.memory_usage + (Math.random() - 0.5) * 3))
      } : null);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => {
      setRefreshing(false);
      loadMetrics();
    }, 1500);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
      case 'degraded': return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
      case 'critical': return 'text-red-500 bg-red-500/10 border-red-500/20';
      default: return 'text-slate-500';
    }
  };

  const getMetricColor = (value: number, threshold: number = 80) => {
    if (value > threshold) return 'text-red-500';
    if (value > threshold * 0.7) return 'text-amber-500';
    return 'text-emerald-500';
  };

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-in fade-in duration-700">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-4xl font-black tracking-tight mb-2">System Monitor</h1>
            <p className="text-slate-400 font-medium">Real-time health monitoring for ELYX core services and watchers.</p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="btn-premium-primary"
          >
            {refreshing ? <Loader2 size={18} className="animate-spin" /> : <RefreshCcw size={18} />}
            {refreshing ? 'Refreshing...' : 'Refresh Metrics'}
          </button>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center p-40 gap-4">
            <Loader2 size={48} className="text-primary animate-spin" />
            <p className="text-slate-500 font-bold flex items-center">Loading system metrics<LoadingDots /></p>
          </div>
        ) : (
          <>
            {/* System Health Status */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                   <Activity size={120} />
                </div>
                <p className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em] mb-4">System Health</p>
                <div className="flex items-center gap-3 mb-4">
                   <div className={`px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest border ${getStatusColor(metrics?.health_status || 'healthy')}`}>
                     {metrics?.health_status || 'Unknown'}
                   </div>
                   <CheckCircle2 size={20} className="text-emerald-500" />
                </div>
                <p className="text-sm text-slate-400 font-medium">All systems operational</p>
              </div>

              <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group">
                 <p className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em] mb-4">CPU Usage</p>
                 <div className="flex items-end gap-3 mb-6">
                    <h2 className={`text-5xl font-black ${getMetricColor(metrics?.cpu_usage || 0)}`}>{metrics?.cpu_usage.toFixed(1)}%</h2>
                 </div>
                 <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden border border-card-border">
                    <div className={`h-full transition-all duration-1000 ${getMetricColor(metrics?.cpu_usage || 0, 80).replace('text-', 'bg-')}`} style={{ width: `${metrics?.cpu_usage}%` }} />
                 </div>
              </div>

              <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group">
                 <p className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em] mb-4">Memory Usage</p>
                 <div className="flex items-end gap-3 mb-6">
                    <h2 className={`text-5xl font-black ${getMetricColor(metrics?.memory_usage || 0)}`}>{metrics?.memory_usage.toFixed(1)}%</h2>
                 </div>
                 <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden border border-card-border">
                    <div className={`h-full transition-all duration-1000 ${getMetricColor(metrics?.memory_usage || 0, 80).replace('text-', 'bg-')}`} style={{ width: `${metrics?.memory_usage}%` }} />
                 </div>
              </div>

              <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group">
                 <p className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em] mb-4">Disk Usage</p>
                 <div className="flex items-end gap-3 mb-6">
                    <h2 className={`text-5xl font-black ${getMetricColor(metrics?.disk_usage || 0)}`}>{metrics?.disk_usage.toFixed(1)}%</h2>
                 </div>
                 <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden border border-card-border">
                    <div className={`h-full transition-all duration-1000 ${getMetricColor(metrics?.disk_usage || 0, 80).replace('text-', 'bg-')}`} style={{ width: `${metrics?.disk_usage}%` }} />
                 </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
               {/* Active Services */}
               <div className="lg:col-span-2 glass-panel rounded-3xl p-8">
                  <div className="flex items-center justify-between mb-8">
                    <h3 className="text-xl font-bold flex items-center gap-2">
                       <Server size={20} className="text-primary" />
                       Active Services
                    </h3>
                  </div>

                  <div className="space-y-4">
                    {[
                      { name: 'Gmail Watcher', status: 'active', interval: '120s' },
                      { name: 'WhatsApp Watcher', status: 'active', interval: '60s' },
                      { name: 'Filesystem Watcher', status: 'active', interval: '10s' },
                      { name: 'Odoo Integration', status: 'active', interval: '3600s' },
                      { name: 'API Server', status: 'active', port: '8000' },
                      { name: 'Database', status: 'active', type: 'SQLite' },
                    ].map((service, i) => (
                      <div key={i} className="flex items-center justify-between p-4 rounded-2xl bg-slate-900/50 border border-card-border hover:border-primary/30 transition-all">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                          <span className="text-sm font-bold text-slate-200">{service.name}</span>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">
                            {service.interval || service.port || service.type}
                          </span>
                          <span className="text-[10px] font-black text-emerald-500 uppercase px-2 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                            Running
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
               </div>

               {/* System Stats */}
               <div className="space-y-8">
                  <div className="glass-panel p-8 rounded-3xl">
                     <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                        <Cpu size={18} className="text-accent" />
                        Performance Stats
                     </h3>
                     <div className="space-y-6">
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-slate-400 uppercase tracking-tighter">Tasks Processed</span>
                          <span className="text-sm font-black text-slate-200">{metrics?.tasks_processed.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-slate-400 uppercase tracking-tighter">Active Watchers</span>
                          <span className="text-sm font-black text-slate-200">{metrics?.active_watchers}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-slate-400 uppercase tracking-tighter">Uptime</span>
                          <span className="text-sm font-black text-slate-200">{metrics?.uptime_hours.toFixed(1)}h</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-slate-400 uppercase tracking-tighter">Last Sync</span>
                          <span className="text-sm font-black text-slate-200">{new Date(metrics?.last_sync || '').toLocaleTimeString()}</span>
                        </div>
                     </div>
                  </div>

                  <div className="glass-panel p-8 rounded-3xl">
                     <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                        <Zap size={18} className="text-primary" />
                        Quick Actions
                     </h3>
                     <div className="space-y-3">
                        <button className="w-full py-3 bg-slate-800 rounded-xl text-xs font-bold text-slate-300 hover:bg-slate-700 hover:text-white transition-all border border-card-border text-left px-4 flex items-center gap-3">
                          <RefreshCcw size={16} />
                          Restart All Watchers
                        </button>
                        <button className="w-full py-3 bg-slate-800 rounded-xl text-xs font-bold text-slate-300 hover:bg-slate-700 hover:text-white transition-all border border-card-border text-left px-4 flex items-center gap-3">
                          <HardDrive size={16} />
                          Clear System Logs
                        </button>
                        <button className="w-full py-3 bg-slate-800 rounded-xl text-xs font-bold text-slate-300 hover:bg-slate-700 hover:text-white transition-all border border-card-border text-left px-4 flex items-center gap-3">
                          <Network size={16} />
                          Check Network Status
                        </button>
                     </div>
                  </div>
               </div>
            </div>

            {/* Recent Activity Log */}
            <div className="glass-panel rounded-3xl p-8">
               <h3 className="text-xl font-bold mb-8 flex items-center gap-2">
                 <Clock size={20} className="text-slate-400" />
                 Recent Activity Log
               </h3>
               <div className="space-y-6">
                  {activity.length === 0 ? (
                    <div className="text-xs text-slate-500 font-bold uppercase tracking-widest opacity-70">
                      No recent activity
                    </div>
                  ) : activity.map((log: any, i: number) => {
                    const ts = new Date(log.timestamp || "");
                    const time = Number.isNaN(ts.getTime())
                      ? "—"
                      : ts.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
                    const t = String(log.action_type || "").toUpperCase();
                    const isOk = !(t.includes("ERROR") || t.includes("FAILED"));
                    return (
                      <div key={i} className="flex items-center gap-4 p-4 rounded-2xl bg-slate-900/30 border border-card-border hover:bg-slate-900/50 transition-all">
                         <span className="text-[10px] font-black text-slate-600 uppercase font-mono">{time}</span>
                         <div className={`w-2 h-2 rounded-full ${isOk ? 'bg-emerald-500' : 'bg-red-500'}`} />
                         <p className="text-sm text-slate-400 font-medium">{log.message || "—"}</p>
                      </div>
                    );
                  })}
               </div>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
