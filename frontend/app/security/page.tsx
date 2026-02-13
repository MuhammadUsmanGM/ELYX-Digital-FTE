"use client";

import { useEffect, useState, useRef } from "react";
import { 
  ShieldCheck, 
  Lock, 
  Key, 
  Eye, 
  AlertOctagon, 
  ShieldAlert, 
  Binary, 
  Fingerprint, 
  Server,
  Zap,
  CheckCircle2,
  ChevronRight,
  MoreVertical,
  Loader2,
  Terminal,
  Activity,
  Cpu,
  Globe,
  Radio
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import LoadingDots from "@/components/LoadingDots";

interface SecurityLog {
  id: string;
  timestamp: string;
  source: string;
  action: string;
  status: 'blocked' | 'verified' | 'flagged';
  protocol: string;
}

export default function SecurityPage() {
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [entropy, setEntropy] = useState(98.42);
  const [logs, setLogs] = useState<SecurityLog[]>([]);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setTimeout(() => setLoading(false), 1200);

    // Initial logs
    const initialLogs: SecurityLog[] = [
      { id: '1', timestamp: new Date().toLocaleTimeString(), source: '192.168.0.104', action: 'Handshake Attempt', status: 'verified', protocol: 'ECC-521' },
      { id: '2', timestamp: new Date().toLocaleTimeString(), source: '84.22.102.15', action: 'Neural Port Scan', status: 'blocked', protocol: 'CAUSAL-GATE' },
      { id: '3', timestamp: new Date().toLocaleTimeString(), source: 'INTERNAL-CORE', action: 'Entropy Refresh', status: 'verified', protocol: 'QUANTUM-GEN' },
    ];
    setLogs(initialLogs);

    // Live entropy simulation
    const interval = setInterval(() => {
      setEntropy(prev => {
        const delta = (Math.random() - 0.5) * 0.05;
        return Math.min(100, Math.max(95, prev + delta));
      });
    }, 2000);

    // Random log generation
    const logInterval = setInterval(() => {
      const sources = ['45.18.22.1', 'NODE-B', 'SAT-LINK-7', '10.0.0.4', 'GATEWAY-X'];
      const actions = ['Protocol Validation', 'Reality Sync Request', 'Causal Chain Audit', 'Packet Decryption', 'Identity Verification'];
      const statuses: ('blocked' | 'verified' | 'flagged')[] = ['blocked', 'verified', 'verified', 'verified', 'flagged'];
      const protocols = ['Q-LINK', 'SHA-3', 'RSA-4096', 'ECC', 'CAUSAL'];
      
      const newLog: SecurityLog = {
        id: Math.random().toString(36).substr(2, 9),
        timestamp: new Date().toLocaleTimeString(),
        source: sources[Math.floor(Math.random() * sources.length)],
        action: actions[Math.floor(Math.random() * actions.length)],
        status: statuses[Math.floor(Math.random() * statuses.length)],
        protocol: protocols[Math.floor(Math.random() * protocols.length)]
      };

      setLogs(prev => [...prev.slice(-14), newLog]);
    }, 3500);

    return () => {
      clearInterval(interval);
      clearInterval(logInterval);
    };
  }, []);

  const runScan = () => {
    setScanning(true);
    setTimeout(() => setScanning(false), 3000);
  };

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                <ShieldCheck size={24} />
              </div>
              <h1 className="text-4xl font-black tracking-tight text-white">Security Perimeter</h1>
            </div>
            <p className="text-slate-400 font-medium max-w-2xl">
              Absolute causal integrity maintained via triple-layer quantum encryption and zero-trust neural architecture.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden lg:flex flex-col items-end px-4 border-r border-card-border/50">
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Global Threat Level</span>
              <span className="text-emerald-500 font-black uppercase text-xs tracking-tighter flex items-center gap-1">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Alpha - Nominal
              </span>
            </div>
            <button 
              onClick={runScan}
              disabled={scanning}
              className="px-6 py-4 bg-red-500/10 border border-red-500/20 rounded-2xl font-black text-[10px] uppercase tracking-widest text-red-500 flex items-center gap-3 hover:bg-white hover:text-red-500 transition-all active:scale-95 disabled:opacity-50 group"
            >
              {scanning ? <Loader2 size={16} className="animate-spin" /> : <Eye size={16} className="group-hover:rotate-12 transition-transform" />}
              Scan Reality Leaks
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center p-40 gap-6">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full animate-pulse" />
              <Loader2 size={64} className="text-primary animate-spin relative" />
            </div>
            <div className="text-center space-y-2">
              <p className="text-slate-200 font-black uppercase tracking-[0.3em] text-sm">Initializing Defensive Layers</p>
              <p className="text-slate-500 text-xs font-mono flex items-center">Quantum Key Exchange in progress<LoadingDots /></p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* Left Column: Metrics & Logs */}
            <div className="lg:col-span-8 space-y-8">
              
              {/* Primary Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricCard 
                  label="Quantum Entropy" 
                  value={`${entropy.toFixed(2)}%`}
                  sub="Stability Level: S-Tier"
                  icon={<Radio className="text-primary" size={20} />}
                  progress={entropy}
                  color="cyan"
                />
                <MetricCard 
                  label="Encryption Depth" 
                  value="8192 Bit"
                  sub="CAUSAL-LAYER-7 ACTIVE"
                  icon={<Lock className="text-emerald-500" size={20} />}
                  progress={100}
                  color="emerald"
                />
                <MetricCard 
                  label="Active Firewalls" 
                  value="1,422"
                  sub="0 BREACHES (24H)"
                  icon={<Activity className="text-blue-500" size={20} />}
                  progress={100}
                  color="blue"
                />
              </div>

              {/* Live Firewall Feed */}
              <div className="glass-panel rounded-[2.5rem] overflow-hidden border-card-border/30">
                <div className="p-8 border-b border-card-border/20 bg-slate-900/40 flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-black text-white flex items-center gap-3">
                      <Terminal size={20} className="text-primary" />
                      Live Neural Firewall Feed
                    </h3>
                    <p className="text-xs text-slate-500 font-medium mt-1">Real-time packet analysis across all communication nodes.</p>
                  </div>
                  <div className="flex gap-2">
                    <div className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-[10px] font-black text-emerald-500 uppercase tracking-widest">
                       Auto-Defend Active
                    </div>
                  </div>
                </div>
                <div className="p-6 h-[400px] overflow-y-auto font-mono scrollbar-hide space-y-2 bg-slate-950/20">
                  {logs.map((log, i) => (
                    <div key={log.id} className="flex flex-col md:flex-row md:items-center gap-4 p-3 rounded-xl bg-slate-900/30 border border-card-border/10 animate-in fade-in slide-in-from-left-4 duration-500">
                      <span className="text-[10px] text-slate-600 min-w-[80px]">{log.timestamp}</span>
                      <div className="flex items-center gap-2 min-w-[120px]">
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          log.status === 'blocked' ? 'bg-red-500' : 
                          log.status === 'flagged' ? 'bg-amber-500' : 'bg-emerald-500'
                        }`} />
                        <span className="text-[10px] font-bold uppercase text-slate-300">{log.action}</span>
                      </div>
                      <span className="text-[10px] text-slate-500 flex-1 truncate">SOURCE: {log.source}</span>
                      <div className="flex items-center gap-4">
                        <span className="text-[9px] font-black text-slate-600 uppercase tracking-widest">{log.protocol}</span>
                        <span className={`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-tighter ${
                          log.status === 'blocked' ? 'bg-red-500/10 text-red-500' : 
                          log.status === 'flagged' ? 'bg-amber-500/10 text-amber-500' : 'bg-emerald-500/10 text-emerald-400'
                        }`}>
                          {log.status === 'blocked' ? 'DROP' : log.status === 'flagged' ? 'ISOLATE' : 'PASS'}
                        </span>
                      </div>
                    </div>
                  ))}
                  <div ref={logEndRef} />
                </div>
              </div>
            </div>

            {/* Right Column: Controls & Protocols */}
            <div className="lg:col-span-4 space-y-8">
              
              {/* Access Authorization */}
              <div className="glass-panel p-8 rounded-[2rem] border-card-border/30">
                <h3 className="text-lg font-black text-white mb-6 flex items-center gap-3">
                  <Fingerprint size={20} className="text-primary" />
                  Biometric Access
                </h3>
                <div className="space-y-4">
                  <AccessItem 
                    label="Master Identity" 
                    status="Verified" 
                    desc="Usman Mustafa / Personal AI ID" 
                    active={true}
                  />
                  <AccessItem 
                    label="Neural Link" 
                    status="Encrypted" 
                    desc="Local Environment Override" 
                    active={true}
                  />
                  <AccessItem 
                    label="Third-Party Delegates" 
                    status="Inactive" 
                    desc="No active external delegations" 
                    active={false}
                  />
                </div>
                <button className="w-full mt-6 py-4 bg-slate-900 border border-card-border rounded-2xl text-[10px] font-black text-slate-400 uppercase tracking-widest hover:text-white hover:border-primary/50 transition-all">
                  Manage Access Tokens
                </button>
              </div>

              {/* Active Protocols List */}
              <div className="glass-panel p-8 rounded-[2rem] border-card-border/30">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 rounded-lg bg-slate-900 text-primary">
                    <CheckCircle2 size={18} />
                  </div>
                  <h3 className="text-lg font-black text-white">Active Defense</h3>
                </div>
                <div className="space-y-5">
                   <ProtocolItem name="Causal Chain Anchoring" status="active" />
                   <ProtocolItem name="Quantum Key Rotation" status="active" />
                   <ProtocolItem name="Zero-Trust Neural Gate" status="active" />
                   <ProtocolItem name="Temporal Sync Protection" status="active" />
                   <ProtocolItem name="Reality Consistency Check" status="warning" />
                </div>
              </div>

              {/* Danger Zone */}
              <div className="glass-panel p-8 rounded-[2rem] border-red-500/10 bg-red-500/[0.02]">
                <h3 className="text-lg font-black text-red-500 mb-6 flex items-center gap-3">
                  <AlertOctagon size={20} />
                  System Redline
                </h3>
                <div className="space-y-4">
                  <button className="w-full py-5 bg-red-500 text-white rounded-3xl font-black text-xs uppercase tracking-[0.2em] hover:bg-white hover:text-red-500 transition-all shadow-xl shadow-red-500/20 active:scale-95">
                    Neural Core Purge
                  </button>
                  <p className="text-[9px] text-slate-600 text-center uppercase font-black leading-normal px-6">
                    Immediate irreversible termination of all neural memories and reality anchors.
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

function MetricCard({ label, value, sub, icon, progress, color }: any) {
  return (
    <div className="glass-panel p-8 rounded-[2rem] premium-hover group h-full flex flex-col justify-between">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="p-3 rounded-2xl bg-slate-900 border border-card-border group-hover:emerald-blue-glow transition-all">
            {icon}
          </div>
          <div className="flex flex-col items-end">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{label}</span>
            <span className="text-[10px] font-black text-emerald-500 uppercase tracking-tighter">Verified</span>
          </div>
        </div>
        <div>
          <h3 className="text-3xl font-black text-slate-100 mb-1">{value}</h3>
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{sub}</p>
        </div>
      </div>
      <div className="mt-6 space-y-2">
        <div className="flex justify-between text-[8px] font-black uppercase text-slate-600">
           <span>Load Integrity</span>
           <span>{progress.toFixed(0)}%</span>
        </div>
        <div className="w-full h-1 bg-slate-900 rounded-full overflow-hidden">
          <div 
             className={`h-full transition-all duration-1000 ${
               color === 'cyan' ? 'bg-primary' : 
               color === 'emerald' ? 'bg-emerald-500' : 'bg-blue-500'
             }`} 
             style={{ width: `${progress}%` }} 
          />
        </div>
      </div>
    </div>
  );
}

function AccessItem({ label, status, desc, active }: any) {
  return (
    <div className={`p-5 rounded-3xl border transition-all ${active ? 'bg-primary/5 border-primary/20' : 'bg-slate-900/40 border-card-border opacity-50'}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-black text-white uppercase tracking-wider">{label}</span>
        <span className={`px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-tighter ${active ? 'bg-primary text-slate-950' : 'bg-slate-800 text-slate-500'}`}>
          {status}
        </span>
      </div>
      <p className="text-[10px] text-slate-500 font-medium leading-relaxed">{desc}</p>
    </div>
  );
}

function ProtocolItem({ name, status }: { name: string, status: 'active' | 'warning' | 'disabled' }) {
  return (
    <div className="flex items-center justify-between p-2 rounded-xl group hover:bg-slate-900/50 transition-all">
      <div className="flex items-center gap-3">
        <div className={`w-1.5 h-1.5 rounded-full ${
          status === 'active' ? 'bg-emerald-500 animate-pulse' : 
          status === 'warning' ? 'bg-amber-500' : 'bg-slate-700'
        }`} />
        <span className="text-xs font-bold text-slate-300 group-hover:text-white transition-colors">{name}</span>
      </div>
      <CheckCircle2 size={12} className={status === 'active' ? 'text-primary' : 'text-slate-700'} />
    </div>
  );
}
