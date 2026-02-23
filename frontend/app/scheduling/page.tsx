"use client";

import { useEffect, useState } from "react";
import {
  Calendar,
  Clock,
  CheckCircle2,
  Loader2,
  Plus,
  MoreHorizontal,
  CalendarDays,
  Timer,
  Bell,
  CalendarClock
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import LoadingDots from "@/components/LoadingDots";

interface ScheduledTask {
  id: string;
  title: string;
  description: string;
  scheduled_time: string;
  status: 'scheduled' | 'running' | 'completed' | 'failed';
  type: 'watcher' | 'briefing' | 'sync' | 'custom';
  recurrence?: 'daily' | 'weekly' | 'monthly';
}

export default function SchedulingPage() {
  const [tasks, setTasks] = useState<ScheduledTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'scheduled' | 'running' | 'completed'>('all');

  const loadData = async () => {
    try {
      setLoading(true);
      // Simulated data - replace with actual API call
      const simulatedTasks: ScheduledTask[] = [
        {
          id: "SCH-001",
          title: "Gmail Watcher Check",
          description: "Monitor Gmail for unread important emails",
          scheduled_time: new Date(Date.now() + 300000).toISOString(), // 5 min from now
          status: 'scheduled',
          type: 'watcher',
          recurrence: 'continuous'
        },
        {
          id: "SCH-002",
          title: "Weekly CEO Briefing",
          description: "Generate weekly business audit and revenue report",
          scheduled_time: new Date(Date.now() + 86400000).toISOString(), // Tomorrow
          status: 'scheduled',
          type: 'briefing',
          recurrence: 'weekly'
        },
        {
          id: "SCH-003",
          title: "Odoo Sync",
          description: "Synchronize invoices and payments with Odoo Cloud",
          scheduled_time: new Date(Date.now() - 1800000).toISOString(), // 30 min ago
          status: 'completed',
          type: 'sync',
          recurrence: 'hourly'
        },
        {
          id: "SCH-004",
          title: "WhatsApp Status Check",
          description: "Monitor WhatsApp for keyword mentions",
          scheduled_time: new Date(Date.now() + 60000).toISOString(), // 1 min from now
          status: 'scheduled',
          type: 'watcher',
          recurrence: 'continuous'
        },
        {
          id: "SCH-005",
          title: "Database Backup",
          description: "Create incremental backup of SQLite database",
          scheduled_time: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
          status: 'completed',
          type: 'custom',
          recurrence: 'daily'
        },
      ];
      setTasks(simulatedTasks);
    } catch (error) {
      console.error("Scheduling fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredTasks = tasks.filter(t => {
    if (filter === 'all') return true;
    return t.status === filter;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 size={16} className="text-emerald-500" />;
      case 'running': return <Loader2 size={16} className="text-primary animate-spin" />;
      case 'scheduled': return <Clock size={16} className="text-slate-500" />;
      case 'failed': return <AlertTriangle size={16} className="text-red-500" />;
      default: return <Clock size={16} />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'watcher': return 'text-blue-500 bg-blue-500/10';
      case 'briefing': return 'text-purple-500 bg-purple-500/10';
      case 'sync': return 'text-emerald-500 bg-emerald-500/10';
      case 'custom': return 'text-amber-500 bg-amber-500/10';
      default: return 'text-slate-500';
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = date.getTime() - now.getTime();
    
    if (diff < 0) {
      const minutes = Math.abs(Math.floor(diff / 60000));
      if (minutes < 60) return `${minutes}m ago`;
      const hours = Math.floor(minutes / 60);
      return `${hours}h ago`;
    } else {
      const minutes = Math.floor(diff / 60000);
      if (minutes < 60) return `in ${minutes}m`;
      const hours = Math.floor(minutes / 60);
      return `in ${hours}h`;
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-in fade-in duration-700">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-4xl font-black tracking-tight mb-2">Task Scheduler</h1>
            <p className="text-slate-400 font-medium">Manage scheduled tasks, recurring jobs, and automated workflows.</p>
          </div>
          <button className="btn-premium-primary flex items-center gap-2">
            <Plus size={18} />
            Schedule Task
          </button>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center p-40 gap-4">
            <Loader2 size={48} className="text-primary animate-spin" />
            <p className="text-slate-500 font-bold flex items-center">Loading schedule<LoadingDots /></p>
          </div>
        ) : (
          <>
            {/* Filter Tabs */}
            <div className="flex gap-3">
               <div className="glass-panel flex p-1 rounded-xl">
                 {(['all', 'scheduled', 'running', 'completed'] as const).map((f) => (
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

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

              {/* Task Timeline */}
              <div className="lg:col-span-2 space-y-6">
                 <div className="glass-panel rounded-3xl p-8">
                    <h3 className="text-lg font-bold mb-8 flex items-center gap-2">
                      <CalendarDays size={20} className="text-primary" />
                      Upcoming & Recent Tasks
                    </h3>

                    <div className="space-y-0 relative">
                       {/* Timeline line */}
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
                                  <div className="flex items-center gap-2">
                                    <span className={`px-2 py-0.5 rounded text-[9px] font-black uppercase ${getTypeColor(task.type)}`}>
                                      {task.type}
                                    </span>
                                    {task.recurrence && (
                                      <span className="text-[9px] font-bold text-slate-500 uppercase flex items-center gap-1">
                                        <Clock size={10} />
                                        {task.recurrence}
                                      </span>
                                    )}
                                  </div>
                                  <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                    {formatTime(task.scheduled_time)}
                                    <CalendarClock size={14} />
                                  </span>
                               </div>
                               <h4 className="text-lg font-bold text-slate-200 mb-2">{task.title}</h4>
                               <p className="text-xs text-slate-500 font-medium mb-4">{task.description}</p>

                               <div className="flex items-center justify-between mt-4 pt-4 border-t border-card-border/50">
                                  <div className="flex items-center gap-4">
                                     <div className="flex items-center gap-2">
                                       <span className="text-[9px] font-black text-slate-600 uppercase">ID:</span>
                                       <span className="text-xs font-bold text-slate-300 font-mono">{task.id}</span>
                                     </div>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <button className="p-2 hover:text-primary transition-colors">
                                      <MoreHorizontal size={18} />
                                    </button>
                                    {task.status === 'scheduled' && (
                                      <button className="p-2 hover:text-emerald-500 transition-colors">
                                        <Timer size={18} />
                                      </button>
                                    )}
                                  </div>
                               </div>
                            </div>
                         </div>
                       ))}
                    </div>
                 </div>
              </div>

              {/* Side Modules */}
              <div className="space-y-8">
                 {/* Quick Stats */}
                 <div className="glass-panel p-8 rounded-3xl">
                    <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-6">Schedule Overview</h3>

                    <div className="space-y-6">
                       <div className="text-center py-6">
                          <h2 className="text-5xl font-black text-slate-100 tabular-nums">{tasks.filter(t => t.status === 'scheduled').length}</h2>
                          <p className="text-[10px] font-bold text-slate-500 uppercase mt-2">Scheduled Tasks</p>
                       </div>
                       <div className="grid grid-cols-2 gap-4">
                          <div className="p-4 rounded-2xl bg-slate-900/30 border border-card-border text-center">
                             <p className="text-2xl font-black text-emerald-500">{tasks.filter(t => t.status === 'completed').length}</p>
                             <p className="text-[9px] font-bold text-slate-500 uppercase mt-1">Completed</p>
                          </div>
                          <div className="p-4 rounded-2xl bg-slate-900/30 border border-card-border text-center">
                             <p className="text-2xl font-black text-primary">{tasks.filter(t => t.status === 'running').length}</p>
                             <p className="text-[9px] font-bold text-slate-500 uppercase mt-1">Running</p>
                          </div>
                       </div>
                    </div>
                 </div>

                 {/* Quick Actions */}
                 <div className="glass-panel p-8 rounded-3xl">
                    <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-6">Quick Actions</h3>
                    <div className="space-y-3">
                       <button className="w-full py-3 bg-slate-800 rounded-xl text-xs font-bold text-slate-300 hover:bg-slate-700 hover:text-white transition-all border border-card-border text-left px-4 flex items-center gap-3">
                          <Plus size={16} />
                          Create New Schedule
                       </button>
                       <button className="w-full py-3 bg-slate-800 rounded-xl text-xs font-bold text-slate-300 hover:bg-slate-700 hover:text-white transition-all border border-card-border text-left px-4 flex items-center gap-3">
                          <Bell size={16} />
                          Configure Notifications
                       </button>
                       <button className="w-full py-3 bg-slate-800 rounded-xl text-xs font-bold text-slate-300 hover:bg-slate-700 hover:text-white transition-all border border-card-border text-left px-4 flex items-center gap-3">
                          <Calendar size={16} />
                          View Calendar
                       </button>
                    </div>
                 </div>

                 {/* Next Major Task */}
                 <div className="glass-panel p-8 rounded-3xl border-primary/20 bg-primary/[0.02]">
                    <div className="flex items-center gap-3 mb-6">
                       <div className="p-2 rounded-lg bg-primary/10 text-primary">
                          <CalendarClock size={18} />
                       </div>
                       <h3 className="text-lg font-bold">Next Major Task</h3>
                    </div>
                    <div className="space-y-4">
                       <div>
                          <p className="text-sm font-bold text-slate-200 mb-1">Weekly CEO Briefing</p>
                          <p className="text-xs text-slate-500 font-medium">Tomorrow at 8:00 AM</p>
                       </div>
                       <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-primary h-full w-[75%]" />
                       </div>
                       <p className="text-[10px] font-bold text-slate-500 uppercase">Starts in 18 hours</p>
                    </div>
                 </div>
              </div>

            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
