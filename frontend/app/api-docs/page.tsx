"use client";

import { useState, useEffect } from "react";
import {
  Terminal,
  Code2,
  Server,
  Activity,
  RefreshCcw,
  CheckCircle2,
  XCircle,
  Copy,
  Play,
  Search,
  Zap,
  Lock,
  Globe,
  Cpu,
  Database,
  Shield
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { motion } from "framer-motion";
import { toast } from "react-hot-toast";

interface APIEndpoint {
  id: string;
  method: 'GET' | 'POST';
  path: string;
  title: string;
  description: string;
  category: 'vault' | 'backend' | 'mcp';
  params?: { name: string; type: string; required: boolean; desc: string }[];
  response?: string;
}

const VAULT_ENDPOINTS: APIEndpoint[] = [
  {
    id: 'vault-summary',
    method: 'GET',
    path: '/api/vault/summary',
    title: 'Get Vault Summary',
    description: 'Get dashboard summary statistics from the Obsidian vault',
    category: 'vault',
    response: `{
  "pending_tasks": 3,
  "pending_approvals": 2,
  "completed_tasks": 14,
  "plans_created": 5,
  "last_updated": "2026-03-01T12:00:00"
}`
  },
  {
    id: 'vault-tasks',
    method: 'GET',
    path: '/api/vault/tasks?folder=Needs_Action',
    title: 'Get Tasks',
    description: 'Get all tasks from a specific vault folder',
    category: 'vault',
    params: [
      { name: 'folder', type: 'string', required: true, desc: 'Folder name (Needs_Action, Done, etc.)' }
    ],
    response: `{
  "tasks": [
    {
      "id": "EMAIL_123",
      "filename": "EMAIL_123.md",
      "type": "email",
      "priority": "high",
      "from": "user@example.com",
      "subject": "Test Email"
    }
  ],
  "count": 1
}`
  },
  {
    id: 'vault-approvals',
    method: 'GET',
    path: '/api/vault/approvals',
    title: 'Get Approvals',
    description: 'Get all pending approval requests',
    category: 'vault',
    response: `{
  "approvals": [
    {
      "id": "APPROVAL_456",
      "action": "Post to LinkedIn",
      "reason": "Social media post request"
    }
  ],
  "count": 1
}`
  },
  {
    id: 'vault-approve',
    method: 'POST',
    path: '/api/vault/approve',
    title: 'Approve Task',
    description: 'Approve a pending task (moves to Approved folder)',
    category: 'vault',
    params: [
      { name: 'filename', type: 'string', required: true, desc: 'Name of the approval file' }
    ],
    response: `{
  "success": true,
  "message": "Task approved",
  "filename": "APPROVAL_456.md"
}`
  },
  {
    id: 'vault-reject',
    method: 'POST',
    path: '/api/vault/reject',
    title: 'Reject Task',
    description: 'Reject a pending task (moves to Rejected folder)',
    category: 'vault',
    params: [
      { name: 'filename', type: 'string', required: true, desc: 'Name of the approval file' }
    ],
    response: `{
  "success": true,
  "message": "Task rejected"
}`
  },
  {
    id: 'vault-completed',
    method: 'GET',
    path: '/api/vault/completed',
    title: 'Get Completed Tasks',
    description: 'Get all completed tasks from Done folder',
    category: 'vault',
    response: `{
  "completed": [...],
  "count": 14
}`
  }
];

const BACKEND_ENDPOINTS: APIEndpoint[] = [
  {
    id: 'dashboard-status',
    method: 'GET',
    path: '/api/dashboard/status',
    title: 'Get Dashboard Status',
    description: 'Get main dashboard data including tasks and health',
    category: 'backend',
    response: `{
  "tasks": { "pending_count": 3 },
  "health": { "status": "healthy" }
}`
  },
  {
    id: 'system-state',
    method: 'GET',
    path: '/api/system/state/system_core',
    title: 'Get System State',
    description: 'Get AI system state and stability metrics',
    category: 'backend',
    response: `{
  "system_state": {
    "stability_score": 98.4,
    "coherence_level": 0.95
  }
}`
  }
];

export default function ApiDocsPage() {
  const [activeCategory, setActiveCategory] = useState<'vault' | 'backend'>('vault');
  const [activeEndpoint, setActiveEndpoint] = useState<APIEndpoint | null>(null);
  const [testResult, setTestResult] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);
  const [vaultStatus, setVaultStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [searchQuery, setSearchQuery] = useState('');

  const checkVaultAPI = async () => {
    try {
      setVaultStatus('checking');
      const res = await fetch('http://localhost:8080/api/vault/summary');
      if (res.ok) {
        setVaultStatus('online');
        toast.success('Vault API is online');
      } else {
        setVaultStatus('offline');
      }
    } catch (error) {
      setVaultStatus('offline');
      toast.error('Vault API is offline. Run: python scripts/start_frontend.py');
    }
  };

  useEffect(() => {
    checkVaultAPI();
    const interval = setInterval(checkVaultAPI, 30000);
    return () => clearInterval(interval);
  }, []);

  const testEndpoint = async (endpoint: APIEndpoint) => {
    setTesting(true);
    setTestResult(null);
    
    try {
      const url = `http://localhost:8080${endpoint.path}`;
      const res = await fetch(url);
      const data = await res.json();
      setTestResult(JSON.stringify(data, null, 2));
      toast.success('API call successful');
    } catch (error: any) {
      setTestResult(JSON.stringify({ error: error.message }, null, 2));
      toast.error('API call failed');
    } finally {
      setTesting(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const filteredEndpoints = [...VAULT_ENDPOINTS, ...BACKEND_ENDPOINTS].filter(ep => {
    if (activeCategory !== 'vault' && activeCategory !== 'backend') return true;
    if (activeCategory === 'vault' && ep.category !== 'vault') return false;
    if (activeCategory === 'backend' && ep.category !== 'backend') return false;
    return ep.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
           ep.path.toLowerCase().includes(searchQuery.toLowerCase());
  });

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-3xl font-bold text-white">API Documentation</h1>
            <p className="text-slate-400 mt-1">Live API endpoints and testing interface</p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              vaultStatus === 'online' ? 'bg-green-500/20 text-green-400' :
              vaultStatus === 'offline' ? 'bg-red-500/20 text-red-400' :
              'bg-yellow-500/20 text-yellow-400'
            }`}>
              {vaultStatus === 'online' ? <CheckCircle2 className="w-4 h-4" /> :
               vaultStatus === 'offline' ? <XCircle className="w-4 h-4" /> :
               <RefreshCcw className="w-4 h-4 animate-spin" />}
              <span className="text-sm font-medium">
                Vault API: {vaultStatus === 'online' ? 'Online' : vaultStatus === 'offline' ? 'Offline' : 'Checking...'}
              </span>
            </div>
            
            <button
              onClick={checkVaultAPI}
              className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <RefreshCcw className="w-5 h-5" />
            </button>
          </div>
        </motion.div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search endpoints..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-primary transition-colors"
          />
        </div>

        {/* Category Tabs */}
        <div className="flex gap-2 border-b border-slate-800">
          <button
            onClick={() => setActiveCategory('vault')}
            className={`px-4 py-2 text-sm font-medium transition-all ${
              activeCategory === 'vault'
                ? "text-primary border-b-2 border-primary"
                : "text-slate-400 hover:text-slate-300"
            }`}
          >
            <Database className="w-4 h-4 inline mr-2" />
            Vault API
          </button>
          <button
            onClick={() => setActiveCategory('backend')}
            className={`px-4 py-2 text-sm font-medium transition-all ${
              activeCategory === 'backend'
                ? "text-primary border-b-2 border-primary"
                : "text-slate-400 hover:text-slate-300"
            }`}
          >
            <Server className="w-4 h-4 inline mr-2" />
            Backend API
          </button>
          <button
            onClick={() => setActiveCategory('all')}
            className={`px-4 py-2 text-sm font-medium transition-all ${
              activeCategory === 'all'
                ? "text-primary border-b-2 border-primary"
                : "text-slate-400 hover:text-slate-300"
            }`}
          >
            <Globe className="w-4 h-4 inline mr-2" />
            All Endpoints
          </button>
        </div>

        {/* Endpoints Grid */}
        <div className="grid gap-4">
          {filteredEndpoints.map((endpoint, index) => (
            <motion.div
              key={endpoint.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => setActiveEndpoint(endpoint)}
              className={`glass-panel p-6 rounded-xl cursor-pointer transition-all hover:border-primary/50 ${
                activeEndpoint?.id === endpoint.id ? 'border-primary/50 bg-primary/5' : ''
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-4 flex-1">
                  <div className={`p-3 rounded-lg ${
                    endpoint.method === 'GET' ? 'bg-blue-500/20 text-blue-400' :
                    'bg-green-500/20 text-green-400'
                  }`}>
                    <span className="text-xs font-bold">{endpoint.method}</span>
                  </div>
                  
                  <div className="flex-1">
                    <h3 className="font-semibold text-white mb-1">{endpoint.title}</h3>
                    <code className="text-sm text-slate-400 font-mono">{endpoint.path}</code>
                    <p className="text-sm text-slate-500 mt-2">{endpoint.description}</p>
                    
                    {endpoint.params && endpoint.params.length > 0 && (
                      <div className="mt-3 space-y-1">
                        {endpoint.params.map((param, i) => (
                          <div key={i} className="text-xs text-slate-500">
                            <span className="text-primary font-medium">{param.name}</span>
                            <span className="text-slate-600 mx-2">•</span>
                            <span className="text-slate-400">{param.type}</span>
                            {param.required && <span className="text-red-400 ml-2">(required)</span>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    testEndpoint(endpoint);
                  }}
                  disabled={testing || vaultStatus !== 'online'}
                  className="px-4 py-2 bg-primary/20 hover:bg-primary/30 text-primary rounded-lg transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Play className="w-4 h-4" />
                  Test
                </button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Test Result */}
        {testResult && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-panel rounded-xl p-6 border border-primary/30"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white flex items-center gap-2">
                <Terminal className="w-5 h-5 text-primary" />
                Response
              </h3>
              <button
                onClick={() => copyToClipboard(testResult)}
                className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <Copy className="w-4 h-4 text-slate-400" />
              </button>
            </div>
            <pre className="bg-slate-900/50 rounded-lg p-4 overflow-x-auto text-sm font-mono text-slate-300 max-h-96 overflow-y-auto">
              {testResult}
            </pre>
          </motion.div>
        )}

        {/* Quick Start Guide */}
        <div className="glass-panel rounded-xl p-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-400" />
            Quick Start
          </h2>
          
          <div className="space-y-4 text-sm text-slate-400">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center text-xs font-bold">1</div>
              <div>
                <p className="text-white font-medium">Start Vault API</p>
                <code className="text-xs bg-slate-800 px-2 py-1 rounded">python scripts/start_frontend.py</code>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center text-xs font-bold">2</div>
              <div>
                <p className="text-white font-medium">Test an endpoint</p>
                <p>Click the "Test" button on any endpoint above</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center text-xs font-bold">3</div>
              <div>
                <p className="text-white font-medium">Use in your code</p>
                <code className="text-xs bg-slate-800 px-2 py-1 rounded">fetch('http://localhost:8080/api/vault/summary')</code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
