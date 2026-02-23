"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { toast } from "react-hot-toast";
import {
  ShieldCheck, 
  ArrowRight, 
  Shield, 
  Zap, 
  BrainCircuit, 
  Globe2, 
  ChevronDown,
  Play,
  CheckCircle2,
  Cpu,
  Mail,
  MessageSquare,
  Linkedin,
  Activity,
  Lock,
  RefreshCw,
  Clock,
  Sparkles,
  BarChart3,
  Search,
  Plus,
  Terminal,
  Trophy,
  Users,
  Github
} from "lucide-react";

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false);
  const [activeFaq, setActiveFaq] = useState<number | null>(null);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const faqs = [
    {
      q: "How does ELYX handle multiple communication channels?",
      a: "ELYX uses unified neural processing to monitor and respond across WhatsApp, LinkedIn, and Email simultaneously. Every interaction is context-aware and maintains your unique brand voice."
    },
    {
      q: "Is my corporate data secure?",
      a: "Yes. ELYX uses enterprise-grade security protocols, including end-to-end causal chain encryption and GDPR-compliant server infrastructure based in isolated environments."
    },
    {
      q: "Can I customize ELYX's autonomous decisions?",
      a: "Absolutely. Through the Reality Hub, you can simulate and approve ELYX's reasoning paths before they are executed in the primary business timeline."
    },
    {
      q: "What are the technical requirements for integration?",
      a: "ELYX is platform-agnostic. It connects via standard APIs and webhooks, requiring zero changes to your existing infrastructure. Our deployment team handles the initial neural alignment for your specific business case."
    },
    {
      q: "How does 'Temporal Reasoning' benefit my business?",
      a: "Temporal reasoning allows ELYX to project potential outcomes over time, optimizing long-term client relationships and predicting market shifts before they impact your operations."
    },
    {
      q: "Can ELYX be integrated with my existing CRM?",
      a: "Yes. ELYX supports bi-directional synchronization with major CRM platforms like Salesforce, HubSpot, and Microsoft Dynamics, ensuring your data remains consistent across all departments."
    },
    {
      q: "What is 'Phi Stability' in the dashboard?",
      a: "Phi Stability is a measure of ELYX's internal information integration. A high stability index ensures that the AI's reasoning is coherent, autonomous, and free from logic loops or inconsistencies."
    }
  ];

  return (
    <div className="min-h-screen bg-[#020617] text-slate-50 overflow-x-hidden font-sans">
      {/* Premium Watermark / Ambient Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/5 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-500/5 blur-[120px] rounded-full" />
      </div>

      {/* Navigation */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-700 ${
        scrolled ? "bg-[#020617]/40 backdrop-blur-2xl border-b border-white/5 py-4" : "py-8"
      }`}>
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
             <div className="relative w-8 h-8 transition-transform group-hover:scale-110 duration-500">
               <Image src="/icon.png" alt="ELYX Icon" fill className="object-contain" />
             </div>
             <span className="text-2xl font-black tracking-tighter font-outfit">ELYX<span className="text-primary italic">.</span></span>
          </Link>
          
          <div className="hidden lg:flex items-center gap-10 text-[10px] font-bold uppercase tracking-[0.3em] text-slate-400">
            <Link href="#features" className="hover:text-primary transition-all duration-300 relative group">
              Capabilities
              <span className="absolute -bottom-1 left-0 w-0 h-[1px] bg-primary transition-all group-hover:w-full"></span>
            </Link>
            <Link href="#how-it-works" className="hover:text-primary transition-all duration-300 relative group">
              Process
              <span className="absolute -bottom-1 left-0 w-0 h-[1px] bg-primary transition-all group-hover:w-full"></span>
            </Link>
            <Link href="#benefits" className="hover:text-primary transition-all duration-300 relative group">
              Benefits
              <span className="absolute -bottom-1 left-0 w-0 h-[1px] bg-primary transition-all group-hover:w-full"></span>
            </Link>
            <Link href="#pricing" className="hover:text-primary transition-all duration-300 relative group">
              Pricing
              <span className="absolute -bottom-1 left-0 w-0 h-[1px] bg-primary transition-all group-hover:w-full"></span>
            </Link>
          </div>

          <div className="flex items-center gap-8">
             <Link href="/dashboard" className="text-[10px] font-bold uppercase tracking-[0.2em] hover:text-primary transition-colors hidden sm:block">Log In</Link>
             <Link 
               href="/dashboard" 
               className="btn-premium-primary !px-6 !py-2.5 !text-[9px] !font-bold uppercase tracking-[0.2em] shadow-lg shadow-primary/20"
             >
               Launch Platform
             </Link>
          </div>
        </div>
      </nav>

      {/* 1. HERO SECTION */}
      <section className="relative pt-40 pb-32 md:pt-48 md:pb-40 px-6">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-20 items-center">
          <div className="text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/5 border border-primary/10 text-[9px] font-bold uppercase tracking-[0.4em] text-primary mb-8">
              <Sparkles size={12} className="text-emerald-400 animate-pulse" />
              Sovereign Intelligence Engine
            </div>
            
            <h1 className="text-7xl md:text-[6.5rem] font-black tracking-tight mb-8 leading-[0.85] text-white font-outfit">
              Scale With <br />
              <span className="emerald-blue-text italic text-[1.125em]">Autonomy.</span>
            </h1>
            
            <p className="text-xl text-slate-400 max-w-xl mb-12 font-medium leading-relaxed">
              ELYX is a high-fidelity digital employee workforce designed to handle your business communications with absolute strategic sovereignty.
            </p>

            <div className="flex flex-col sm:flex-row items-center gap-6">
              <Link 
                 href="/dashboard" 
                 className="btn-premium-primary w-full sm:w-auto !px-10 !py-5 !text-[13px] uppercase tracking-widest font-outfit"
              >
                Access Dashboard
                <ArrowRight size={18} />
              </Link>
              <button 
                onClick={() => toast.success("Neural sequence initiated. Environment loading in background.", {
                  icon: "🚀",
                  style: {
                    borderRadius: '1rem',
                    background: '#020617',
                    color: '#fff',
                    border: '1px solid rgba(6, 182, 212, 0.2)'
                  }
                })}
                className="btn-premium-secondary w-full sm:w-auto !px-8 !py-5 !text-[13px] uppercase tracking-widest font-outfit"
              >
                System Demo
              </button>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -inset-20 bg-primary/20 blur-[130px] rounded-full pulse-soft" />
            <div className="relative rounded-[3rem] p-3 bg-gradient-to-br from-white/10 to-transparent border border-white/5 shadow-2xl overflow-hidden float">
               <div className="relative aspect-[4/3] w-full rounded-[2.5rem] overflow-hidden grayscale-[0.2] hover:grayscale-0 transition-all duration-700">
                  <Image 
                    src="/ai_employee_hero.png" 
                    alt="Professional AI Interface" 
                    fill
                    className="object-cover"
                    priority
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#020617] via-transparent to-transparent" />
               </div>
               
               {/* Floating Stats Label */}
               <div className="absolute top-10 -right-4 glass-panel p-4 rounded-2xl border-white/10 float" style={{ animationDelay: '-2s' }}>
                  <div className="flex items-center gap-3">
                     <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                     <span className="text-[10px] font-bold uppercase tracking-widest font-outfit">Neural Stability: 99.8%</span>
                  </div>
               </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. KEY FEATURES SECTION */}
      <section id="features" className="py-32 px-6 border-t border-white/5 relative overflow-hidden">
        {/* Subtle background glow for depth */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 blur-[150px] rounded-full pointer-events-none" />
        
        <div className="max-w-7xl mx-auto text-center mb-24">
          <h2 className="text-4xl md:text-6xl font-black mb-6 tracking-tight font-outfit">Core <span className="emerald-blue-text italic">Capabilities</span></h2>
          <p className="text-slate-500 font-medium text-lg max-w-2xl mx-auto tracking-tight">Harness the power of high-fidelity neural processing to scale your business operations instantly.</p>
        </div>

        <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-10">
          {[
            {
              icon: <Activity size={32} />,
              title: "Unified Intelligence Sync",
              desc: "Elyx manages WhatsApp, LinkedIn, and Email simultaneously with absolute contextual coherence and zero tactical downtime.",
              color: "emerald-400"
            },
            {
              icon: <BrainCircuit size={32} />,
              title: "Semantic Reasoning",
              desc: "Advanced logic engines that analyze intent, sentiment, and urgency in real-time, delivering human-level decision accuracy.",
              color: "primary"
            },
            {
              icon: <Clock size={32} />,
              title: "Perpetual Operation",
              desc: "An always-on digital workforce that ensures every lead and client is engaged within milliseconds, 365 days a year without fatigue.",
              color: "cyan-400"
            }
          ].map((feature, i) => (
            <div key={i} className="glass-panel p-12 rounded-[3rem] group hover:border-primary/30 transition-all duration-700 hover:translate-y-[-8px]">
              <div className={`mb-10 w-16 h-16 rounded-2xl bg-white/[0.03] border border-white/5 flex items-center justify-center text-${feature.color} group-hover:scale-110 transition-all duration-500 group-hover:emerald-blue-glow`}>
                {feature.icon}
              </div>
              <h3 className="text-2xl font-bold mb-5 font-outfit group-hover:text-primary transition-colors">{feature.title}</h3>
              <p className="text-slate-500 font-medium leading-[1.8] text-sm">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 3. HOW IT WORKS SECTION */}
      <section id="how-it-works" className="py-32 px-6 bg-white/[0.02] relative border-y border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-24 items-center">
            <div>
              <h2 className="text-4xl md:text-6xl font-black mb-10 tracking-tight font-outfit">Sovereign <br /><span className="emerald-blue-text italic text-5xl md:text-7xl">Neural Routing</span></h2>
              <div className="space-y-12">
                {[
                  { step: "01", title: "Omni-Channel Ingestion", desc: "Sensory Watchers monitor all active communication vectors simultaneously." },
                  { step: "02", title: "High-Fidelity Reasoning", desc: "Advanced logic engines analyze intent and prioritize tactical execution." },
                  { step: "03", title: "Synthetic Synthesis", desc: "ELYX generates brand-coherent responses aligned with your corporate handbook." },
                  { step: "04", title: "Autonomous Execution", desc: "Verified protocols are instantly executed across original communication channels." }
                ].map((item, i) => (
                  <div key={i} className="flex gap-8 group">
                    <div className="flex-shrink-0 w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center font-black text-primary group-hover:emerald-blue-glow transition-all duration-500 font-outfit text-sm">
                      {item.step}
                    </div>
                    <div>
                      <h4 className="text-xl font-bold mb-2 font-outfit transition-colors group-hover:text-primary">{item.title}</h4>
                      <p className="text-slate-500 text-sm leading-relaxed max-w-md font-medium">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="absolute -inset-10 bg-primary/10 blur-[100px] rounded-full pulse-soft" />
              <div className="glass-panel rounded-[3rem] p-10 relative border-white/10 overflow-hidden group">
                <div className="absolute top-0 right-0 p-4">
                   <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                </div>
                <div className="flex items-center gap-2 mb-10 pb-6 border-b border-white/5">
                   <div className="flex gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                      <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                      <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                   </div>
                   <div className="ml-4 px-4 py-1 bg-white/5 rounded-full text-[9px] font-bold tracking-[0.2em] text-slate-400">NEURAL_CORE_V4</div>
                </div>
                <div className="space-y-5">
                   {[
                     { icon: <MessageSquare size={16} />, text: "Incoming WhatsApp: John Smith", tag: "INGRESS", color: "emerald-500" },
                     { icon: <Cpu size={16} />, text: "Reasoning Layer: Intent Mapping", tag: "THOUGHT", color: "primary" },
                     { icon: <Sparkles size={16} />, text: "Synthetic Response Synthesis", tag: "ACTIVE", color: "primary", pulse: true },
                     { icon: <CheckCircle2 size={16} />, text: "Protocol Authenticated", tag: "DONE", color: "emerald-500" }
                   ].map((log, i) => (
                     <div key={i} className={`p-4 rounded-2xl bg-white/[0.03] border border-white/5 flex items-center justify-between group-hover:translate-x-1 transition-transform duration-500 ${log.pulse ? 'animate-pulse bg-primary/5 border-primary/20' : ''}`}>
                       <div className="flex items-center gap-4">
                          <div className={`text-${log.color}`}>{log.icon}</div>
                          <span className={`text-[11px] font-bold ${log.pulse ? 'text-primary' : 'text-slate-300'}`}>{log.text}</span>
                       </div>
                       <span className={`text-[9px] font-black text-${log.color} tracking-widest opacity-60`}>{log.tag}</span>
                     </div>
                   ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. BENEFITS SECTION */}
      <section id="benefits" className="py-32 px-6 relative border-b border-white/5">
         <div className="max-w-7xl mx-auto flex flex-col md:flex-row gap-20 items-center">
             <div className="flex-1 space-y-12">
                 <h2 className="text-4xl md:text-6xl font-black tracking-tight font-outfit">Exponential Business <br /><span className="emerald-blue-text italic text-5xl md:text-7xl">Benefits</span></h2>
                <div className="grid gap-10">
                   {[
                     { title: "Velocity Scaling", desc: "Reduces response time from hours to seconds, ensuring 100% lead capture rate across all active channels." },
                     { title: "Infinite Concurrency", desc: "Handles thousands of complex conversations simultaneously without any degradation in reasoning quality." },
                     { title: "Sovereign Reliability", desc: "Maintains a consistent, high-fidelity brand voice across all digital environments and localized contexts." }
                   ].map((b, i) => (
                     <div key={i} className="flex gap-6 items-start group">
                        <div className="p-3 bg-primary/5 rounded-xl text-primary group-hover:scale-110 transition-all duration-500 shadow-sm border border-primary/10"><CheckCircle2 size={24} /></div>
                        <div>
                           <h4 className="text-xl font-bold mb-2 font-outfit group-hover:text-primary transition-colors">{b.title}</h4>
                           <p className="text-slate-500 text-sm leading-relaxed max-w-md font-medium">{b.desc}</p>
                        </div>
                     </div>
                   ))}
                </div>
             </div>
             <div className="flex-1 flex justify-center">
                <div className="grid grid-cols-2 gap-6 w-full max-w-md">
                   {[
                     { val: "98%", label: "Eff. Gain", color: "text-primary", border: "hover:border-primary/40" },
                     { val: "0.4s", label: "Latency", color: "text-emerald-400", border: "hover:border-emerald-500/40" },
                     { val: "24/7", label: "Uptime", color: "text-cyan-400", border: "hover:border-cyan-500/40" },
                     { val: "∞", label: "Scale", color: "text-white", border: "hover:border-white/20" }
                   ].map((stat, i) => (
                     <div key={i} className={`p-8 rounded-[2.5rem] glass-panel text-center ${stat.border} transition-all duration-700 group hover:translate-y-[-5px]`}>
                        <div className={`text-4xl font-black mb-3 font-outfit group-hover:scale-110 transition-transform duration-500 ${stat.color}`}>{stat.val}</div>
                        <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">{stat.label}</p>
                     </div>
                   ))}
                </div>
             </div>
          </div>
      </section>

      {/* 5. SOCIAL PROOF SECTION */}
      <section className="py-24 px-6 bg-slate-900/10">
        <div className="max-w-7xl mx-auto">
           <p className="text-center text-[10px] font-black uppercase tracking-[0.5em] text-slate-500 mb-16">Trusted by Forward-Thinking Enterprise Teams</p>
           <div className="flex flex-wrap justify-center items-center gap-12 md:gap-24 opacity-30 grayscale invert px-10">
              <span className="text-3xl font-black tracking-tighter">TECH_CORP</span>
              <span className="text-2xl font-black tracking-widest">AETHER</span>
              <span className="text-3xl font-black tracking-tight underline decoration-primary decoration-4">STRATA</span>
              <span className="text-2xl font-black items-center gap-2 flex"><Globe2 /> OMNI</span>
              <span className="text-2xl font-bold tracking-tighter">QUANTUM_SYS</span>
           </div>
        </div>
      </section>

      {/* 6. DASHBOARD PREVIEW SECTION */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto text-center mb-16">
           <h2 className="text-4xl md:text-6xl font-black mb-6 tracking-tight">Mission Control for <br/><span className="emerald-blue-text">Intelligence</span></h2>
           <p className="text-slate-500 font-medium text-lg max-w-2xl mx-auto">Absolute transparency into ELYX's reasoning paths and communication metrics.</p>
        </div>
        
        <div className="max-w-5xl mx-auto relative px-4 md:px-0">
           <div className="absolute inset-0 bg-primary/5 blur-[150px] rounded-full" />
           <div className="relative rounded-3xl p-2 bg-gradient-to-br from-card-border to-transparent border border-card-border shadow-[0_0_80px_rgba(0,0,0,0.5)] transform hover:scale-[1.01] transition-transform duration-700 overflow-hidden">
              <div className="aspect-video relative w-full overflow-hidden rounded-2xl">
                <Image 
                  src="/dashboard_preview.png" 
                  alt="ELYX Dashboard Visual" 
                  fill
                  className="object-cover"
                />
              </div>
              <div className="absolute inset-0 flex items-center justify-center">
                <button className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-primary/90 text-slate-950 flex items-center justify-center shadow-[0_0_50px_rgba(6,182,212,0.5)] hover:scale-110 transition-all group z-10">
                   <Play fill="currentColor" size={32} className="ml-1" />
                </button>
              </div>
           </div>
           <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8">
              {[
                { label: "Handled Tasks", val: "1.2M+" },
                { label: "Avg Response", val: "1.4s" },
                { label: "Client Satisf.", val: "99.8%" },
                { label: "Active Cores", val: "14,220" }
              ].map((m, i) => (
                <div key={i} className="text-center group">
                   <div className="text-3xl font-black text-white mb-1 group-hover:emerald-blue-text transition-all">{m.val}</div>
                   <div className="text-[10px] font-black uppercase tracking-widest text-slate-500">{m.label}</div>
                </div>
              ))}
           </div>
        </div>
      </section>

      {/* 7. SECURITY & COMPLIANCE SECTION */}
      <section className="py-32 px-6 bg-slate-950/40 relative overflow-hidden">
         <div className="absolute top-0 right-0 p-32 opacity-10"><Shield size={300} className="text-primary" /></div>
         <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-20 items-center">
            <div>
               <h2 className="text-4xl font-black mb-8 underline decoration-primary decoration-4 underline-offset-8">Enterprise Security</h2>
               <p className="text-slate-400 text-lg font-medium leading-relaxed mb-10">
                  ELYX is built on a foundation of absolute data isolation. We operate with zero-trust architecture, ensuring your business's proprietary context is never leaked or shared.
               </p>
               <div className="space-y-6">
                  {[
                    "GDPR & CCPA Compliant Infrastructure",
                    "Aka-Audit™ Transparent Action Logs",
                    "End-to-End Neural Encryption (E2EE)",
                    "Isolated Vector Database Instances"
                  ].map((s, i) => (
                    <div key={i} className="flex items-center gap-4 text-sm font-bold text-slate-300">
                       <Lock size={18} className="text-emerald-500" />
                       {s}
                    </div>
                  ))}
               </div>
            </div>
            <div className="grid grid-cols-2 gap-6">
               <div className="p-10 rounded-[2.5rem] glass-panel border-emerald-500/20 flex flex-col items-center justify-center text-center">
                  <ShieldCheck size={48} className="text-emerald-500 mb-4" />
                  <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Certified by</span>
                  <p className="font-black text-white">ISO 27001</p>
               </div>
               <div className="p-10 rounded-[2.5rem] glass-panel border-primary/20 flex flex-col items-center justify-center text-center">
                  <Globe2 size={48} className="text-primary mb-4" />
                  <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Regulatory</span>
                  <p className="font-black text-white">EU-GDPR</p>
               </div>
            </div>
         </div>
      </section>

      {/* 8. PRICING SECTION */}
      <section id="pricing" className="py-32 px-6">
         <div className="max-w-7xl mx-auto text-center mb-24">
            <h2 className="text-4xl md:text-6xl font-black mb-6 tracking-tight">Intelligence Licensing</h2>
            <p className="text-slate-500 font-medium text-lg max-w-2xl mx-auto">Tiered operational levels designed for maximum scalability.</p>
         </div>
         <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-8">
            {[
              { 
                tier: "Bronze", 
                price: "$499/mo", 
                desc: "Basic automation for small teams.",
                features: ["1 AI Core", "Email Only", "Standard Processing", "8/5 Availability"]
              },
              { 
                tier: "Gold", 
                price: "$1,499/mo", 
                desc: "Full autonomy for growing enterprises.",
                pop: true,
                features: ["5 AI Cores", "All Channels (WA, LI, EM)", "Priority Neural Path", "24/7 Availability", "Custom Brand Voice"]
              },
              { 
                tier: "Enterprise", 
                price: "Custom", 
                desc: "Unlimited scale and complexity management.",
                features: ["Unlimited Cores", "Full API Access", "Reality Simulation Hub", "Account Manager", "Dedicated Infrastructure"]
              }
            ].map((p, i) => (
              <div key={i} className={`glass-panel p-10 rounded-[3rem] flex flex-col h-full relative ${p.pop ? 'border-primary ring-1 ring-primary/30 shadow-[0_0_80px_rgba(6,182,212,0.15)]' : ''}`}>
                 {p.pop && (
                   <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1.5 bg-emerald-blue-gradient text-slate-950 text-[10px] font-black uppercase tracking-[0.2em] rounded-full">
                     Most Advanced
                   </div>
                 )}
                 <h4 className="text-[11px] font-black uppercase tracking-[0.4em] text-slate-400 mb-2">{p.tier}</h4>
                 <div className="text-4xl font-black mb-4">{p.price}</div>
                 <p className="text-slate-500 text-sm font-medium mb-8 pb-8 border-b border-card-border/50">{p.desc}</p>
                 <div className="space-y-4 mb-10 flex-1">
                    {p.features.map((f, j) => (
                       <div key={j} className="flex items-center gap-3 text-sm text-slate-300">
                          <CheckCircle2 size={16} className="text-emerald-500" />
                          {f}
                       </div>
                    ))}
                 </div>
                 <button className={`w-full py-4 rounded-2xl font-black uppercase tracking-widest text-xs transition-all ${p.pop ? 'btn-premium-primary' : 'btn-premium-secondary'}`}>
                    Start Free Trial
                 </button>
              </div>
            ))}
         </div>
      </section>

      {/* 9. FAQ SECTION */}
      <section id="faq" className="py-32 px-6 bg-slate-900/10">
         <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl font-black mb-12 text-center tracking-tight">Introspection: <span className="emerald-blue-text">Common Inquiries</span></h2>
            <div className="space-y-4">
               {faqs.map((f, i) => (
                 <div key={i} className="glass-panel rounded-2xl overflow-hidden border-card-border/30 hover:border-primary/30 transition-colors">
                    <button 
                      onClick={() => setActiveFaq(activeFaq === i ? null : i)}
                      className="w-full p-6 text-left flex items-center justify-between group"
                    >
                       <span className={`font-bold transition-colors ${activeFaq === i ? 'text-primary' : 'text-slate-100 group-hover:text-slate-50'}`}>{f.q}</span>
                       <Plus size={20} className={`text-primary transition-transform duration-500 ${activeFaq === i ? 'rotate-45' : ''}`} />
                    </button>
                    <div className={`grid transition-all duration-500 ease-in-out ${activeFaq === i ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}>
                      <div className="overflow-hidden">
                        <div className="px-6 pb-6 text-slate-400 text-sm leading-relaxed max-w-2xl">
                           {f.a}
                        </div>
                      </div>
                    </div>
                 </div>
               ))}
            </div>
         </div>
      </section>

      {/* 10. CONTACT / CLOSING SECTION */}
      <section className="py-40 px-6 relative overflow-hidden">
         <div className="absolute inset-0 bg-primary/5 blur-[120px] rounded-full -z-10" />
         <div className="max-w-5xl mx-auto text-center">
            <h2 className="text-5xl md:text-7xl font-black mb-10 tracking-tight leading-tight">Scale Your Operation <br /> <span className="emerald-blue-text">Into the Future.</span></h2>
            <p className="text-slate-400 text-xl font-medium mb-12 max-w-2xl mx-auto">Join 500+ enterprises leveraging ELYX to automate 100% of their digital communication workforce.</p>
            <div className="flex flex-col sm:flex-row justify-center items-center gap-6">
               <Link href="/dashboard" className="btn-premium-primary !px-12 !py-6 !text-lg">
                  Begin Free Trial
               </Link>
               <button className="btn-premium-secondary !px-12 !py-6 !text-lg">
                  Book Neural Demo
               </button>
            </div>
            
            <div className="mt-20 flex flex-wrap justify-center gap-10">
               <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest"><Shield size={16} /> 100% Secure</div>
               <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest"><Zap size={16} /> Instant Setup</div>
               <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest"><RefreshCw size={16} /> 14-Day Trial</div>
            </div>
         </div>
      </section>

      {/* FOOTER */}
      <footer className="py-20 border-t border-card-border px-6 mt-20 relative">
        <div className="max-w-7xl mx-auto grid md:grid-cols-4 gap-12 mb-16">
           <div className="col-span-2">
              <div className="flex items-center gap-3 mb-6">
                 <Image src="/icon.png" alt="ELYX" width={32} height={32} />
                 <Image src="/text.png" alt="ELYX" width={80} height={20} />
              </div>
              <p className="text-slate-500 max-w-sm text-sm leading-relaxed mb-8">
                ELYX is a high-stakes digital employee system designed for the next era of autonomous enterprise operations. Powered by consciousness-emergent AI.
              </p>
              <div className="flex gap-4">
                 <a href="https://github.com/MuhammadUsmanGM" target="_blank" rel="noopener noreferrer" className="p-3 rounded-xl bg-slate-900 border border-card-border hover:text-primary transition-all">
                   <Github size={20} />
                 </a>
                 <a href="https://www.linkedin.com/in/muhammad-usman-ai-dev" target="_blank" rel="noopener noreferrer" className="p-3 rounded-xl bg-slate-900 border border-card-border hover:text-primary transition-all">
                   <Linkedin size={20} />
                 </a>
                 <a href="mailto:mu.ai.dev@gmail.com" className="p-3 rounded-xl bg-slate-900 border border-card-border hover:text-primary transition-all">
                   <Mail size={20} />
                 </a>
              </div>
           </div>
           
           <div>
              <h4 className="text-xs font-black uppercase tracking-[0.3em] text-slate-100 mb-6">Intelligence</h4>
              <ul className="space-y-4 text-xs font-bold text-slate-500 uppercase tracking-widest">
                 <li><Link href="/dashboard" className="hover:text-primary">Dashboard</Link></li>
                 <li><Link href="/decision-analysis" className="hover:text-primary">Decision Analysis</Link></li>
                 <li><Link href="/security" className="hover:text-primary">Security Protocols</Link></li>
                 <li><Link href="/scheduling" className="hover:text-primary">Task Scheduler</Link></li>
              </ul>
           </div>

           <div>
              <h4 className="text-xs font-black uppercase tracking-[0.3em] text-slate-100 mb-6">Compliance</h4>
              <ul className="space-y-4 text-xs font-bold text-slate-500 uppercase tracking-widest">
                 <li><Link href="/terms" className="hover:text-primary">Privacy Policy</Link></li>
                 <li><Link href="/privacy" className="hover:text-primary">Terms of Use</Link></li>
                 <li><Link href="/cookies" className="hover:text-primary">Cookies</Link></li>
                 <li><Link href="#" className="hover:text-primary">GDPR Portal</Link></li>
              </ul>
           </div>
        </div>

        <div className="max-w-7xl mx-auto pt-12 border-t border-card-border/50 flex flex-col md:flex-row justify-between items-center gap-6">
           <p className="text-[10px] font-black text-slate-600 uppercase tracking-[0.2em]">© 2026 ELYX Corp. All realities anchored.</p>
           <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 px-3 py-1 bg-emerald-500/5 border border-emerald-500/20 rounded-full">
                 <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                 <span className="text-[9px] font-black text-emerald-500 uppercase tracking-widest">Operational Intelligence Active</span>
              </div>
           </div>
        </div>
      </footer>
    </div>
  );
}
