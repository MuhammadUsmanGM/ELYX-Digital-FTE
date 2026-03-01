"use client";

import Link from "next/link";
import Image from "next/image";
import { ArrowLeft, Cookie } from "lucide-react";

export default function CookiesPolicy() {
  return (
    <div className="min-h-screen bg-[#020617] text-slate-300 py-20 px-6 selection:bg-primary selection:text-slate-950 relative overflow-hidden">
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
        <Link href="/" className="inline-flex items-center gap-2 text-primary font-bold mb-12 hover:gap-3 transition-all">
          <ArrowLeft size={20} />
          Back to Reality
        </Link>
        
        <div className="flex items-center gap-4 mb-8">
           <div className="p-3 rounded-2xl bg-primary/10 text-primary border border-primary/20">
              <Cookie size={32} />
           </div>
           <h1 className="text-5xl font-black text-slate-50 tracking-tight">Cookie Protocol</h1>
        </div>

        <div className="space-y-8 leading-relaxed font-medium">
          <section>
            <h2 className="text-xl font-bold text-slate-100 mb-4">1. Temporal Anchors (Essential Cookies)</h2>
            <p>
              These are necessary for the platform to function. They act as temporal anchors, maintaining your neural session and ensuring you stay connected to the correct timeline as you navigate the dashboard.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-100 mb-4">2. Cognitive Preference Cookies</h2>
            <p>
              These cookies help ELYX remember your preferred interface configuration, such as your chosen theme, layout settings, and dashboard focus areas.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-slate-100 mb-4">3. Performance Telemetry</h2>
            <p>
              We use anonymized telemetry to monitor the stability of the ELYX core. This data helps us optimize Φ (phi) stability and cognitive load management across the system.
            </p>
          </section>
        </div>

        <div className="mt-20 pt-8 border-t border-card-border text-xs text-slate-500">
           Last updated: February 2026 • Version 2.0
        </div>
      </div>
    </div>
  );
}
