"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Cpu, 
  Zap, 
  Shield, 
  Settings, 
  Mail, 
  Slack, 
  MessageSquare, 
  ChevronRight, 
  ChevronLeft, 
  CheckCircle2, 
  BrainCircuit,
  Lock,
  Globe2,
  Database,
  Terminal,
  Unplug,
  Loader2
} from "lucide-react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import Image from "next/image";
import { saveOnboardingData } from "@/lib/api";
import { toast } from "react-hot-toast";
import LoadingDots from "@/components/LoadingDots";

type Step = 1 | 2 | 3 | 4;

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState<Step>(1);
  const [loading, setLoading] = useState(false);
  const [anthropicKey, setAnthropicKey] = useState("");
  const [selectedChannels, setSelectedChannels] = useState<string[]>([]);
  const router = useRouter();

  const channels = [
    { id: 'email', name: 'Email Connector', icon: <Mail size={18} />, desc: 'Primary communication channel' },
    { id: 'slack', name: 'Slack Integration', icon: <Slack size={18} />, desc: 'Real-time internal workspace' },
    { id: 'whatsapp', name: 'WhatsApp Secure', icon: <MessageSquare size={18} />, desc: 'End-to-end encrypted mobility' },
    { id: 'linkedin', name: 'LinkedIn Professional', icon: <Globe2 size={18} />, desc: 'B2B growth & outreach' },
  ];

  useEffect(() => {
    const checkUser = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        router.push("/auth");
      }
    };
    checkUser();
  }, [router]);

  const handleNext = () => {
    if (currentStep === 2 && !anthropicKey) {
      toast.error("Please provide a valid Anthropic API Security Token.");
      return;
    }
    if (currentStep === 3 && selectedChannels.length === 0) {
      toast.error("At least one communication vector must be synchronized.");
      return;
    }

    if (currentStep < 4) {
      setCurrentStep((prev) => (prev + 1) as Step);
      toast.success(`Module ${currentStep} Calibrated`, {
        icon: '⚙️',
        style: {
          background: '#020617',
          color: '#fff',
          border: '1px solid rgba(6, 182, 212, 0.2)',
          fontSize: '10px',
          fontWeight: 'bold',
          textTransform: 'uppercase'
        }
      });
    }
    else finishOnboarding();
  };

  const handleBack = () => {
    if (currentStep > 1) setCurrentStep((prev) => (prev - 1) as Step);
  };

  const toggleChannel = (id: string) => {
    const isSelecting = !selectedChannels.includes(id);
    setSelectedChannels(prev => 
      prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id]
    );
    
    if (isSelecting) {
      toast.success(`Channel Enabled: ${id}`, {
        duration: 2000,
        position: 'bottom-center'
      });
    }
  };

  const finishOnboarding = async () => {
    setLoading(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        await saveOnboardingData({
          user_id: user.id,
          anthropic_key: anthropicKey,
          selected_channels: selectedChannels
        });
      }
      
      toast.success("System Link Established. Welcome to the Workspace.", {
        duration: 4000
      });

      setTimeout(() => {
        setLoading(false);
        router.push("/dashboard");
      }, 2500);
    } catch (error) {
       console.error("Onboarding failed", error);
       toast.error("Handshake Failed: Database storage error.");
       setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-white flex flex-col relative overflow-hidden selection:bg-primary/30">
      <div className="absolute inset-0 z-0 opacity-10 pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#131f33_1px,transparent_1px),linear-gradient(to_bottom,#131f33_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
      </div>

      <div className="relative z-10 w-full pt-12 px-8 flex flex-col items-center">
        <div className="w-full max-w-4xl flex items-center justify-between mb-4">
           <div className="flex items-center gap-3">
              <Image src="/icon.png" alt="ELYX" width={32} height={32} />
              <span className="text-xs font-black tracking-[0.3em] text-slate-500 uppercase">System Provisioning v2.0</span>
           </div>
           <div className="text-[10px] font-black text-primary tracking-widest uppercase">
             Step {currentStep} of 4
           </div>
        </div>
        <div className="w-full max-w-4xl h-1 bg-slate-900 rounded-full overflow-hidden border border-white/5">
           <motion.div 
             initial={{ width: "25%" }}
             animate={{ width: `${(currentStep / 4) * 100}%` }}
             className="h-full bg-gradient-to-r from-primary to-indigo-500 shadow-[0_0_10px_rgba(6,182,212,0.5)]"
           />
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6 relative z-10">
        <AnimatePresence mode="wait">
          {currentStep === 1 && (
            <motion.div key="step1" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="w-full max-w-2xl text-center space-y-8">
              <div className="relative inline-block">
                <div className="absolute inset-0 bg-primary blur-3xl opacity-20" />
                <div className="w-24 h-24 border border-primary/30 rounded-3xl flex items-center justify-center bg-slate-950 relative z-10 mx-auto shadow-2xl">
                  <BrainCircuit className="text-primary w-12 h-12" />
                </div>
              </div>
              <div className="space-y-4">
                <h1 className="text-5xl font-black tracking-tighter uppercase">Welcome to <span className="text-primary italic">ELYX</span>.</h1>
                <p className="text-slate-400 text-lg font-medium leading-relaxed max-w-md mx-auto">You are about to initialize your personal AI employee. Let's calibrate your workspace environment.</p>
              </div>
              <div className="grid grid-cols-3 gap-4 text-left">
                <div className="p-4 rounded-2xl bg-slate-900/50 border border-card-border/50">
                  <Shield size={20} className="text-emerald-500 mb-2" />
                  <p className="text-[10px] font-black uppercase text-slate-500 tracking-tighter">Privacy First</p>
                  <p className="text-[11px] font-bold text-slate-200">Local compute & memory.</p>
                </div>
                <div className="p-4 rounded-2xl bg-slate-900/50 border border-card-border/50">
                   <Zap size={20} className="text-primary mb-2" />
                   <p className="text-[10px] font-black uppercase text-slate-500 tracking-tighter">Real-time</p>
                   <p className="text-[11px] font-bold text-slate-200">System synchronization.</p>
                </div>
                <div className="p-4 rounded-2xl bg-slate-900/50 border border-card-border/50">
                   <Settings size={20} className="text-accent mb-2" />
                   <p className="text-[10px] font-black uppercase text-slate-500 tracking-tighter">Enterprise Hub</p>
                   <p className="text-[11px] font-bold text-slate-200">Advanced AI capabilities.</p>
                </div>
              </div>
            </motion.div>
          )}

          {currentStep === 2 && (
            <motion.div key="step2" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} className="w-full max-w-xl space-y-8">
              <div className="flex items-center gap-4">
                 <div className="w-12 h-12 rounded-2xl bg-primary/10 border border-primary/30 flex items-center justify-center">
                   <Cpu className="text-primary" />
                 </div>
                 <div>
                   <h2 className="text-2xl font-black tracking-tight text-white uppercase">Configure AI Core</h2>
                   <p className="text-slate-500 text-sm font-bold">Connecting the Anthropic Claude provider.</p>
                 </div>
              </div>
              <div className="glass-panel p-8 rounded-3xl border-card-border space-y-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest pl-1">Claude API Security Token</label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                    <input type="password" value={anthropicKey} onChange={(e) => setAnthropicKey(e.target.value)} placeholder="sk-ant-api03-..." className="w-full bg-slate-950/50 border border-card-border rounded-2xl py-4 pl-12 pr-4 text-sm font-bold text-white outline-none focus:border-primary/50 transition-all placeholder:text-slate-800" />
                  </div>
                </div>
                <div className="p-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 flex gap-4">
                  <CheckCircle2 className="text-emerald-500 shrink-0" size={18} />
                  <p className="text-xs text-slate-400 leading-relaxed font-medium">ELYX uses <span className="text-emerald-500 font-bold">Claude 3.5 Sonnet</span> as its primary reasoning layer.</p>
                </div>
              </div>
            </motion.div>
          )}

          {currentStep === 3 && (
            <motion.div key="step3" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} className="w-full max-w-2xl space-y-8">
              <div className="flex items-center gap-4">
                 <div className="w-12 h-12 rounded-2xl bg-accent/10 border border-accent/30 flex items-center justify-center">
                   <Globe2 className="text-accent" />
                 </div>
                 <div>
                   <h2 className="text-2xl font-black tracking-tight">Channel Synchronization</h2>
                   <p className="text-slate-500 text-sm font-bold">Where should your AI Employee exert its influence?</p>
                 </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {channels.map((channel) => (
                  <button key={channel.id} onClick={() => toggleChannel(channel.id)} className={`flex items-start gap-4 p-5 rounded-3xl border transition-all text-left group ${selectedChannels.includes(channel.id) ? "bg-primary/5 border-primary/40 shadow-[0_0_20px_rgba(6,182,212,0.1)]" : "bg-slate-900/50 border-card-border hover:border-slate-700 hover:bg-slate-900/80" }`}>
                    <div className={`p-3 rounded-2xl transition-colors ${selectedChannels.includes(channel.id) ? "bg-primary text-slate-950" : "bg-slate-800 text-slate-500 group-hover:text-slate-300" }`}>{channel.icon}</div>
                    <div className="flex-1">
                      <p className={`text-sm font-black mb-1 ${selectedChannels.includes(channel.id) ? "text-white" : "text-slate-300"}`}>{channel.name}</p>
                      <p className="text-[10px] font-bold text-slate-500 line-clamp-1">{channel.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {currentStep === 4 && (
            <motion.div key="step4" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="w-full max-w-xl text-center space-y-8">
                <div className="relative">
                   <motion.div animate={{ rotate: 360 }} transition={{ duration: 10, repeat: Infinity, ease: "linear" }} className="absolute inset-0 border-2 border-dashed border-primary/20 rounded-full" />
                   <div className="w-32 h-32 rounded-full bg-slate-900 border border-primary/40 flex items-center justify-center mx-auto relative z-10">
                      <div className="absolute inset-0 bg-primary/10 rounded-full animate-ping" />
                      <CheckCircle2 className="text-primary" size={48} />
                   </div>
                </div>
                <div className="space-y-4">
                  <h2 className="text-4xl font-black tracking-tight uppercase">Initializing Workspace</h2>
                  <p className="text-slate-400 font-bold max-w-sm mx-auto">All system pathways have been mapped. Preparing your Enterprise workspace.</p>
                </div>
                <div className="p-6 rounded-3xl bg-slate-900/50 border border-card-border flex flex-col gap-4 text-left">
                  <div className="flex items-center justify-between text-[10px] font-black tracking-[0.2em] text-slate-500 uppercase"><span>Status</span><span className="text-emerald-500">99% Complete</span></div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs font-bold text-slate-300"><span className="flex items-center gap-2"><Cpu size={14} className="text-primary"/> AI Core</span><span className="text-emerald-500">Active</span></div>
                    <div className="flex items-center justify-between text-xs font-bold text-slate-300"><span className="flex items-center gap-2"><Database size={14} className="text-indigo-400"/> Local Vault</span><span className="text-indigo-400">Secure</span></div>
                    <div className="flex items-center justify-between text-xs font-bold text-slate-300"><span className="flex items-center gap-2"><Terminal size={14} className="text-accent"/> Logic Engine</span><span className="text-accent">Calibrated</span></div>
                  </div>
                </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="relative z-10 w-full p-8 flex justify-center">
        <div className="w-full max-w-4xl flex items-center justify-between">
           <button onClick={handleBack} disabled={currentStep === 1 || loading} className={`flex items-center gap-2 px-6 py-3 rounded-2xl text-xs font-black tracking-widest uppercase transition-all ${currentStep === 1 ? "opacity-0 pointer-events-none" : "hover:text-primary text-slate-500" }`}>
             <ChevronLeft size={16} /> Terminal Back
           </button>
           <div className="flex items-center gap-4">
             {loading ? (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-center gap-4 text-xs font-black uppercase text-primary tracking-[0.25em] font-outfit"
                >
                  <Loader2 className="animate-spin" size={20} />
                  <span className="flex items-center">Initializing System Workflows<LoadingDots /></span>
                </motion.div>
             ) : (
                <button onClick={handleNext} className="btn-premium-primary !px-10 !py-4 shadow-[0_20px_40px_rgba(6,182,212,0.15)] group">
                  <span className="tracking-[0.25em] text-xs font-black uppercase">{currentStep === 4 ? "ESTABLISH LINK" : "CONTINUE"}</span>
                  <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" />
                </button>
             )}
           </div>
        </div>
      </div>
    </div>
  );
}
