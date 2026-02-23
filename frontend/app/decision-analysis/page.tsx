"use client";

import { useEffect, useState } from "react";
import {
  Target,
  TrendingUp,
  AlertTriangle,
  Loader2,
  BarChart3,
  PieChart,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle2,
  Clock,
  Layers
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import LoadingDots from "@/components/LoadingDots";

interface DecisionScenario {
  id: string;
  name: string;
  description: string;
  impact_score: number;
  probability: number;
  status: 'analyzing' | 'ready' | 'action_required';
  type: 'strategic' | 'operational' | 'financial';
}

interface ImpactMetrics {
  total_decisions: number;
  high_impact: number;
  avg_confidence: number;
  pending_review: number;
}

export default function DecisionAnalysisPage() {
  const [scenarios, setScenarios] = useState<DecisionScenario[]>([]);
  const [metrics, setMetrics] = useState<ImpactMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      // Simulated data - replace with actual API calls
      const simulatedScenarios: DecisionScenario[] = [
        {
          id: "DEC-2026-001",
          name: "Client Payment Delay - ABC Corp",
          description: "Payment 15 days overdue. Recommend automated reminder sequence or escalation to collections.",
          impact_score: 72,
          probability: 0.85,
          status: 'action_required',
          type: 'financial'
        },
        {
          id: "DEC-2026-002",
          name: "Q2 Marketing Budget Allocation",
          description: "Analyze ROI from Q1 channels and recommend budget redistribution for Q2 campaigns.",
          impact_score: 89,
          probability: 0.92,
          status: 'analyzing',
          type: 'strategic'
        },
        {
          id: "DEC-2026-003",
          name: "Vendor Contract Renewal - TechStack Inc",
          description: "Contract expires in 45 days. Evaluate usage patterns and negotiate renewal terms.",
          impact_score: 64,
          probability: 0.78,
          status: 'ready',
          type: 'operational'
        },
        {
          id: "DEC-2026-004",
          name: "Hiring Decision - Senior Developer Role",
          description: "Candidate evaluation complete. Compare offer competitiveness and team fit analysis.",
          impact_score: 81,
          probability: 0.88,
          status: 'action_required',
          type: 'strategic'
        },
      ];

      const simulatedMetrics: ImpactMetrics = {
        total_decisions: 47,
        high_impact: 12,
        avg_confidence: 87,
        pending_review: 5
      };

      setScenarios(simulatedScenarios);
      setMetrics(simulatedMetrics);
    } catch (error) {
      console.error("Decision analysis fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const runAnalysis = () => {
    setAnalyzing(true);
    setTimeout(() => {
      setAnalyzing(false);
      loadData();
    }, 2500);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready': return 'text-emerald-500 border-emerald-500/20 bg-emerald-500/10';
      case 'analyzing': return 'text-primary border-primary/20 bg-primary/10';
      case 'action_required': return 'text-amber-500 border-amber-500/20 bg-amber-500/10';
      default: return 'text-slate-500 border-slate-500/20';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'strategic': return 'text-purple-500 bg-purple-500/10';
      case 'operational': return 'text-blue-500 bg-blue-500/10';
      case 'financial': return 'text-emerald-500 bg-emerald-500/10';
      default: return 'text-slate-500';
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">

        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 px-2">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                <Target size={24} />
              </div>
              <h1 className="text-4xl font-black tracking-tight text-white">Decision Analysis</h1>
            </div>
            <p className="text-slate-400 font-medium max-w-2xl">
              AI-powered impact assessment and scenario modeling for strategic business decisions.
            </p>
          </div>
          <div className="flex gap-4">
             <button
               onClick={runAnalysis}
               disabled={analyzing}
               className="group relative px-8 py-4 bg-slate-950 border border-primary/30 rounded-2xl font-black text-xs uppercase tracking-widest text-primary overflow-hidden transition-all hover:border-primary hover:shadow-[0_0_30px_rgba(6,182,212,0.2)] active:scale-95 disabled:opacity-50"
             >
               <span className="relative z-10 flex items-center gap-2">
                 {analyzing ? <Loader2 size={16} className="animate-spin" /> : <TrendingUp size={16} />}
                  {analyzing ? <span className="flex items-center">Analyzing<LoadingDots /></span> : "Run Impact Analysis"}
               </span>
               <div className="absolute inset-0 bg-primary/10 opacity-0 group-hover:opacity-100 transition-opacity" />
             </button>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center p-40 gap-8">
            <Loader2 size={64} className="text-primary animate-spin" />
            <div className="text-center space-y-2">
               <p className="text-slate-200 font-black uppercase tracking-[0.4em] text-sm flex items-center">Loading Decision Models<LoadingDots /></p>
               <p className="text-slate-500 text-xs font-mono">Processing impact scenarios...</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

            {/* Sidebar: Metrics */}
            <div className="lg:col-span-3 space-y-6">
              <div className="glass-panel p-8 rounded-[2.5rem] border-primary/20 relative overflow-hidden group">
                <div className="absolute -top-12 -right-12 p-4 opacity-[0.03] group-hover:scale-110 transition-transform duration-1000">
                  <BarChart3 size={200} />
                </div>

                <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-8 flex items-center gap-2">
                  <Layers size={14} className="text-primary" />
                  Decision Metrics
                </h3>

                <div className="space-y-8">
                  <div className="relative">
                    <p className="text-[10px] font-black text-slate-500 uppercase mb-4 tracking-tighter">Total Decisions</p>
                    <div className="flex items-baseline gap-2">
                      <h2 className="text-5xl font-black text-white tracking-tighter">{metrics?.total_decisions}</h2>
                      <span className="text-emerald-500 font-black text-[10px] uppercase tracking-widest flex items-center">
                        <ArrowUpRight size={14} /> +12%
                      </span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex justify-between items-end">
                      <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Avg Confidence</p>
                      <p className="text-[10px] font-black text-primary uppercase">{metrics?.avg_confidence}%</p>
                    </div>
                    <div className="w-full bg-slate-900/80 h-1.5 rounded-full overflow-hidden border border-card-border/50">
                      <div className="bg-primary h-full shadow-[0_0_10px_rgba(6,182,212,0.5)]" style={{ width: `${metrics?.avg_confidence}%` }} />
                    </div>
                  </div>

                  <div className="p-5 rounded-3xl bg-slate-950/50 border border-card-border/30 backdrop-blur-sm">
                    <div className="flex items-center gap-2 text-amber-500 mb-3">
                      <AlertTriangle size={14} className="fill-amber-500/20" />
                      <span className="text-[10px] font-black uppercase tracking-[0.2em]">Pending Review</span>
                    </div>
                    <p className="text-2xl font-black text-white">{metrics?.pending_review}</p>
                    <p className="text-[10px] text-slate-500 leading-relaxed font-medium mt-1">
                      High-impact decisions requiring approval
                    </p>
                  </div>
                </div>
              </div>

              {/* Quick Stats */}
              <div className="glass-panel p-6 rounded-[2rem] border-card-border/20">
                <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-6 flex items-center justify-between">
                  Impact Distribution
                </h4>
                <div className="space-y-5">
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">High Impact</span>
                    <span className="text-[10px] font-black text-red-500">{metrics?.high_impact}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Medium Impact</span>
                    <span className="text-[10px] font-black text-amber-500">23</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Low Impact</span>
                    <span className="text-[10px] font-black text-emerald-500">12</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Area: Scenarios */}
            <div className="lg:col-span-9 space-y-8">

               {/* Metrics Row */}
               <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="glass-panel p-6 rounded-3xl border-card-border/30 flex items-center justify-between">
                    <div>
                      <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">This Week</p>
                      <h4 className="text-xl font-black text-slate-100">8 decisions</h4>
                    </div>
                    <div className="text-[10px] font-black px-2 py-1 rounded-lg bg-slate-900 border border-card-border text-emerald-500">
                      +2.4%
                    </div>
                  </div>
                  <div className="glass-panel p-6 rounded-3xl border-card-border/30 flex items-center justify-between">
                    <div>
                      <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Avg Impact</p>
                      <h4 className="text-xl font-black text-slate-100">67%</h4>
                    </div>
                    <div className="text-[10px] font-black px-2 py-1 rounded-lg bg-slate-900 border border-card-border text-primary">
                      +8%
                    </div>
                  </div>
                  <div className="glass-panel p-6 rounded-3xl border-card-border/30 flex items-center justify-between">
                    <div>
                      <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Implementation</p>
                      <h4 className="text-xl font-black text-slate-100">34 active</h4>
                    </div>
                    <div className="text-[10px] font-black px-2 py-1 rounded-lg bg-slate-900 border border-card-border text-purple-500">
                      On track
                    </div>
                  </div>
               </div>

               {/* Scenario Cards */}
               <div className="space-y-6">
                  <div className="flex items-center justify-between px-2">
                    <h3 className="text-xl font-black text-white flex items-center gap-3">
                      <BarChart3 size={22} className="text-primary" />
                      Active Decision Scenarios
                    </h3>
                    <div className="flex gap-3">
                      <select className="bg-slate-900 border border-card-border rounded-xl px-4 py-2 text-[10px] font-black text-slate-500 uppercase tracking-widest outline-none focus:border-primary transition-all">
                        <option>All Types</option>
                        <option>Strategic</option>
                        <option>Operational</option>
                        <option>Financial</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {scenarios.map((s) => (
                      <ScenarioCard
                        key={s.id}
                        scenario={s}
                        active={selectedScenario === s.id}
                        onClick={() => setSelectedScenario(s.id)}
                      />
                    ))}
                  </div>
               </div>

               {/* Analysis Canvas */}
               <div className="glass-panel rounded-[3rem] p-10 relative overflow-hidden border-primary/20 bg-primary/[0.01]">
                  <div className="flex items-center justify-between mb-10">
                    <div>
                      <h3 className="text-xl font-black text-white flex items-center gap-3">
                        <PieChart size={24} className="text-primary" />
                        Impact Projection Matrix
                      </h3>
                      <p className="text-xs text-slate-500 font-medium mt-1">Multi-factor analysis of selected decision outcomes.</p>
                    </div>
                    <div className="px-4 py-2 bg-slate-950 border border-card-border rounded-2xl flex items-center gap-3">
                      <div className="w-2 h-2 rounded-full bg-primary animate-ping" />
                      <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest">Live Analysis</span>
                    </div>
                  </div>

                  {/* Impact Visualization */}
                  <div className="relative h-[300px] mb-8 bg-slate-950/40 rounded-[2rem] border border-card-border/30 overflow-hidden">
                    <div className="absolute inset-0 grid grid-cols-6 grid-rows-4 gap-px opacity-10">
                      {Array.from({ length: 24 }).map((_, i) => (
                        <div key={i} className="border-[0.5px] border-slate-500" />
                      ))}
                    </div>

                    <div className="absolute inset-0 flex items-center justify-center p-12">
                      <div className="w-full h-full flex items-center justify-center gap-12">
                        <div className="flex-1 text-center">
                          <p className="text-[10px] font-black text-slate-500 uppercase mb-2">Positive Impact</p>
                          <p className="text-4xl font-black text-emerald-500">+73%</p>
                        </div>
                        <div className="w-px h-24 bg-slate-700" />
                        <div className="flex-1 text-center">
                          <p className="text-[10px] font-black text-slate-500 uppercase mb-2">Risk Factor</p>
                          <p className="text-4xl font-black text-amber-500">12%</p>
                        </div>
                        <div className="w-px h-24 bg-slate-700" />
                        <div className="flex-1 text-center">
                          <p className="text-[10px] font-black text-slate-500 uppercase mb-2">Confidence</p>
                          <p className="text-4xl font-black text-primary">87%</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Action Bar */}
                  <div className="p-6 rounded-[2rem] bg-slate-900/50 border border-card-border/50 flex items-center justify-between">
                    <div className="flex items-center gap-5">
                      <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary shadow-[0_0_20px_rgba(6,182,212,0.2)]">
                        <CheckCircle2 size={24} />
                      </div>
                      <div>
                        <p className="text-sm font-black text-slate-100 uppercase tracking-tight">Analysis Complete</p>
                        <p className="text-[10px] text-slate-500 font-medium">Ready for review and implementation planning.</p>
                      </div>
                    </div>
                    <button className="px-6 py-3 bg-primary text-white rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-white hover:text-primary transition-all shadow-lg shadow-primary/20 active:scale-95">
                      Review Recommendations
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

function ScenarioCard({ scenario, active, onClick }: { scenario: DecisionScenario, active: boolean, onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      className={`glass-panel p-8 rounded-[2.5rem] transition-all duration-500 cursor-pointer group relative overflow-hidden border-2 ${
        active ? 'border-primary/50 bg-primary/[0.02] shadow-[0_0_40px_rgba(6,182,212,0.1)]' : 'border-card-border/30 hover:border-primary/20'
      }`}
    >
      <div className="absolute top-0 right-0 w-48 h-48 bg-primary/5 blur-[80px] pointer-events-none group-hover:scale-125 transition-transform duration-1000" />

      <div className="flex items-start justify-between mb-8 relative z-10">
        <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border ${getStatusColor(scenario.status)}`}>
          {scenario.status.replace('_', ' ')}
        </span>
        <span className={`px-3 py-1 rounded-lg text-[9px] font-black uppercase ${getTypeColor(scenario.type)}`}>
          {scenario.type}
        </span>
      </div>

      <div className="relative z-10 mb-8">
        <h4 className="text-xl font-black text-slate-100 mb-3 group-hover:text-primary transition-colors leading-tight">{scenario.name}</h4>
        <p className="text-xs text-slate-500 font-medium leading-relaxed line-clamp-2">{scenario.description}</p>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-8 relative z-10">
        <div className="p-5 rounded-3xl bg-slate-900/60 border border-card-border/50 group-hover:bg-slate-900 transition-colors">
          <p className="text-[10px] font-black text-slate-600 uppercase mb-2 tracking-[0.1em]">Impact Score</p>
          <div className="flex items-center justify-between">
            <span className="text-xl font-black text-slate-200">{scenario.impact_score}%</span>
            <Target size={18} className="text-primary/40" />
          </div>
        </div>
        <div className="p-5 rounded-3xl bg-slate-900/60 border border-card-border/50 group-hover:bg-slate-900 transition-colors">
          <p className="text-[10px] font-black text-slate-600 uppercase mb-2 tracking-[0.1em]">Probability</p>
          <div className="flex items-center justify-between">
            <span className="text-xl font-black text-slate-200">{(scenario.probability * 100).toFixed(0)}%</span>
            <TrendingUp size={18} className="text-accent/40" />
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between pt-6 border-t border-card-border/30 relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-slate-900 border border-card-border flex items-center justify-center text-primary">
            <Layers size={14} />
          </div>
          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{scenario.id}</span>
        </div>
        <button className="flex items-center gap-2 text-[10px] font-black text-primary uppercase tracking-widest hover:gap-3 transition-all group-hover:text-white">
          View Analysis
          <ArrowUpRight size={14} />
        </button>
      </div>
    </div>
  );
}
