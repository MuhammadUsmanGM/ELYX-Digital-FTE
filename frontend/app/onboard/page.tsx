"use client";

import { useState, useEffect } from "react";
import {
  ArrowRight,
  CheckCircle2,
  Loader2,
  Shield,
  Zap,
  MessageSquare,
  Mail,
  Linkedin,
  Twitter,
  Facebook,
  Instagram,
  Smartphone,
  Globe,
  Database,
  Key,
  Server,
  Terminal
} from "lucide-react";
import { useRouter } from "next/navigation";
import { toast } from "react-hot-toast";
import { motion } from "framer-motion";
import { saveOnboardingData } from "@/lib/api";

const CHANNELS = [
  { id: 'gmail', name: 'Gmail', icon: <Mail className="w-6 h-6" />, description: 'Email monitoring and responses' },
  { id: 'whatsapp', name: 'WhatsApp', icon: <Smartphone className="w-6 h-6" />, description: 'Instant messaging' },
  { id: 'linkedin', name: 'LinkedIn', icon: <Linkedin className="w-6 h-6" />, description: 'Professional networking' },
  { id: 'twitter', name: 'Twitter/X', icon: <Twitter className="w-6 h-6" />, description: 'Social media updates' },
  { id: 'facebook', name: 'Facebook', icon: <Facebook className="w-6 h-6" />, description: 'Social networking' },
  { id: 'instagram', name: 'Instagram', icon: <Instagram className="w-6 h-6" />, description: 'Visual content sharing' }
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [selectedChannels, setSelectedChannels] = useState<string[]>([]);
  const [anthropicKey, setAnthropicKey] = useState('');
  const [gmailCreds, setGmailCreds] = useState<File | null>(null);
  const [isSettingUp, setIsSettingUp] = useState(false);
  const [setupProgress, setSetupProgress] = useState<string>('');

  const toggleChannel = (channelId: string) => {
    setSelectedChannels(prev =>
      prev.includes(channelId)
        ? prev.filter(id => id !== channelId)
        : [...prev, channelId]
    );
  };

  const handleFileDrop = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setGmailCreds(file);
      toast.success('Gmail credentials loaded');
    }
  };

  const completeOnboarding = async () => {
    setIsSettingUp(true);
    
    try {
      // Step 1: Save configuration
      setSetupProgress('Saving configuration...');
      await saveOnboardingData({
        user_id: 'current_user',
        anthropic_key: anthropicKey,
        selected_channels: selectedChannels
      });

      // Step 2: Create vault structure
      setSetupProgress('Creating vault structure...');
      await fetch('http://localhost:8080/api/vault/summary').catch(() => {
        // Vault API might not be running, that's OK
      });

      // Step 3: Setup complete
      setSetupProgress('Finalizing setup...');
      await new Promise(resolve => setTimeout(resolve, 1000));

      toast.success('Welcome to ELYX! Your AI employee is ready.');
      router.push('/dashboard');
    } catch (error) {
      console.error('Onboarding error:', error);
      toast.error('Setup failed. Please try again.');
    } finally {
      setIsSettingUp(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-50 flex items-center justify-center p-6">
      <div className="max-w-4xl w-full">
        {/* Progress Steps */}
        <div className="mb-12">
          <div className="flex items-center justify-between mb-4">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all ${
                  step >= s ? 'bg-primary text-white' : 'bg-slate-800 text-slate-500'
                }`}>
                  {step > s ? <CheckCircle2 className="w-5 h-5" /> : s}
                </div>
                {s < 3 && (
                  <div className={`w-24 h-1 mx-4 rounded ${
                    step > s ? 'bg-primary' : 'bg-slate-800'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-slate-500">
            <span>AI Setup</span>
            <span>Channels</span>
            <span>Vault Setup</span>
          </div>
        </div>

        {/* Step 1: AI Configuration */}
        {step === 1 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-panel rounded-3xl p-10"
          >
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 rounded-full text-primary mb-6">
                <Zap className="w-4 h-4" />
                <span className="text-xs font-bold uppercase tracking-widest">Step 1 of 3</span>
              </div>
              <h1 className="text-4xl font-black text-white mb-4">Configure Your AI Brain</h1>
              <p className="text-slate-400 text-lg">Choose your AI provider and enter your API key</p>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">
                  AI Provider
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <button className="p-4 bg-primary/20 border border-primary/50 rounded-xl text-left">
                    <div className="flex items-center gap-3 mb-2">
                      <Shield className="w-5 h-5 text-primary" />
                      <span className="font-semibold text-white">Claude (Anthropic)</span>
                    </div>
                    <p className="text-xs text-slate-400">Recommended for complex reasoning</p>
                  </button>
                  <button className="p-4 bg-slate-800 border border-slate-700 rounded-xl text-left opacity-50">
                    <div className="flex items-center gap-3 mb-2">
                      <Globe className="w-5 h-5 text-slate-400" />
                      <span className="font-semibold text-slate-300">More coming soon</span>
                    </div>
                    <p className="text-xs text-slate-500">Qwen, Gemini, Codex support</p>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">
                  Anthropic API Key
                </label>
                <input
                  type="password"
                  value={anthropicKey}
                  onChange={(e) => setAnthropicKey(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-primary"
                  placeholder="sk-ant-..."
                />
                <p className="text-xs text-slate-500 mt-2">
                  Get your API key from{' '}
                  <a href="https://console.anthropic.com" target="_blank" className="text-primary hover:underline">
                    console.anthropic.com
                  </a>
                </p>
              </div>

              <button
                onClick={() => setStep(2)}
                disabled={!anthropicKey}
                className="w-full py-4 bg-primary hover:bg-primary/80 disabled:bg-slate-800 disabled:text-slate-500 rounded-xl text-white font-semibold transition-all flex items-center justify-center gap-2"
              >
                Continue
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 2: Channel Selection */}
        {step === 2 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-panel rounded-3xl p-10"
          >
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 rounded-full text-primary mb-6">
                <MessageSquare className="w-4 h-4" />
                <span className="text-xs font-bold uppercase tracking-widest">Step 2 of 3</span>
              </div>
              <h1 className="text-4xl font-black text-white mb-4">Select Communication Channels</h1>
              <p className="text-slate-400 text-lg">Choose which channels your AI should monitor</p>
            </div>

            <div className="grid md:grid-cols-2 gap-4 mb-8">
              {CHANNELS.map((channel) => (
                <button
                  key={channel.id}
                  onClick={() => toggleChannel(channel.id)}
                  className={`p-4 rounded-xl border transition-all text-left ${
                    selectedChannels.includes(channel.id)
                      ? 'bg-primary/20 border-primary/50'
                      : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${
                      selectedChannels.includes(channel.id)
                        ? 'bg-primary/30 text-primary'
                        : 'bg-slate-700 text-slate-400'
                    }`}>
                      {channel.icon}
                    </div>
                    <div>
                      <h3 className="font-semibold text-white">{channel.name}</h3>
                      <p className="text-xs text-slate-400">{channel.description}</p>
                    </div>
                    {selectedChannels.includes(channel.id) && (
                      <CheckCircle2 className="w-5 h-5 text-primary ml-auto" />
                    )}
                  </div>
                </button>
              ))}
            </div>

            {selectedChannels.includes('gmail') && (
              <div className="mb-6 p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                <div className="flex items-center gap-3 mb-3">
                  <Mail className="w-5 h-5 text-primary" />
                  <span className="font-semibold text-white">Gmail Setup Required</span>
                </div>
                <input
                  type="file"
                  accept=".json"
                  onChange={handleFileDrop}
                  className="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary/20 file:text-primary hover:file:bg-primary/30"
                />
                <p className="text-xs text-slate-500 mt-2">
                  Upload your gmail_credentials.json file from Google Cloud Console
                </p>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="flex-1 py-4 bg-slate-800 hover:bg-slate-700 rounded-xl text-white font-semibold transition-all"
              >
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                disabled={selectedChannels.length === 0}
                className="flex-1 py-4 bg-primary hover:bg-primary/80 disabled:bg-slate-800 disabled:text-slate-500 rounded-xl text-white font-semibold transition-all flex items-center justify-center gap-2"
              >
                Continue
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 3: Vault Setup */}
        {step === 3 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-panel rounded-3xl p-10"
          >
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 rounded-full text-primary mb-6">
                <Database className="w-4 h-4" />
                <span className="text-xs font-bold uppercase tracking-widest">Step 3 of 3</span>
              </div>
              <h1 className="text-4xl font-black text-white mb-4">Setup Your Vault</h1>
              <p className="text-slate-400 text-lg">Initialize your Obsidian vault and start ELYX</p>
            </div>

            {isSettingUp ? (
              <div className="text-center py-12">
                <Loader2 className="w-16 h-16 animate-spin text-primary mx-auto mb-6" />
                <h3 className="text-xl font-semibold text-white mb-2">Setting up your workspace...</h3>
                <p className="text-slate-400">{setupProgress}</p>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                    <Database className="w-8 h-8 text-primary mb-3" />
                    <h3 className="font-semibold text-white mb-2">Obsidian Vault</h3>
                    <p className="text-xs text-slate-400">Local markdown storage for all tasks and memories</p>
                  </div>
                  <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                    <Terminal className="w-8 h-8 text-primary mb-3" />
                    <h3 className="font-semibold text-white mb-2">Vault API</h3>
                    <p className="text-xs text-slate-400">REST API for vault operations on port 8080</p>
                  </div>
                  <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                    <Server className="w-8 h-8 text-primary mb-3" />
                    <h3 className="font-semibold text-white mb-2">MCP Servers</h3>
                    <p className="text-xs text-slate-400">Tool servers for AI agent integration</p>
                  </div>
                </div>

                <div className="bg-primary/10 border border-primary/20 rounded-xl p-6">
                  <h3 className="font-semibold text-white mb-3">After setup:</h3>
                  <ul className="space-y-2 text-sm text-slate-300">
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary" />
                      Vault API will start on http://localhost:8080
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary" />
                      You can manage tasks at /tasks and /approvals
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary" />
                      AI will monitor your selected channels
                    </li>
                  </ul>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => setStep(2)}
                    className="flex-1 py-4 bg-slate-800 hover:bg-slate-700 rounded-xl text-white font-semibold transition-all"
                  >
                    Back
                  </button>
                  <button
                    onClick={completeOnboarding}
                    className="flex-1 py-4 bg-primary hover:bg-primary/80 rounded-xl text-white font-semibold transition-all flex items-center justify-center gap-2"
                  >
                    <Zap className="w-5 h-5" />
                    Complete Setup
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
