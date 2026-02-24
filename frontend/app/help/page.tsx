"use client";

import { useState } from "react";
import { 
  HelpCircle, 
  Search, 
  Book, 
  PlayCircle, 
  LifeBuoy, 
  ChevronRight, 
  ExternalLink, 
  MessageSquare, 
  FileText,
  Zap,
  ArrowRight,
  Plus,
  Clock,
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";

const KB_CATEGORIES = [
  { id: 'getting-started', title: 'Onboarding & Setup', count: 12, icon: <Zap className="text-primary" size={18} /> },
  { id: 'security', title: 'Data & Privacy', count: 8, icon: <LifeBuoy className="text-emerald-500" size={18} /> },
  { id: 'system-sync', title: 'System Synchronization', count: 15, icon: <Book className="text-blue-500" size={18} /> },
  { id: 'performance-modeling', title: 'Performance Forecasting', count: 6, icon: <FileText className="text-purple-500" size={18} /> },
];

const TUTORIALS = [
  { title: "Your First System Sync", duration: "4:20", level: "Beginner", image: "https://images.unsplash.com/photo-1620712943543-bcc4628c6bb5?auto=format&fit=crop&q=80&w=400" },
  { title: "Advanced Workflow Logic", duration: "12:45", level: "Expert", image: "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=400" },
  { title: "Security Protocols 101", duration: "8:12", level: "Intermediate", image: "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=400" },
];

export default function HelpPage() {
  const [activeTab, setActiveTab] = useState<'kb' | 'tutorials' | 'support'>('kb');
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 px-2">
          <div className="space-y-2">
            <h1 className="text-5xl font-black tracking-tighter text-white">
              Intelligence <span className="text-primary italic">Center</span>
            </h1>
            <p className="text-slate-500 font-medium max-w-xl">
              Access the foundational knowledge, tutorials, and support required to master the <span className="text-slate-300 font-bold">ELYX System Core</span>.
            </p>
          </div>
          <div className="flex items-center gap-4">
             <div className="relative group w-80">
                <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-hover:text-primary transition-colors" />
                <input 
                  type="text" 
                  placeholder="Query knowledge base..." 
                  className="w-full bg-slate-900 border border-card-border rounded-2xl py-4 pl-12 pr-6 text-sm font-bold text-slate-300 outline-none focus:border-primary/50 transition-all shadow-2xl"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
             </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 p-1 bg-slate-900/50 border border-card-border/50 rounded-2xl w-fit">
           <TabButton active={activeTab === 'kb'} onClick={() => setActiveTab('kb')} icon={<Book size={16} />} label="Knowledge Base" />
           <TabButton active={activeTab === 'tutorials'} onClick={() => setActiveTab('tutorials')} icon={<PlayCircle size={16} />} label="Tutorials" />
           <TabButton active={activeTab === 'support'} onClick={() => setActiveTab('support')} icon={<MessageSquare size={16} />} label="Support Tickets" />
        </div>

        {/* Content Area */}
        <div className="min-h-[600px]">
          {activeTab === 'kb' && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in duration-500">
               {/* Categories */}
               <div className="lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                  {KB_CATEGORIES.map((cat) => (
                    <div key={cat.id} className="glass-panel p-8 rounded-[2.5rem] border-card-border/30 hover:border-primary/30 transition-all group cursor-pointer relative overflow-hidden">
                       <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:scale-110 transition-transform duration-700">
                          {cat.icon}
                       </div>
                       <div className="p-3 rounded-2xl bg-slate-900 border border-card-border mb-6 group-hover:shadow-[0_0_15px_rgba(6,182,212,0.1)] transition-all inline-block">
                          {cat.icon}
                       </div>
                       <h3 className="text-xl font-black text-white mb-2">{cat.title}</h3>
                       <p className="text-xs text-slate-500 font-medium mb-6 uppercase tracking-widest">{cat.count} Intelligence Units</p>
                       <div className="space-y-3">
                          <p className="text-sm text-slate-400 font-medium flex items-center justify-between group/item hover:text-white transition-colors">
                             Setting up your system anchor
                             <ChevronRight size={14} className="text-slate-600 group-hover/item:translate-x-1 transition-transform" />
                          </p>
                          <p className="text-sm text-slate-400 font-medium flex items-center justify-between group/item hover:text-white transition-colors">
                             Distributed system security
                             <ChevronRight size={14} className="text-slate-600 group-hover/item:translate-x-1 transition-transform" />
                          </p>
                       </div>
                    </div>
                  ))}
               </div>

               {/* Trending Side */}
               <div className="lg:col-span-4 space-y-8">
                  <div className="glass-panel p-8 rounded-[2rem] border-card-border/30">
                     <h3 className="text-lg font-black text-white mb-6">Trending Queries</h3>
                     <div className="space-y-4">
                        {['How to optimize system stability?', 'Connecting to WhatsApp API', 'System divergence warnings', 'Auth token rotation'].map((q, i) => (
                           <div key={i} className="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-900 transition-colors cursor-pointer group">
                              <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                              <span className="text-sm font-bold text-slate-400 group-hover:text-slate-200 transition-colors">{q}</span>
                           </div>
                        ))}
                     </div>
                  </div>

                  <div className="glass-panel p-8 rounded-[2rem] bg-primary/[0.02] border-primary/20">
                     <h3 className="text-lg font-black text-white mb-4">System Assistant</h3>
                     <p className="text-xs text-slate-500 font-medium leading-relaxed mb-6 italic underline decoration-primary/30">
                        "I am trained on our entire documentation corpus. Ask me any technical query for immediate synthesis."
                     </p>
                     <button className="w-full py-4 bg-primary text-slate-950 rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-white transition-all shadow-xl shadow-primary/20">
                        Initialize AI Support
                     </button>
                  </div>
               </div>
            </div>
          )}

          {activeTab === 'tutorials' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
               {TUTORIALS.map((video, i) => (
                 <div key={i} className="glass-panel overflow-hidden rounded-[2.5rem] border-card-border/30 group hover:border-primary/20 transition-all">
                    <div className="relative h-48 bg-slate-900 overflow-hidden">
                       <img src={video.image} className="w-full h-full object-cover opacity-60 group-hover:scale-110 transition-transform duration-1000" alt={video.title} />
                       <div className="absolute inset-0 flex items-center justify-center">
                          <button className="w-14 h-14 rounded-full bg-primary/20 border border-primary/50 flex items-center justify-center backdrop-blur-md group-hover:bg-primary group-hover:text-slate-950 transition-all scale-90 group-hover:scale-100">
                             <PlayCircle size={32} />
                          </button>
                       </div>
                       <div className="absolute bottom-4 right-4 px-3 py-1 bg-slate-950/80 border border-card-border rounded-lg text-[10px] font-black text-white">
                          {video.duration}
                       </div>
                    </div>
                    <div className="p-8">
                       <div className="flex items-center justify-between mb-4">
                          <span className="text-[10px] font-black text-primary uppercase tracking-widest">{video.level}</span>
                          <span className="text-[10px] font-bold text-slate-500 uppercase">Module {i+1}</span>
                       </div>
                       <h3 className="text-xl font-black text-white mb-4 group-hover:text-primary transition-colors">{video.title}</h3>
                       <button className="flex items-center gap-2 text-[10px] font-black text-slate-400 uppercase tracking-widest hover:text-white transition-colors">
                          Resume Learning <ArrowRight size={14} />
                       </button>
                    </div>
                 </div>
               ))}
            </div>
          )}

          {activeTab === 'support' && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in duration-500">
               {/* Left: Ticket Statistics */}
               <div className="lg:col-span-4 space-y-6">
                  <div className="glass-panel p-8 rounded-[2.5rem] border-card-border/30">
                     <h3 className="text-lg font-black text-white mb-8">Active Tickets</h3>
                     <div className="space-y-6">
                        <TicketStat label="Open Inquiries" value={2} color="text-primary" />
                        <TicketStat label="Resolved (30d)" value={14} color="text-emerald-500" />
                        <TicketStat label="Avg Response" value="2h 45m" color="text-blue-500" />
                     </div>
                     <button className="w-full mt-10 py-5 bg-slate-900 border border-card-border rounded-2xl font-black text-xs text-white uppercase tracking-widest hover:bg-white hover:text-slate-950 transition-all flex items-center justify-center gap-2 group">
                        <Plus size={18} className="group-hover:rotate-90 transition-transform" />
                        Open New Support Ticket
                     </button>
                  </div>
               </div>

               {/* Right: Ticket List */}
               <div className="lg:col-span-8">
                  <div className="glass-panel p-1 border-card-border/30 rounded-[2.5rem] overflow-hidden">
                     <div className="p-8 border-b border-card-border/30 bg-slate-900/30">
                        <h3 className="text-xl font-black text-white">Recent Interactions</h3>
                     </div>
                     <div className="divide-y divide-card-border/20">
                        <TicketItem 
                          id="TKT-8842" 
                          subject="System Sync Lag on Node 7" 
                          status="open" 
                          date="Feb 06, 2026"
                          icon={<AlertCircle className="text-red-400" size={18} />}
                        />
                        <TicketItem 
                          id="TKT-8812" 
                          subject="Onboarding Guidance Query" 
                          status="processing" 
                          date="Feb 05, 2026"
                          icon={<Clock className="text-primary" size={18} />}
                        />
                        <TicketItem 
                          id="TKT-8765" 
                          subject="Priority Deployment Verification" 
                          status="resolved" 
                          date="Jan 30, 2026"
                          icon={<CheckCircle2 className="text-emerald-500" size={18} />}
                        />
                     </div>
                  </div>
               </div>
            </div>
          )}
        </div>

      </div>
    </DashboardLayout>
  );
}

