"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { 
  Settings, 
  MessageSquare, 
  CheckCircle2, 
  Bell, 
  Cpu, 
  Shield, 
  BrainCircuit,
  Save,
  RefreshCw,
  ToggleLeft,
  ToggleRight,
  ChevronRight,
  Loader2
} from "lucide-react";
import { fetchUserPreferences, updateUserPreference } from "@/lib/api";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("communication");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<Record<string, any>>({
    communication_whatsapp: true,
    communication_linkedin: true,
    communication_email_sorting: false,
    workflow_verification: true,
    ai_logic_projection: true,
    ai_tone_adjustment: true,
    ai_safety_anchors: true,
    notifications_instant_alerts: true,
    notifications_workflow_requests: true,
    notifications_daily_digest: false,
    brand_voice: "Corporate Professional (Standard)"
  });

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const prefs = await fetchUserPreferences();
        const newSettings = { ...settings };
        prefs.forEach((p: any) => {
          let val = p.preference_value;
          try {
            const parsed = JSON.parse(val);
            val = parsed.value !== undefined ? parsed.value : parsed;
          } catch (e) {
            // Keep as is if not JSON
          }
          if (val === "true") val = true;
          if (val === "false") val = false;
          newSettings[p.preference_key] = val;
        });
        setSettings(newSettings);
      } catch (error) {
        console.error("Failed to load settings:", error);
      } finally {
        setLoading(false);
      }
    };
    loadSettings();
  }, []);

  const handleToggle = (key: string) => {
    setSettings(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Save each setting (In a real app, you might have a bulk update API)
      for (const [key, value] of Object.entries(settings)) {
        await updateUserPreference(key, value);
      }
      alert("Configuration committed to system core successfully.");
    } catch (error) {
      alert("Failed to sync settings with backend.");
    } finally {
      setSaving(false);
    }
  };

  const tabs = [
    { id: "communication", label: "Communication", icon: <MessageSquare size={18} /> },
    { id: "workflow", label: "Workflow", icon: <CheckCircle2 size={18} /> },
    { id: "notifications", label: "Notifications", icon: <Bell size={18} /> },
    { id: "ai_behavior", label: "AI Behavior", icon: <Cpu size={18} /> },
    { id: "security", label: "System Security", icon: <Shield size={18} /> }
  ];

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
          <Loader2 className="animate-spin text-primary mb-4" size={48} />
          <p className="text-slate-400 font-bold uppercase tracking-widest">Accessing System Config...</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-8 max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
          <div>
            <h1 className="text-4xl font-black text-white mb-2 flex items-center gap-3">
              <Settings className="text-primary" size={32} />
              System Configuration
            </h1>
            <p className="text-slate-500 font-medium">Fine-tune your ELYX digital employee's operational constraints and logic scope.</p>
          </div>
          <button 
            onClick={handleSave} 
            disabled={saving}
            className="btn-premium-primary !px-8 !py-4 disabled:opacity-50"
          >
            {saving ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
            {saving ? "Syncing..." : "Commit Changes"}
          </button>
        </div>

        <div className="grid lg:grid-cols-[280px_1fr] gap-10">
          {/* Navigation Tabs */}
          <div className="space-y-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center justify-between p-4 rounded-2xl transition-all duration-300 group ${
                  activeTab === tab.id 
                    ? "bg-primary/10 text-primary border border-primary/20 shadow-[0_0_20px_rgba(6,182,212,0.1)]" 
                    : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`transition-colors ${activeTab === tab.id ? "text-primary" : "text-slate-500 group-hover:text-primary"}`}>
                    {tab.icon}
                  </div>
                  <span className="font-bold text-sm uppercase tracking-widest">{tab.label}</span>
                </div>
                <ChevronRight size={16} className={`transition-transform ${activeTab === tab.id ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-2"}`} />
              </button>
            ))}
          </div>

          {/* Settings Content */}
          <div className="glass-panel rounded-[2rem] p-10 min-h-[600px] border-card-border/30">
            {activeTab === "communication" && (
              <div className="space-y-10 animate-fade-in">
                <section>
                  <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                    <MessageSquare size={20} className="text-primary" />
                    Communication Preferences
                  </h3>
                  <div className="space-y-6">
                    <SettingToggle 
                      title="Autonomous WhatsApp Engagement" 
                      desc="Allow ELYX to initiate and respond to WhatsApp messages without human oversight."
                      active={settings.communication_whatsapp}
                      onToggle={() => handleToggle('communication_whatsapp')}
                    />
                    <SettingToggle 
                      title="LinkedIn Outreach Protocol" 
                      desc="Enable autonomous processing of LinkedIn connection requests and direct messages."
                      active={settings.communication_linkedin}
                      onToggle={() => handleToggle('communication_linkedin')}
                    />
                    <SettingToggle 
                      title="Email Priority Sorting" 
                      desc="Automatically categorize incoming emails based on system priority detection."
                      active={settings.communication_email_sorting}
                      onToggle={() => handleToggle('communication_email_sorting')}
                    />
                  </div>
                </section>

                <section className="pt-10 border-t border-card-border/30">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-bold text-white">Brand Voice Profile</h3>
                    <div className="px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-[10px] font-black text-primary uppercase tracking-widest">
                       Logical Synthesis Active
                    </div>
                  </div>
                  
                  {/* Premium Custom Select */}
                  <div className="relative mb-8">
                    <button 
                      onClick={() => setSettings(prev => ({ ...prev, _voiceDropdown: !prev._voiceDropdown }))}
                      className="w-full bg-slate-900 border border-card-border rounded-xl p-4 text-left text-slate-300 font-bold flex items-center justify-between hover:border-primary/50 transition-all"
                    >
                      <span className="flex items-center gap-3">
                         <div className="w-2 h-2 rounded-full bg-primary shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
                         {settings.brand_voice}
                      </span>
                      <ChevronRight size={18} className={`transition-transform duration-300 ${settings._voiceDropdown ? 'rotate-90' : ''}`} />
                    </button>

                    {settings._voiceDropdown && (
                      <div className="absolute top-full left-0 right-0 mt-2 bg-slate-900 border border-card-border rounded-2xl overflow-hidden z-20 shadow-2xl animate-in fade-in slide-in-from-top-2">
                        {["Corporate Professional (Standard)", "Technical Specialist", "Friendly & Approachable", "Minimalist / Concise"].map((voice) => (
                          <button
                            key={voice}
                            onClick={() => setSettings(prev => ({ ...prev, brand_voice: voice, _voiceDropdown: false }))}
                            className={`w-full p-4 text-left text-sm font-bold transition-all hover:bg-primary/10 ${settings.brand_voice === voice ? 'text-primary bg-primary/5' : 'text-slate-400'}`}
                          >
                            {voice}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Intelligence Metrics Table */}
                  <div className="rounded-2xl border border-card-border/30 bg-slate-900/40 overflow-hidden">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="border-b border-card-border/30 bg-slate-900/60">
                          <th className="p-4 text-[10px] font-black uppercase tracking-widest text-slate-500">Logic Parameters</th>
                          <th className="p-4 text-[10px] font-black uppercase tracking-widest text-slate-500">Value Delta</th>
                          <th className="p-4 text-[10px] font-black uppercase tracking-widest text-slate-500 text-right">Optimization</th>
                        </tr>
                      </thead>
                      <tbody className="text-xs font-bold divide-y divide-card-border/20">
                        <VoiceMetricRow 
                           label="Syntactic Complexity" 
                           value={settings.brand_voice.includes("Technical") ? "9.4/10" : settings.brand_voice.includes("Minimalist") ? "1.2/10" : "6.8/10"} 
                           status="stable"
                        />
                        <VoiceMetricRow 
                           label="Empathy Resonance" 
                           value={settings.brand_voice.includes("Friendly") ? "9.8/10" : "4.2/10"} 
                           status="active"
                        />
                        <VoiceMetricRow 
                           label="Fact-Verification Depth" 
                           value={settings.brand_voice.includes("Corporate") || settings.brand_voice.includes("Technical") ? "Deep" : "Surface"} 
                           status="stable"
                        />
                        <VoiceMetricRow 
                           label="Response Latency Target" 
                           value={settings.brand_voice.includes("Minimalist") ? "< 200ms" : "< 1200ms"} 
                           status="optimized"
                        />
                      </tbody>
                    </table>
                  </div>
                </section>
              </div>
            )}

            {activeTab === "workflow" && (
              <div className="space-y-10 animate-fade-in">
                <section>
                  <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                    <CheckCircle2 size={20} className="text-primary" />
                    Approval Workflow
                  </h3>
                  <div className="space-y-8">
                    <SettingToggle 
                      title="Strict Process Verification" 
                      desc="Require dual-layered workflow verification for all high-stakes business decisions."
                      active={settings.workflow_verification}
                      onToggle={() => handleToggle('workflow_verification')}
                    />
                    <div className="p-6 rounded-2xl bg-primary/5 border border-primary/10">
                      <p className="text-xs font-black uppercase tracking-[0.2em] text-primary mb-2">Threshold Configuration</p>
                      <input type="range" className="w-full accent-primary h-2 bg-slate-900 rounded-lg appearance-none cursor-pointer" />
                      <div className="flex justify-between mt-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                        <span>Low Autonomy</span>
                        <span className="text-primary">Current: 85% Auto</span>
                        <span>Full Autonomy</span>
                      </div>
                    </div>
                  </div>
                </section>
              </div>
            )}

            {activeTab === "ai_behavior" && (
              <div className="space-y-10 animate-fade-in">
                <section>
                  <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                    <BrainCircuit size={20} className="text-primary" />
                    AI Logic Constraints
                  </h3>
                  <div className="space-y-6">
                    <SettingToggle 
                      title="Workflow Outcome Projection" 
                      desc="Enable the AI to project outcomes into simulated scenarios before responding."
                      active={settings.ai_logic_projection}
                      onToggle={() => handleToggle('ai_logic_projection')}
                    />
                    <SettingToggle 
                      title="Adaptive Tone System" 
                      desc="Allow AI to adjust communication tone based on perceived context and intent."
                      active={settings.ai_tone_adjustment}
                      onToggle={() => handleToggle('ai_tone_adjustment')}
                    />
                    <SettingToggle 
                      title="Operational Safety Anchors" 
                      desc="Ensure all AI reasoning adheres to primary ethical and operational rules."
                      active={settings.ai_safety_anchors}
                      onToggle={() => handleToggle('ai_safety_anchors')}
                    />
                  </div>
                </section>
              </div>
            )}

            {activeTab === "notifications" && (
              <div className="space-y-10 animate-fade-in">
                <section>
                  <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                    <Bell size={20} className="text-primary" />
                    System Alert Configurations
                  </h3>
                  <div className="space-y-6">
                    <SettingToggle 
                      title="Instant Operational Alerts" 
                      desc="Receive real-time notifications for every autonomous action performed."
                      active={settings.notifications_instant_alerts}
                      onToggle={() => handleToggle('notifications_instant_alerts')}
                    />
                    <SettingToggle 
                      title="Workflow Verification Requests" 
                      desc="Notify via desktop and mobile when a high-stakes decision requires manual oversight."
                      active={settings.notifications_workflow_requests}
                      onToggle={() => handleToggle('notifications_workflow_requests')}
                    />
                    <SettingToggle 
                      title="Daily Performance Digest" 
                      desc="Synthesize all interactions into a single comprehensive morning report."
                      active={settings.notifications_daily_digest}
                      onToggle={() => handleToggle('notifications_daily_digest')}
                    />
                  </div>
                </section>

                <section className="pt-10 border-t border-card-border/30">
                  <h3 className="text-lg font-bold text-white mb-4">Notification Channels</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <button className="flex items-center justify-between p-4 rounded-xl bg-slate-900 border border-card-border hover:border-primary/50 transition-all">
                      <span className="text-xs font-bold text-slate-300">Desktop Push</span>
                      <div className="w-2 h-2 rounded-full bg-primary" />
                    </button>
                    <button className="flex items-center justify-between p-4 rounded-xl bg-slate-900 border border-card-border hover:border-primary/50 transition-all">
                      <span className="text-xs font-bold text-slate-300">Email Alerts</span>
                      <div className="w-2 h-2 rounded-full bg-primary" />
                    </button>
                  </div>
                </section>
              </div>
            )}

            {/* Placeholder for other tabs to keep UI consistent */}
            {activeTab === "security" && (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
                 <div className="p-8 rounded-full bg-slate-900/50 border border-card-border animate-pulse">
                   <RefreshCw size={48} className="text-slate-600" />
                 </div>
                 <h3 className="text-xl font-bold text-slate-400 uppercase tracking-widest">Sector Initializing</h3>
                 <p className="text-slate-600 max-w-xs mx-auto">This system configuration module is currently being optimized for your tier.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

function SettingToggle({ title, desc, active, onToggle }: { title: string, desc: string, active: boolean, onToggle: () => void }) {
  return (
    <div className="flex items-start justify-between gap-6 p-4 hover:bg-slate-900/40 rounded-2xl transition-colors">
      <div className="space-y-1">
        <h4 className="text-sm font-bold text-slate-100 uppercase tracking-wider">{title}</h4>
        <p className="text-xs text-slate-500 leading-relaxed max-w-md">{desc}</p>
      </div>
      <button onClick={onToggle} className={`transition-colors duration-300 ${active ? 'text-primary' : 'text-slate-800'}`}>
        {active ? <ToggleRight size={40} /> : <ToggleLeft size={40} />}
      </button>
    </div>
  );
}

function VoiceMetricRow({ label, value, status }: { label: string, value: string, status: string }) {
  return (
    <tr className="hover:bg-primary/5 transition-colors">
      <td className="p-4 text-slate-300">{label}</td>
      <td className="p-4 text-slate-100">{value}</td>
      <td className="p-4 text-right">
        <span className={`px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-tighter ${
          status === 'optimized' ? 'bg-emerald-500/20 text-emerald-400' : 
          status === 'stable' ? 'bg-blue-500/20 text-blue-400' : 
          'bg-primary/20 text-primary animate-pulse'
        }`}>
          {status}
        </span>
      </td>
    </tr>
  );
}
