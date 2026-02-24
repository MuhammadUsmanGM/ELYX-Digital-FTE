"use client";

import { useEffect, useState } from "react";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  BarChart3, 
  ArrowUpRight, 
  ArrowDownRight,
  Target,
  Zap,
  Clock,
  Briefcase,
  Loader2,
  ChevronRight,
  MoreVertical
} from "lucide-react";
import { fetchTransactions, fetchKPIs, fetchWorkflows } from "@/lib/api";
import { Transaction, KPI, BusinessWorkflow } from "@/lib/types";
import DashboardLayout from "@/components/DashboardLayout";

export default function BusinessPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [workflows, setWorkflows] = useState<BusinessWorkflow[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tData, kData, wData] = await Promise.all([
        fetchTransactions(),
        fetchKPIs(),
        fetchWorkflows()
      ]);
      setTransactions(tData);
      setKpis(kData);
      setWorkflows(wData);
    } catch (error) {
      console.error("Business data load error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-in fade-in duration-500">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-4xl font-black tracking-tight mb-2">Business Operations</h1>
            <p className="text-slate-400 font-medium">Monitoring enterprise performance and financial vectors.</p>
          </div>
          <div className="flex gap-3">
            <button className="btn-premium-secondary">
              <BarChart3 size={16} />
              Export Report
            </button>
          </div>
        </div>

        {/* KPI Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {loading ? (
            Array(4).fill(0).map((_, i) => (
              <div key={i} className="glass-panel h-32 rounded-2xl animate-pulse bg-slate-900/50" />
            ))
          ) : kpis.map((kpi, i) => (
            <div key={i} className="glass-panel p-6 rounded-2xl group premium-hover">
              <div className="flex items-center justify-between mb-4">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">{kpi.label}</p>
                <div className={`p-1.5 rounded-lg ${
                  kpi.trend === 'up' ? 'text-emerald-500 bg-emerald-500/10' : 
                  kpi.trend === 'down' ? 'text-red-500 bg-red-500/10' : 
                  'text-slate-500 bg-slate-500/10'
                }`}>
                  {kpi.trend === 'up' ? <TrendingUp size={16} /> : 
                   kpi.trend === 'down' ? <TrendingDown size={16} /> : 
                   <Zap size={16} />}
                </div>
              </div>
              <div className="flex items-end justify-between">
                <h3 className="text-2xl font-black text-slate-200">{kpi.value}</h3>
                <div className="flex items-center gap-1">
                   {kpi.change !== 0 && (
                     <>
                      {kpi.change > 0 ? <ArrowUpRight size={12} className="text-emerald-500" /> : <ArrowDownRight size={12} className="text-red-500" />}
                      <span className={`text-[10px] font-black ${kpi.change > 0 ? 'text-emerald-500' : 'text-red-500'}`}>
                        {Math.abs(kpi.change)}%
                      </span>
                     </>
                   )}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Transaction History */}
          <div className="glass-panel rounded-3xl p-8">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <DollarSign size={20} className="text-primary" />
                Financial Transactions
              </h2>
              <button className="text-xs font-bold text-primary hover:underline">View All</button>
            </div>
            
            {loading ? (
              <div className="flex justify-center p-20"><Loader2 className="animate-spin text-primary" /></div>
            ) : (
              <div className="space-y-4">
                {transactions.map((t) => (
                  <div key={t.id} className="flex items-center gap-4 p-4 rounded-2xl bg-slate-900/30 border border-card-border/50 hover:bg-slate-900/50 transition-all group">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      t.type === 'income' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'
                    }`}>
                      {t.type === 'income' ? <ArrowUpRight size={18} /> : <ArrowDownRight size={18} />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-bold text-slate-200 truncate">{t.merchant}</p>
                      <p className="text-[10px] text-slate-500 font-medium uppercase">{t.category}</p>
                    </div>
                    <div className="text-right">
                      <p className={`text-sm font-black ${t.type === 'income' ? 'text-emerald-500' : 'text-slate-200'}`}>
                        {t.type === 'income' ? '+' : '-'}${t.amount.toLocaleString()}
                      </p>
                      <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
                        {t.status}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Workflow Efficiency */}
          <div className="glass-panel rounded-3xl p-8">
             <div className="flex items-center justify-between mb-8">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Zap size={20} className="text-accent" />
                Active Workflows
              </h2>
              <button className="text-xs font-bold text-accent hover:underline">Configure</button>
            </div>

            {loading ? (
              <div className="flex justify-center p-20"><Loader2 className="animate-spin text-accent" /></div>
            ) : (
              <div className="space-y-6">
                {workflows.map((wf) => (
                  <div key={wf.id} className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${
                          wf.status === 'active' ? 'bg-accent animate-pulse' : 
                          wf.status === 'completed' ? 'bg-emerald-500' : 
                          'bg-slate-700'
                        }`} />
                        <p className="text-sm font-bold text-slate-200">{wf.name}</p>
                      </div>
                      <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{wf.efficiency}% Eff.</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden border border-card-border">
                      <div 
                        className={`h-full transition-all duration-1000 ${
                          wf.status === 'active' ? 'bg-accent' : 
                          wf.status === 'completed' ? 'bg-emerald-500' : 
                          'bg-slate-700'
                        }`} 
                        style={{ width: `${(wf.steps_completed / wf.total_steps) * 100}%` }}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                       <p className="text-[10px] text-slate-600 font-bold uppercase">
                         Step {wf.steps_completed} of {wf.total_steps}
                       </p>
                       <p className="text-[10px] text-slate-600 font-bold uppercase">
                         Last run: {new Date(wf.last_run).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                       </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            <div className="mt-8 p-4 rounded-2xl bg-emerald-950/20 border border-accent/20">
               <div className="flex items-start gap-4">
                  <Target className="text-accent shrink-0" size={20} />
                  <div>
                     <h4 className="text-sm font-bold text-accent mb-1 uppercase tracking-tighter">AI Process Optimization</h4>
                     <p className="text-xs text-slate-400 leading-relaxed">
                       ELYX suggests merging the "Reconciliation" and "Sentiment" loops to save 14% of system resources and compute time.
                     </p>
                  </div>
               </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