function TabButton({ active, onClick, icon, label }: any) {
  return (
    <button 
      onClick={onClick}
      className={`flex items-center gap-3 px-6 py-3 rounded-xl text-xs font-black uppercase tracking-widest transition-all ${
        active 
          ? 'bg-primary text-slate-950 shadow-[0_0_20px_rgba(6,182,212,0.3)]' 
          : 'text-slate-500 hover:text-slate-300'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

function TicketStat({ label, value, color }: any) {
  return (
    <div className="flex items-center justify-between">
       <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{label}</span>
       <span className={`text-xl font-black ${color}`}>{value}</span>
    </div>
  );
}

function TicketItem({ id, subject, status, date, icon }: any) {
  return (
    <div className="p-6 hover:bg-slate-900 transition-colors group cursor-pointer">
       <div className="flex items-center justify-between gap-6">
          <div className="flex items-center gap-4">
             <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-card-border flex items-center justify-center">
                {icon}
             </div>
             <div>
                <div className="flex items-center gap-3 mb-1">
                   <p className="text-sm font-black text-slate-200 group-hover:text-primary transition-colors">{subject}</p>
                   <span className="text-[10px] font-mono text-slate-600">#{id}</span>
                </div>
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{date}</p>
             </div>
          </div>
          <div className="flex items-center gap-4">
             <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter border ${
                status === 'open' ? 'text-red-400 border-red-400/20 bg-red-400/5' :
                status === 'processing' ? 'text-primary border-primary/20 bg-primary/5' :
                'text-emerald-500 border-emerald-500/20 bg-emerald-500/5'
             }`}>
                {status}
             </span>
             <ChevronRight size={18} className="text-slate-700 group-hover:text-primary group-hover:translate-x-1 transition-all" />
          </div>
       </div>
    </div>
  );
}
