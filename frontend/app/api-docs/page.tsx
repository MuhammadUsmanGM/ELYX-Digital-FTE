"use client";

import { useState, useEffect } from "react";
import { 
  Terminal, 
  Code2, 
  Globe, 
  Lock, 
  Zap, 
  Copy, 
  Check, 
  Play, 
  ChevronRight, 
  Search,
  BookOpen,
  Cpu,
  Layers,
  Webhook,
  ArrowRight,
  Loader2
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import LoadingDots from "@/components/LoadingDots";

interface Endpoint {
  id: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  title: string;
  description: string;
  params?: { name: string; type: string; required: boolean; desc: string }[];
  requestBody?: string;
  response: string;
}

const ENDPOINTS: Endpoint[] = [
  {
    id: 'consciousness-state',
    method: 'GET',
    path: '/api/consciousness/state/{entity_id}',
    title: 'Get Consciousness State',
    description: 'Retrieves the current neural stability, phi score, and attention focus of a specific AI entity.',
    params: [
      { name: 'entity_id', type: 'string', required: true, desc: 'Unique identifier for the neural entity (e.g., system_core).' }
    ],
    response: `{
  "consciousness_state": {
    "id": "neural_v2_99",
    "phi": 98.42,
    "attention_focus": ["market_analysis", "causal_modeling"],
    "self_awareness": 0.92,
    "cognitive_load": 2.4
  },
  "timestamp": "2026-02-06T09:15:00Z"
}`
  },
  {
    id: 'reality-forecast',
    method: 'POST',
    path: '/api/reality/forecast',
    title: 'Initiate Reality Forecast',
    description: 'Trigger a new causal simulation to project business outcomes across divergent timelines.',
    requestBody: `{
  "scenario_name": "Global Expansion V2",
  "causal_anchors": ["revenue", "market_share"],
  "depth": "deep"
}`,
    response: `{
  "task_id": "sim_81023",
  "status": "simulating",
  "estimated_completion": "200ms",
  "causal_nodes_locked": 1422
}`
  },
  {
    id: 'task-chains',
    method: 'GET',
    path: '/api/tasks/chains',
    title: 'List Active Task Chains',
    description: 'Returns all currently executing autonomous task chains and their current neural status.',
    response: `{
  "active_chains": [
    {
      "id": "T-900",
      "status": "processing",
      "priority": "high",
      "progress": 0.82
    }
  ]
}`
  }
];

export default function ApiDocsPage() {
  const [activeEndpoint, setActiveEndpoint] = useState<Endpoint>(ENDPOINTS[0]);
  const [activeLang, setActiveLang] = useState<'javascript' | 'python' | 'curl'>('javascript');
  const [copied, setCopied] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const runTest = () => {
    setTesting(true);
    setTestResult(null);
    setTimeout(() => {
      setTesting(false);
      setTestResult(activeEndpoint.response);
    }, 800);
  };

  const getCodeSnippet = () => {
    const url = `https://api.elyx.ai${activeEndpoint.path}`;
    if (activeLang === 'javascript') {
      return `const response = await fetch('${url}', {
  method: '${activeEndpoint.method}',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }${activeEndpoint.requestBody ? `,\n  body: JSON.stringify(${activeEndpoint.requestBody})` : ''}
});
const data = await response.json();
console.log(data);`;
    }
    if (activeLang === 'python') {
      return `import requests

url = "${url}"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}

response = requests.${activeEndpoint.method.toLowerCase()}(
    url, 
    headers=headers${activeEndpoint.requestBody ? `, \n    json=${activeEndpoint.requestBody}` : ''}
)
print(response.json())`;
    }
    return `curl -X ${activeEndpoint.method} "${url}" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  ${activeEndpoint.requestBody ? `-d '${activeEndpoint.requestBody}'` : ''}`;
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-140px)] animate-in fade-in slide-in-from-bottom-4 duration-700">
        
        {/* Header Section */}
        <div className="flex items-center justify-between mb-8 px-2">
          <div className="space-y-1">
            <h1 className="text-4xl font-black tracking-tighter text-white flex items-center gap-3">
              <Terminal className="text-primary" size={32} />
              API <span className="text-primary italic">Developer Hub</span>
            </h1>
            <p className="text-slate-500 font-medium">Build multi-timeline integrations with the ELYX Neural Core.</p>
          </div>
          <div className="flex items-center gap-4">
             <div className="px-4 py-2 bg-slate-900 border border-card-border rounded-xl flex items-center gap-3">
                <Lock size={14} className="text-emerald-500" />
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">v2.0 Stable</span>
             </div>
             <button className="btn-premium-primary !px-6 !py-4 group">
               <BookOpen size={18} />
               Full Guide
               <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
             </button>
          </div>
        </div>

        <div className="flex-1 flex gap-8 min-h-0">
          
          {/* Navigation Sidebar */}
          <div className="w-80 flex flex-col gap-6">
            <div className="glass-panel rounded-3xl p-6 border-card-border/30 flex flex-col h-full">
               <div className="relative mb-6">
                  <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input 
                    placeholder="Search Endpoints..." 
                    className="w-full bg-slate-950 border border-card-border/50 rounded-xl py-3 pl-10 pr-4 text-xs font-bold text-slate-300 outline-none focus:border-primary/50 transition-all"
                  />
               </div>

               <div className="flex-1 overflow-y-auto pr-2 space-y-6 scrollbar-hide">
                  <div>
                    <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                       <Layers size={12} />
                       Core Intelligence
                    </h3>
                    <div className="space-y-2">
                      {ENDPOINTS.map((ep) => (
                        <button
                          key={ep.id}
                          onClick={() => setActiveEndpoint(ep)}
                          className={`w-full text-left p-3 rounded-xl transition-all group ${
                            activeEndpoint.id === ep.id 
                              ? 'bg-primary/10 border border-primary/20' 
                              : 'hover:bg-slate-900 border border-transparent'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                             <span className={`text-[8px] font-black px-1.5 py-0.5 rounded ${
                                ep.method === 'GET' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-primary/20 text-primary'
                             }`}>
                                {ep.method}
                             </span>
                             <span className={`text-xs font-bold transition-colors ${
                                activeEndpoint.id === ep.id ? 'text-white' : 'text-slate-500 group-hover:text-slate-300'
                             }`}>
                                {ep.title}
                             </span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                       <Webhook size={12} />
                       Event Webhooks
                    </h3>
                    <div className="p-4 rounded-2xl bg-slate-950/50 border border-dashed border-card-border/30 text-center">
                       <p className="text-[10px] font-bold text-slate-600 uppercase">Incoming Clusters</p>
                    </div>
                  </div>
               </div>

               <div className="mt-6 pt-6 border-t border-card-border/30">
                  <div className="p-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/10">
                    <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest mb-1">API Status</p>
                    <p className="text-[10px] text-slate-500 font-medium">Global nodes operational. Latency &lt; 20ms</p>
                  </div>
               </div>
            </div>
          </div>

          {/* Documentation Content */}
          <div className="flex-1 flex flex-col gap-8 overflow-y-auto pr-4 scrollbar-hide">
            
            {/* Main Info */}
            <div className="glass-panel rounded-[2.5rem] p-10 border-card-border/30">
               <div className="flex items-start justify-between mb-8">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                       <span className={`px-3 py-1 rounded-lg text-xs font-black ${
                          activeEndpoint.method === 'GET' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-primary/20 text-primary'
                       }`}>
                          {activeEndpoint.method}
                       </span>
                       <code className="text-xl font-mono text-slate-300 font-bold tracking-tight">
                          {activeEndpoint.path}
                       </code>
                    </div>
                    <h2 className="text-3xl font-black text-white">{activeEndpoint.title}</h2>
                    <p className="text-slate-500 font-medium mt-4 max-w-2xl leading-relaxed">
                       {activeEndpoint.description}
                    </p>
                  </div>
                  <button className="p-4 bg-slate-900 border border-card-border rounded-2xl text-slate-400 hover:text-primary transition-all">
                     <Copy size={20} />
                  </button>
               </div>

               {activeEndpoint.params && (
                 <div className="mt-10">
                    <h3 className="text-sm font-black text-white uppercase tracking-widest mb-6">Parameters</h3>
                    <div className="rounded-2xl border border-card-border/30 overflow-hidden">
                       <table className="w-full text-left text-xs">
                          <thead className="bg-slate-900/50 border-b border-card-border/30">
                             <tr>
                                <th className="p-4 font-black uppercase text-slate-500 tracking-widest">Name</th>
                                <th className="p-4 font-black uppercase text-slate-500 tracking-widest">Type</th>
                                <th className="p-4 font-black uppercase text-slate-500 tracking-widest">Description</th>
                             </tr>
                          </thead>
                          <tbody className="divide-y divide-card-border/20">
                             {activeEndpoint.params.map((p, i) => (
                               <tr key={i} className="hover:bg-white/[0.02]">
                                  <td className="p-4">
                                     <code className="text-primary font-bold">{p.name}</code>
                                     {p.required && <span className="ml-2 text-red-500/50 italic text-[10px]">required</span>}
                                  </td>
                                  <td className="p-4 text-slate-400">{p.type}</td>
                                  <td className="p-4 text-slate-500">{p.desc}</td>
                               </tr>
                             ))}
                          </tbody>
                       </table>
                    </div>
                 </div>
               )}
            </div>

            {/* Code & Testing Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
               
               {/* Code Preview */}
               <div className="glass-panel rounded-[2.5rem] overflow-hidden flex flex-col border-card-border/30">
                  <div className="p-6 bg-slate-900/50 border-b border-card-border/30 flex items-center justify-between">
                     <div className="flex gap-2">
                        {['javascript', 'python', 'curl'].map((lang) => (
                          <button
                            key={lang}
                            onClick={() => setActiveLang(lang as any)}
                            className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest transition-all ${
                              activeLang === lang ? 'bg-primary/20 text-primary' : 'text-slate-500 hover:text-slate-300'
                            }`}
                          >
                            {lang}
                          </button>
                        ))}
                     </div>
                     <button 
                       onClick={() => copyToClipboard(getCodeSnippet())}
                       className="text-slate-500 hover:text-white transition-colors"
                     >
                        {copied ? <Check size={16} className="text-emerald-500" /> : <Copy size={16} />}
                     </button>
                  </div>
                  <div className="flex-1 p-6 bg-slate-950 font-mono text-[11px] leading-relaxed text-slate-400 overflow-x-auto">
                     <pre>
                        <code>{getCodeSnippet()}</code>
                     </pre>
                  </div>
               </div>

               {/* Result / Terminal */}
               <div className="glass-panel rounded-[2.5rem] overflow-hidden flex flex-col border-card-border/30">
                  <div className="p-6 bg-slate-900/50 border-b border-card-border/30 flex items-center justify-between">
                     <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                        <Play size={10} className="text-emerald-500 fill-emerald-500" />
                        Response Terminal
                     </h4>
                     <button 
                        onClick={runTest}
                        disabled={testing}
                        className="btn-premium-primary !px-4 !py-1.5 !rounded-lg !text-[9px] group"
                     >
                        {testing ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
                        Execute Request
                     </button>
                  </div>
                  <div className="flex-1 p-6 bg-slate-950 font-mono text-[11px] leading-relaxed text-emerald-400/80 overflow-y-auto max-h-[300px] scrollbar-hide">
                     {testResult ? (
                       <pre className="animate-in fade-in slide-in-from-top-2">
                          <code>{testResult}</code>
                       </pre>
                     ) : (
                        <p className="text-slate-700 italic flex items-center">No request executed yet. System idle<LoadingDots /></p>
                     )}
                  </div>
               </div>

            </div>

         </div>

        </div>
      </div>
    </DashboardLayout>
  );
}
