"use client";

import { useState, useEffect } from "react";
import {
  Cpu,
  Shield,
  TrendingUp,
  Plug,
  ToggleLeft,
  ToggleRight,
  Save,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  RefreshCcw
} from "lucide-react";
import { toast } from "react-hot-toast";
import { motion } from "framer-motion";
import { fetchFeatureFlags, updateFeatureFlag, FeatureFlag } from "@/lib/api";

export default function FeatureFlagsTab() {
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<Record<string, boolean>>({});
  const [activeCategory, setActiveCategory] = useState<string>("all");

  const loadFlags = async () => {
    try {
      setLoading(true);
      const data = await fetchFeatureFlags();
      setFlags(data);
    } catch (error) {
      console.error("Failed to load feature flags:", error);
      toast.error("Failed to load feature flags");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFlags();
  }, []);

  const handleToggle = async (flagName: string, currentValue: boolean) => {
    setSaving(prev => ({ ...prev, [flagName]: true }));
    
    try {
      const success = await updateFeatureFlag(flagName, !currentValue);
      
      if (success) {
        setFlags(prev =>
          prev.map(f =>
            f.name === flagName ? { ...f, value: !currentValue } : f
          )
        );
        toast.success(`${flagName} ${!currentValue ? 'enabled' : 'disabled'}`);
      } else {
        toast.error(`Failed to update ${flagName}`);
      }
    } catch (error) {
      console.error("Toggle failed:", error);
      toast.error("Failed to update feature flag");
    } finally {
      setSaving(prev => ({ ...prev, [flagName]: false }));
    }
  };

  const categories = [
    { id: "all", label: "All", icon: <Cpu size={16} /> },
    { id: "features", label: "Features", icon: <TrendingUp size={16} /> },
    { id: "security", label: "Security", icon: <Shield size={16} /> },
    { id: "integrations", label: "Integrations", icon: <Plug size={16} /> }
  ];

  const filteredFlags = activeCategory === "all"
    ? flags
    : flags.filter(f => f.category === activeCategory);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="animate-spin text-primary" size={48} />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
            <Cpu className="text-primary" size={24} />
            Feature Flags
          </h3>
          <p className="text-slate-400">
            Enable or disable advanced features and experimental functionality
          </p>
        </div>
        
        <button
          onClick={loadFlags}
          className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
        >
          <RefreshCcw className="w-5 h-5 text-slate-400" />
        </button>
      </div>

      {/* Category Filter */}
      <div className="flex gap-2 border-b border-slate-800">
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`px-4 py-2 text-sm font-medium transition-all flex items-center gap-2 ${
              activeCategory === cat.id
                ? "text-primary border-b-2 border-primary"
                : "text-slate-400 hover:text-slate-300"
            }`}
          >
            {cat.icon}
            {cat.label}
            {cat.id !== "all" && (
              <span className="text-xs bg-slate-800 px-2 py-0.5 rounded-full">
                {flags.filter(f => f.category === cat.id).length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Feature Flags Grid */}
      <div className="grid gap-4">
        {filteredFlags.map((flag, index) => (
          <motion.div
            key={flag.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="glass-panel p-6 rounded-xl"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="font-semibold text-white text-lg">{flag.name}</h4>
                  <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                    flag.category === 'features' ? 'bg-green-500/20 text-green-400' :
                    flag.category === 'security' ? 'bg-red-500/20 text-red-400' :
                    'bg-blue-500/20 text-blue-400'
                  }`}>
                    {flag.category}
                  </span>
                  {!flag.default && (
                    <span className="text-xs text-slate-500">(Custom)</span>
                  )}
                </div>
                
                <p className="text-slate-400 text-sm mb-3">{flag.description}</p>
                
                <div className="flex items-center gap-4 text-xs">
                  <span className="text-slate-500">
                    Default: <span className={flag.default ? 'text-green-400' : 'text-slate-400'}>
                      {flag.default ? 'Enabled' : 'Disabled'}
                    </span>
                  </span>
                  <span className="text-slate-500">
                    Current: <span className={flag.value ? 'text-green-400' : 'text-slate-400'}>
                      {flag.value ? 'Enabled' : 'Disabled'}
                    </span>
                  </span>
                </div>
              </div>
              
              <button
                onClick={() => handleToggle(flag.name, flag.value)}
                disabled={saving[flag.name]}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  flag.value
                    ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                    : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {saving[flag.name] ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : flag.value ? (
                  <>
                    <ToggleRight className="w-6 h-6" />
                    <span className="text-sm font-bold">ON</span>
                  </>
                ) : (
                  <>
                    <ToggleLeft className="w-6 h-6" />
                    <span className="text-sm font-bold">OFF</span>
                  </>
                )}
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Info Box */}
      <div className="glass-panel p-6 rounded-xl border border-primary/20">
        <div className="flex items-start gap-4">
          <AlertTriangle className="w-6 h-6 text-primary flex-shrink-0 mt-1" />
          <div>
            <h4 className="font-semibold text-white mb-2">Important Notes</h4>
            <ul className="text-sm text-slate-400 space-y-1">
              <li>• Changes are saved to .env file immediately</li>
              <li>• Some features may require restarting ELYX to take effect</li>
              <li>• Security features should only be disabled for debugging</li>
              <li>• Default values are recommended for most use cases</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
