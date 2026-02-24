"use client";

import { useEffect, useState } from "react";
import { 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  ChevronRight, 
  Mail, 
  MessageCircle, 
  FileText, 
  DollarSign,
  Filter,
  Search,
  ArrowUpRight,
  MoreVertical,
  Loader2,
  Trash2,
  CheckCircle,
  ShieldCheck
} from "lucide-react";
import { fetchTasks, fetchApprovals } from "@/lib/api";
import { Task, ApprovalRequest } from "@/lib/types";
import DashboardLayout from "@/components/DashboardLayout";
import LoadingDots from "@/components/LoadingDots";

export default function OperationsPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'pending' | 'approvals'>('pending');

  const loadData = async () => {
    try {
      setLoading(true);
      const [fetchedTasks, fetchedApprovals] = await Promise.all([
        fetchTasks(),
        fetchApprovals()
      ]);
      setTasks(fetchedTasks);
      setApprovals(fetchedApprovals);
    } catch (error) {
      console.error("Operations load error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-500 bg-red-500/10 border-red-500/20';
      case 'high': return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
      case 'medium': return 'text-primary bg-primary/10 border-primary/20';
      default: return 'text-slate-400 bg-slate-800 border-slate-700';
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'email': return <Mail size={18} />;
      case 'whatsapp': return <MessageCircle size={18} />;
      case 'file_drop': return <FileText size={18} />;
      case 'finance': return <DollarSign size={18} />;
      default: return <CheckCircle2 size={18} />;
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-in fade-in duration-500">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-4xl font-black tracking-tight mb-2">Operations Center</h1>
            <p className="text-slate-400 font-medium">Manage the ELYX workload and active task queues.</p>
          </div>
          <div className="flex gap-3">
            <div className="glass-panel flex p-1 rounded-xl">
              <button 
                onClick={() => setActiveTab('pending')}
                className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                  activeTab === 'pending' ? 'bg-primary text-slate-950' : 'text-slate-400 hove:text-slate-200'
                }`}
              >
                Action Queue
              </button>
              <button 
                onClick={() => setActiveTab('approvals')}
                className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                  activeTab === 'approvals' ? 'bg-primary text-slate-950' : 'text-slate-400 hove:text-slate-200'
                }`}
              >
                Approvals Needed
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            <div className="glass-panel p-6 rounded-2xl">
              <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Search & Filters</h3>
              <div className="space-y-4">
                <div className="relative">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input 
                    type="text" 
                    placeholder="Find task..." 
                    className="w-full bg-slate-900/50 border border-card-border rounded-xl py-2 pl-10 pr-4 text-sm focus:border-primary/50 outline-none transition-all"
                  />
                </div>
                <div className="pt-2">
                  <p className="text-xs font-bold text-slate-600 mb-2 uppercase tracking-tighter">Priority</p>
                  <div className="flex flex-wrap gap-2">
                    {['Critical', 'High', 'Medium', 'Low'].map((p) => (
                      <button key={p} className="px-3 py-1 rounded-lg border border-card-border bg-slate-900/30 text-[10px] font-bold text-slate-400 hover:border-primary/30 transition-all">
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="glass-panel p-6 rounded-2xl bg-primary/5 border-primary/10">
              <div className="flex items-center gap-2 mb-3 text-primary">
                <AlertCircle size={18} />
                <h3 className="font-bold">Queue Health</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                The system processor is handling 14 workflows with 99.8% precision.
              </p>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div className="bg-primary h-full w-[85%]" />
              </div>
            </div>
          </div>

          {/* Task List */}
          <div className="lg:col-span-3">
            {loading ? (
              <div className="glass-panel rounded-3xl p-20 flex flex-col items-center justify-center gap-4">
                <Loader2 size={40} className="text-primary animate-spin" />
                <p className="text-slate-500 font-bold flex items-center">Synchronizing metadata<LoadingDots /></p>
              </div>
            ) : (
              <div className="space-y-4">
                {activeTab === 'pending' ? (
                  tasks.length > 0 ? tasks.map((task) => (
                    <div key={task.id} className="glass-panel rounded-2xl p-6 premium-hover group relative">
                      <div className="flex items-start gap-4">
                        <div className={`p-3 rounded-xl border ${getPriorityColor(task.priority)}`}>
                          {getIcon(task.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-1">
                            <h3 className="text-lg font-bold text-slate-200 truncate">{task.subject || task.from}</h3>
                            <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase border ${getPriorityColor(task.priority)}`}>
                              {task.priority}
                            </span>
                          </div>
                          <p className="text-sm text-slate-400 mb-4 line-clamp-2">{task.content}</p>
                          
                          <div className="flex flex-wrap gap-2">
                            {task.suggested_actions?.map((action, i) => (
                              <button key={i} className="px-4 py-1.5 rounded-lg bg-slate-800 border border-card-border text-[11px] font-bold text-slate-300 hover:bg-primary hover:text-slate-950 hover:border-primary transition-all flex items-center gap-2">
                                {action}
                                <ArrowUpRight size={12} />
                              </button>
                            ))}
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">
                            {new Date(task.created).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                          <button className="text-slate-600 hover:text-slate-200 transition-colors">
                            <MoreVertical size={20} />
                          </button>
                        </div>
                      </div>
                    </div>
                  )) : (
                    <div className="glass-panel rounded-3xl p-20 text-center">
                      <CheckCircle2 size={48} className="text-accent mx-auto mb-4 opacity-20" />
                      <h3 className="text-xl font-bold text-slate-500">Inbox Zero</h3>
                      <p className="text-slate-600">ELYX has cleared all immediate action items.</p>
                    </div>
                  )
                ) : (
                  approvals.map((app) => (
                    <div key={app.id} className="glass-panel rounded-2xl p-6 border-accent/20">
                      <div className="flex flex-col md:flex-row gap-6">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 rounded-lg bg-accent/10 text-accent border border-accent/20">
                              <ShieldCheck size={20} />
                            </div>
                            <div>
                              <h3 className="font-bold text-slate-200 capitalize">{app.action.replace('_', ' ')}</h3>
                              <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest">Approval Requested</p>
                            </div>
                          </div>
                          
                          <div className="bg-slate-950/50 rounded-xl p-4 border border-card-border mb-4">
                            <pre className="text-xs text-slate-400 whitespace-pre-wrap font-mono">
                              {app.details}
                            </pre>
                          </div>
                          
                          <p className="text-sm text-slate-300 italic">" {app.reason} "</p>
                        </div>
                        
                        <div className="flex md:flex-col gap-3 justify-end md:w-48">
                          <button className="btn-premium-primary !text-[#020617] !font-black">
                            <CheckCircle size={18} />
                            Approve
                          </button>
                          <button className="btn-premium-danger">
                            <Trash2 size={18} />
                            Reject
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
