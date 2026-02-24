"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BrainCircuit,
  Clock,
  Globe2,
  Briefcase,
  ShieldCheck,
  MessageSquare,
  CheckCircle2,
  Bell,
  Search,
  Settings,
  MoreVertical,
  Activity,
  Loader2,
  BarChart3,
  Terminal,
  ArrowRight,
  HelpCircle,
  Users,
  LogOut,
  ChevronRight,
  Sparkles,
  Calendar
} from "lucide-react";
import { useState, useEffect } from "react";
import { DashboardData } from "@/lib/types";
import { fetchDashboardData, fetchOnboardingStatus } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import { User } from "@supabase/supabase-js";
import { useRouter } from "next/navigation";
import { toast } from "react-hot-toast";
import { motion, AnimatePresence } from "framer-motion";

export default function SidebarLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [data, setData] = useState<DashboardData | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isSidebarHovered, setIsSidebarHovered] = useState(false);
  const router = useRouter();

  const sidebarItems = [
    { icon: <LayoutDashboard size={18} />, label: "Mission Control", href: "/dashboard" },
    { icon: <BarChart3 size={18} />, label: "Decision Matrix", href: "/analytics" },
    { icon: <Users size={18} />, label: "Team Directory", href: "/users" },
    { icon: <Briefcase size={18} />, label: "Business Operations", href: "/business" },
    { icon: <MessageSquare size={18} />, label: "Global Comms", href: "/comms" },
    { icon: <Activity size={18} />, label: "System Monitor", href: "/system-monitor" },
    { icon: <Calendar size={18} />, label: "Task Scheduler", href: "/scheduling" },
    { icon: <ShieldCheck size={18} />, label: "Vault Security", href: "/security" },
    { icon: <Settings size={18} />, label: "OS Settings", href: "/settings" },
  ];

  useEffect(() => {
    const checkUserAndOnboarding = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session && pathname !== "/auth") {
        router.push("/auth");
        return;
      }
      
      setUser(session?.user ?? null);

      if (session?.user && pathname !== "/onboard" && pathname !== "/auth") {
        const onboarded = await fetchOnboardingStatus(session.user.id);
        if (!onboarded) {
          router.push("/onboard");
        }
      }
    };
    
    checkUserAndOnboarding();

    const loadData = async () => {
      try {
        const dashData = await fetchDashboardData();
        setData(dashData);
      } catch (error) {
        console.error("Layout data fetch error:", error);
      }
    };
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [pathname, router]);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    toast.success("System Session Terminated. Returning to Login.");
    router.push("/auth");
  };

  return (
    <div className="flex min-h-screen bg-[#020617] text-slate-200 selection:bg-primary/30 relative overflow-hidden">
      {/* Premium Texture Overlay */}
      <div className="noise-overlay" />
      
      {/* Dynamic Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] right-[-5%] w-[40%] h-[40%] bg-primary/5 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] left-[-5%] w-[30%] h-[30%] bg-accent/5 blur-[100px] rounded-full" />
      </div>

      {/* Sidebar */}
      <aside 
        onMouseEnter={() => setIsSidebarHovered(true)}
        onMouseLeave={() => setIsSidebarHovered(false)}
        className="w-72 border-r border-white/5 bg-[#020617]/40 backdrop-blur-2xl flex flex-col fixed h-full z-30 transition-all duration-500"
      >
        <div className="p-8 pb-4">
          <Link href="/dashboard" className="flex items-center gap-4 group cursor-pointer">
            <motion.div 
              whileHover={{ rotate: 180, scale: 1.1 }}
              transition={{ duration: 0.8, type: "spring" }}
              className="relative w-11 h-11 bg-gradient-to-br from-primary/20 via-transparent to-accent/20 rounded-2xl border border-white/10 flex items-center justify-center shadow-2xl shadow-primary/10 overflow-hidden"
            >
              <div className="absolute inset-0 bg-primary/10 animate-pulse" />
              <Image src="/icon.png" alt="ELYX Icon" width={28} height={28} className="object-contain relative z-10" />
            </motion.div>
            <div className="flex flex-col">
              <span className="text-xl font-black tracking-tighter text-white group-hover:text-primary transition-colors">ELYX</span>
              <span className="text-[8px] font-black tracking-[0.3em] text-slate-500 uppercase">System Workspace v2.0</span>
            </div>
          </Link>
        </div>

        <nav className="flex-1 px-4 py-8 space-y-1.5 overflow-y-auto scrollbar-hide custom-scrollbar">
          {sidebarItems.map((item, i) => {
            const active = pathname === item.href;
            return (
              <Link
                key={i}
                href={item.href}
                className={`group relative w-full flex items-center gap-4 px-5 py-3.5 rounded-2xl transition-all duration-300 cursor-pointer overflow-hidden ${
                  active 
                    ? "bg-gradient-to-r from-primary/10 to-transparent text-primary" 
                    : "text-slate-400 hover:text-slate-100"
                }`}
              >
                {active && (
                  <motion.div 
                    layoutId="sidebar-active"
                    className="absolute inset-0 bg-primary/5 border-l-2 border-primary z-0"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <span className={`relative z-10 p-0.5 transition-all duration-300 ${active ? "text-primary scale-110 drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]" : "text-slate-500 group-hover:text-primary group-hover:scale-110"}`}>
                  {item.icon}
                </span>
                <span className={`relative z-10 font-bold text-xs uppercase tracking-widest transition-all duration-300 ${active ? "opacity-100" : "opacity-70 group-hover:opacity-100"}`}>
                  {item.label}
                </span>
                
                {active && (
                  <motion.div 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="ml-auto relative z-10"
                  >
                    <ChevronRight size={14} className="text-primary/40" />
                  </motion.div>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="p-6 border-t border-white/5 space-y-4 bg-gradient-to-t from-black/20 to-transparent">
          {/* API Hub Button */}
          <Link 
            href="/api-docs" 
            className="group relative flex items-center gap-4 px-5 py-4 bg-white/[0.02] border border-white/5 hover:border-primary/40 transition-all rounded-[1.25rem] overflow-hidden shadow-xl"
          >
            <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="w-8 h-8 rounded-xl bg-slate-900 flex items-center justify-center text-slate-500 group-hover:text-primary transition-colors border border-white/5">
              <Terminal size={14} />
            </div>
            <div className="flex flex-col">
              <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Developer</span>
               <span className="text-[11px] font-bold text-slate-300 group-hover:text-white transition-colors">System Interface</span>
            </div>
          </Link>

          {/* System Integrity Widget */}
          <div className="glass-panel rounded-[1.25rem] p-5 bg-accent/5 border border-accent/10 relative overflow-hidden group">
            <div className="absolute -top-4 -right-4 p-4 opacity-[0.05] group-hover:scale-110 transition-transform duration-1000">
              <Sparkles size={40} className="text-accent" />
            </div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className={`w-1.5 h-1.5 rounded-full ${data?.health.status === 'healthy' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)] animate-pulse'}`} />
                <span className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em]">Core Stability</span>
              </div>
              <span className="text-[10px] font-black text-accent">{data?.system.stability_score.toFixed(1) || "98.4"}%</span>
            </div>
            <div className="h-1 w-full bg-slate-900 rounded-full overflow-hidden border border-white/5">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${data?.system.stability_score || 98.4}%` }}
                className="h-full bg-gradient-to-r from-accent/40 to-accent"
              />
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 ml-72 flex flex-col min-h-screen relative z-10">
        {/* Futuristic Header */}
        <header className="h-24 px-10 border-b border-white/5 bg-[#020617]/60 backdrop-blur-2xl sticky top-0 z-20 flex items-center justify-between gap-8">
          <div className="flex-1 max-w-2xl relative group">
            <div className="absolute inset-0 bg-primary/5 blur-xl group-focus-within:bg-primary/10 transition-all opacity-0 group-focus-within:opacity-100" />
            <div className="relative flex items-center gap-4 bg-white/[0.03] border border-white/10 rounded-2xl px-6 py-3.5 group-focus-within:border-primary/40 transition-all">
              <Search size={18} className="text-slate-500 group-focus-within:text-primary transition-colors" />
              <input 
                type="text" 
                placeholder="Query system database..." 
                className="bg-transparent border-none outline-none text-[13px] text-slate-300 w-full font-bold placeholder:text-slate-600 tracking-wide"
              />
              <div className="hidden sm:flex items-center gap-1.5 px-2 py-1 bg-slate-900 border border-white/5 rounded-lg">
                <span className="text-[9px] font-black text-slate-500 tracking-[0.2em]">CMD + K</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-8">
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="relative w-12 h-12 flex items-center justify-center rounded-2xl bg-white/[0.03] border border-white/10 text-slate-400 hover:text-primary hover:border-primary/30 transition-all shadow-xl"
            >
              <Bell size={20} />
              {data && data.tasks.pending_count > 0 && (
                <span className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-primary text-black rounded-lg text-[10px] font-black flex items-center justify-center border-2 border-[#020617] shadow-lg">
                  {data.tasks.pending_count}
                </span>
              )}
            </motion.button>

            <div className="h-10 w-px bg-white/10 mx-2" />

            <div className="flex items-center gap-5">
              <div className="text-right hidden xl:block">
                <p className="text-xs font-black text-slate-200 capitalize tracking-tight leading-none mb-1">
                  {user?.email?.split('@')[0].replace('.', ' ') || "System Admin"}
                </p>
                <div className="flex items-center justify-end gap-1.5">
                  <div className="w-1 h-1 rounded-full bg-primary" />
                  <p className="text-[9px] font-black text-primary uppercase tracking-[0.2em]">Authorized</p>
                </div>
              </div>
              
              <div className="relative group p-1 bg-gradient-to-br from-primary/20 via-transparent to-accent/20 rounded-2xl border border-white/10 transition-all hover:scale-105">
                <button 
                  onClick={() => {
                    const dropdown = document.getElementById('user-dropdown');
                    dropdown?.classList.toggle('hidden');
                  }}
                  className="w-11 h-11 rounded-xl overflow-hidden bg-slate-900 border border-white/5 relative z-10"
                >
                  <img src={`https://api.dicebear.com/7.x/bottts-neutral/svg?seed=${user?.email || 'default'}&backgroundColor=020617`} alt="Avatar" className="w-full h-full object-cover" />
                </button>
                
                <div id="user-dropdown" className="hidden absolute top-full right-0 mt-4 w-60 bg-[#020617] border border-white/10 rounded-2xl shadow-2xl p-3 backdrop-blur-2xl z-50">
                  <div className="p-4 border-b border-white/5 mb-2">
                    <p className="text-xs font-black text-white truncate mb-0.5">{user?.email}</p>
                    <p className="text-[10px] font-bold text-slate-500">System Integrity: Optimal</p>
                  </div>
                  <Link href="/settings" className="flex items-center gap-3 px-4 py-3 text-[11px] font-bold text-slate-400 hover:text-white hover:bg-white/5 rounded-xl transition-all">
                    <Settings size={14} /> Workspace Settings
                  </Link>
                  <button 
                    onClick={handleSignOut}
                    className="w-full flex items-center gap-3 px-4 py-3 text-[11px] font-bold text-red-500/80 hover:text-red-400 hover:bg-red-500/5 rounded-xl transition-all border-t border-white/5 mt-2 pt-4"
                  >
                    <LogOut size={14} /> Sign Out Session
                  </button>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Dynamic Content Viewport */}
        <main className="flex-1 p-10 relative overflow-x-hidden">
          <div className="h-full relative z-10">
            {children}
          </div>
        </main>

        {/* Status Bar */}
        <footer className="h-10 px-10 border-t border-white/5 bg-black/40 flex items-center justify-between backdrop-blur-md">
           <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                 <div className="w-1 h-1 rounded-full bg-primary animate-ping" />
                 <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">System Link: Active</span>
              </div>
              <div className="h-3 w-px bg-white/10" />
              <div className="flex items-center gap-2">
                 <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Entropy Level:</span>
                 <span className="text-[9px] font-black text-emerald-500 uppercase tracking-widest">Low</span>
              </div>
           </div>
           <div className="text-[9px] font-black text-slate-600 uppercase tracking-widest">
              ELYX System Core © 2024 • Enterprise Secure
           </div>
        </footer>
      </div>
    </div>
  );
}
