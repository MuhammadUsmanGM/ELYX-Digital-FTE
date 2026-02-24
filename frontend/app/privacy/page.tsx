"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { ArrowLeft, ShieldCheck } from "lucide-react";

export default function PrivacyPolicy() {
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
           <div className="p-4 rounded-2xl bg-emerald-500/5 text-emerald-400 border border-emerald-500/10 shadow-lg shadow-emerald-500/5">
              <ShieldCheck size={32} />
           </div>
           <h1 className="text-5xl md:text-6xl font-black text-slate-50 tracking-tighter font-outfit">Privacy <span className="emerald-blue-text italic text-4xl md:text-5xl">Policy</span></h1>
        </div>

        <div className="space-y-8 leading-relaxed font-medium">
          <section>
            <h2 className="text-xl font-bold text-slate-100 mb-4">1. Data Encryption Standards</h2>
            <p>
              At ELYX, your data is treated as a unique digital signature. All interactions across all workflows are encrypted using AES-256 standards. We do not store "data" in the traditional sense; we maintain encrypted data clusters that are inaccessible to any entity other than the primary owner.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-100 mb-4">2. Operational Privacy</h2>
            <p>
              Business workflows managed within Mission Control are isolated. Data generated during processes is purged immediately upon completion unless explicitly saved by the user.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-100 mb-4">3. Biological Metrics</h2>
            <p>
              ELYX does not collect biological biometric data. Any personalization is based purely on system interaction patterns and mission-specific parameters.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-100 mb-4">4. Third-Party Data Practices</h2>
            <p>
              We do not share your workflow history with external advertising networks. ELYX is a zero-trust environment designed for high-stakes autonomous operations.
            </p>
          </section>
        </div>

        <div className="mt-20 pt-8 border-t border-card-border text-xs text-slate-500">
           Last updated: February 2026 • Version 2.0 (Enterprise Edition)
        </div>
      </div>
    </div>
  );
}
