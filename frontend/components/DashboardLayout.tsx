"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  BrainCircuit, 
  Clock, 
  Globe2, 
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
  LogOut
} from "lucide-react";
import { useState, useEffect } from "react";
import { DashboardData } from "@/lib/types";
import { fetchDashboardData, fetchOnboardingStatus } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import { User } from "@supabase/supabase-js";
import { useRouter } from "next/navigation";
import { toast } from "react-hot-toast";

export default function SidebarLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [data, setData] = useState<DashboardData | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();

  const sidebarItems = [
    { icon: <LayoutDashboard size={20} />, label: "Dashboard", href: "/dashboard" },
    { icon: <BarChart3 size={20} />, label: "Analytics", href: "/analytics" },
    { icon: <Users size={20} />, label: "Team", href: "/users" },
    { icon: <CheckCircle2 size={20} />, label: "Operations", href: "/operations" },
    { icon: <Activity size={20} />, label: "Business", href: "/business" },
    { icon: <MessageSquare size={20} />, label: "Communications", href: "/comms" },
    { icon: <BrainCircuit size={20} />, label: "Consciousness", href: "/consciousness" },
    { icon: <Clock size={20} />, label: "Temporal", href: "/temporal" },
    { icon: <Globe2 size={20} />, label: "Reality", href: "/reality" },
    { icon: <ShieldCheck size={20} />, label: "Security", href: "/security" },
    { icon: <Settings size={20} />, label: "Settings", href: "/settings" },
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
    toast.success("Neural Session Terminated. Returning to Baseline.");
    router.push("/auth");
  };

  return (
    <div className="flex min-h-screen bg-[#020617]">
      {/* Sidebar */}
      <aside className="w-64 border-r border-card-border bg-[#020617]/50 backdrop-blur-xl flex flex-col fixed h-full z-20">
        <Link href="/" className="p-6 flex items-center gap-3 hover:opacity-80 transition-opacity cursor-pointer">
          <div className="relative w-10 h-10">
            <Image src="/icon.png" alt="ELYX Icon" fill className="object-contain" />
          </div>
          <Image src="/text.png" alt="ELYX" width={80} height={20} className="object-contain" />
        </Link>

        <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto scrollbar-hide">
          {sidebarItems.map((item, i) => {
            const active = pathname === item.href;
            return (
              <Link
                key={i}
                href={item.href}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group cursor-pointer ${
                  active 
                    ? "bg-primary/10 text-primary border border-primary/20" 
                    : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                }`}
              >
                <span className={active ? "text-primary" : "text-slate-500 group-hover:text-primary transition-colors"}>
                  {item.icon}
                </span>
                <span className="font-medium text-sm">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-card-border space-y-3">
          {/* API Terminal Premium Button */}
          <Link 
            href="/api-docs" 
            className="group relative flex items-center justify-center gap-3 py-3.5 bg-slate-900 border border-card-border hover:border-primary/50 transition-all overflow-hidden shadow-2xl rounded-2xl"
          >
            <div className="absolute inset-0 bg-primary/[0.03] opacity-0 group-hover:opacity-100 transition-opacity" />
            <Terminal size={16} className="text-slate-500 group-hover:text-primary transition-colors" />
            <span className="text-[10px] font-black text-slate-400 group-hover:text-slate-200 uppercase tracking-[0.2em]">Developer Hub</span>
            <div className="w-1 h-1 rounded-full bg-primary shadow-[0_0_8px_rgba(6,182,212,0.8)] animate-pulse" />
          </Link>

          {/* Help Center Premium Button */}
          <Link 
            href="/help" 
            className="group relative flex items-center justify-center gap-3 py-3.5 bg-slate-900 border border-card-border hover:border-emerald-500/50 rounded-2xl transition-all overflow-hidden shadow-2xl"
          >
            <div className="absolute inset-0 bg-emerald-500/[0.03] opacity-0 group-hover:opacity-100 transition-opacity" />
            <HelpCircle size={16} className="text-slate-500 group-hover:text-emerald-500 transition-colors" />
            <span className="text-[10px] font-black text-slate-400 group-hover:text-slate-200 uppercase tracking-[0.2em]">Help Center</span>
            <div className="w-1 h-1 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
          </Link>

          {/* System Status Panel */}
          <div className="glass-panel rounded-xl p-4 bg-emerald-950/20 border border-accent/10 hover:border-accent/30 transition-all">
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-1.5 h-1.5 rounded-full ${data?.health.status === 'healthy' ? 'bg-accent animate-pulse' : 'bg-red-500'}`} />
              <span className="text-[10px] font-black text-accent uppercase tracking-[0.2em]">System Optimal</span>
            </div>
            <p className="text-[10px] text-slate-500 leading-relaxed font-bold">
              Phi Stability: {data?.consciousness.phi.toFixed(1) || "98.4"}%
            </p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-64">
        {/* Header */}
        <header className="h-20 border-b border-card-border bg-[#020617]/50 backdrop-blur-md sticky top-0 z-10 px-8 flex items-center justify-between">
          <div className="flex items-center gap-4 bg-slate-900/50 border border-card-border rounded-full px-4 py-2 w-96">
            <Search size={18} className="text-slate-500" />
            <input 
              type="text" 
              placeholder="Search neural core..." 
              className="bg-transparent border-none outline-none text-sm text-slate-300 w-full font-medium"
            />
          </div>

          <div className="flex items-center gap-6">
            <button className="relative text-slate-400 hover:text-primary transition-all group">
              <Bell size={22} className="group-hover:rotate-12 transition-transform" />
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full border-2 border-[#020617] text-[10px] font-black text-white flex items-center justify-center">
                {data?.tasks.pending_count || 0}
              </span>
            </button>
            <div className="flex items-center gap-4 pl-6 border-l border-card-border group relative">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-black text-slate-200 group-hover:text-primary transition-colors">
                  {user?.email?.split('@')[0] || "Neural Entity"}
                </p>
                <p className="text-[10px] font-black text-primary uppercase tracking-tighter">
                  {user ? "Verified Agent" : "Premium Node Access"}
                </p>
              </div>
              <button 
                onClick={handleSignOut}
                className="w-11 h-11 rounded-2xl border border-primary/20 p-1 overflow-hidden bg-slate-900 transition-all group-hover:border-red-500/50 group-hover:shadow-[0_0_15px_rgba(239,68,68,0.2)] flex items-center justify-center group"
              >
                <div className="w-full h-full rounded-xl bg-slate-800 flex items-center justify-center relative">
                   <LogOut size={18} className="text-slate-400 group-hover:text-red-500 transition-colors" />
                </div>
              </button>
            </div>
          </div>
        </header>

        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
