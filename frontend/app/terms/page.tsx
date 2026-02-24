"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { ArrowLeft, FileText } from "lucide-react";

export default function TermsAndConditions() {
  const router = useRouter();
  
  return (
    <div className="min-h-screen bg-[#020617] text-slate-300 py-20 px-6 selection:bg-primary selection:text-slate-950 relative overflow-hidden font-sans">
      {/* Premium Watermark */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none select-none overflow-hidden z-0 opacity-[0.03]">
        <Image 
          src="/icon.png" 
          alt="" 
          width={800} 
          height={800} 
          className="grayscale"
        />
      </div>

      <div className="max-w-3xl mx-auto relative z-10">
        <button 
          onClick={() => router.back()} 
          className="inline-flex items-center gap-3 text-primary font-bold mb-12 hover:gap-4 transition-all uppercase tracking-widest text-[10px] font-outfit"
        >
          <ArrowLeft size={16} />
          Back to System
        </button>
        
        <div className="flex items-center gap-6 mb-12">
           <div className="p-4 rounded-2xl bg-primary/5 text-primary border border-primary/10 shadow-lg shadow-primary/5">
              <FileText size={32} />
           </div>
           <h1 className="text-5xl md:text-6xl font-black text-slate-50 tracking-tighter font-outfit">Terms of <span className="emerald-blue-text italic text-4xl md:text-5xl">Service</span></h1>
        </div>

        <div className="space-y-8 leading-relaxed font-medium">
          <section>
            <h2 className="text-xl font-bold text-slate-100 mb-4">1. Acceptance of Terms</h2>
            <p>
              By accessing ELYX, you agree to be bound by these terms across all primary and auxiliary workflows. You represent that you have the legal authority to enter into this agreement.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-100 mb-4">2. Autonomy and Usage</h2>
            <p>
              ELYX operates as a semi-autonomous digital entity. While ELYX provides high-level business reasoning and predictive analysis, the ultimate decision-making responsibility remains with the primary owner (User). ELYX is not responsible for outcomes resulting from autonomous task execution initiated by the user.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-100 mb-4">3. Prohibited Activities</h2>
            <p>
              Users may not use ELYX to simulate illicit activities, generate malicious automated loops, or attempt to breach the system integrity of other users' environments.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-100 mb-4">4. Termination of Access</h2>
            <p>
              Violation of safety protocols may result in the immediate suspension of your access credentials and purging of all associated operational data.
            </p>
          </section>
        </div>

        <div className="mt-20 pt-8 border-t border-card-border text-xs text-slate-500">
           Last updated: February 2026 • Version 2.0 (Standard-Enterprise)
        </div>
      </div>
    </div>
  );
}
