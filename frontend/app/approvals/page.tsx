"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { 
  Shield,
  CheckCircle2, 
  XCircle,
  AlertTriangle,
  RefreshCcw,
  FileText,
  DollarSign,
  Mail,
  User
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { toast } from "react-hot-toast";
import { fetchVaultApprovals, approveVaultTask, rejectVaultTask } from "@/lib/api";

interface Approval {
  id: string;
  filename: string;
  type: string;
  action: string;
  amount?: number;
  recipient?: string;
  reason: string;
  created: string;
  content: string;
}

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<string | null>(null);

  const loadApprovals = async () => {
    try {
      setLoading(true);
      const data = await fetchVaultApprovals();
      setApprovals(data || []);
    } catch (error) {
      console.error("Failed to load approvals:", error);
      toast.error("Failed to load approvals");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApprovals();
    const interval = setInterval(loadApprovals, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (filename: string) => {
    try {
      setProcessing(filename);
      
      const success = await approveVaultTask(filename);
      
      if (success) {
        toast.success("Task approved! Moving to processing...");
        loadApprovals();
      } else {
        toast.error("Failed to approve task");
      }
    } catch (error) {
      console.error("Approval error:", error);
      toast.error("Failed to approve task");
    } finally {
      setProcessing(null);
    }
  };

  const handleReject = async (filename: string) => {
    try {
      setProcessing(filename);
      
      const success = await rejectVaultTask(filename);
      
      if (success) {
        toast.success("Task rejected");
        loadApprovals();
      } else {
        toast.error("Failed to reject task");
      }
    } catch (error) {
      console.error("Rejection error:", error);
      toast.error("Failed to reject task");
    } finally {
      setProcessing(null);
    }
  };

  const getActionIcon = (action: string) => {
    if (action.includes("payment") || action.includes("money")) {
      return <DollarSign className="w-6 h-6 text-green-400" />;
    }
    if (action.includes("email")) {
      return <Mail className="w-6 h-6 text-blue-400" />;
    }
    if (action.includes("contact") || action.includes("user")) {
      return <User className="w-6 h-6 text-purple-400" />;
    }
    return <FileText className="w-6 h-6 text-slate-400" />;
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <div className="flex items-center gap-3">
              <Shield className="w-8 h-8 text-primary" />
              <h1 className="text-3xl font-bold text-white">Approvals Required</h1>
            </div>
            <p className="text-slate-400 mt-1">
              Review and approve sensitive actions
            </p>
          </div>
          
          <button
            onClick={loadApprovals}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition-all"
          >
            <RefreshCcw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="glass-panel p-6 rounded-xl">
            <div className="flex items-center gap-3 mb-2">
              <AlertTriangle className="w-5 h-5 text-yellow-400" />
              <span className="text-slate-400 text-sm">Pending</span>
            </div>
            <p className="text-3xl font-bold text-white">{approvals.length}</p>
          </div>
          
          <div className="glass-panel p-6 rounded-xl">
            <div className="flex items-center gap-3 mb-2">
              <DollarSign className="w-5 h-5 text-green-400" />
              <span className="text-slate-400 text-sm">Financial</span>
            </div>
            <p className="text-3xl font-bold text-white">
              {approvals.filter(a => a.action.includes("payment")).length}
            </p>
          </div>
          
          <div className="glass-panel p-6 rounded-xl">
            <div className="flex items-center gap-3 mb-2">
              <Mail className="w-5 h-5 text-blue-400" />
              <span className="text-slate-400 text-sm">Communications</span>
            </div>
            <p className="text-3xl font-bold text-white">
              {approvals.filter(a => a.action.includes("email") || a.action.includes("message")).length}
            </p>
          </div>
        </div>

        {/* Approvals List */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <RefreshCcw className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : approvals.length === 0 ? (
          <div className="text-center py-20">
            <Shield className="w-16 h-16 mx-auto text-slate-700 mb-4" />
            <p className="text-slate-400">No pending approvals</p>
            <p className="text-slate-500 text-sm mt-2">
              All actions are either auto-approved or already processed
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {approvals.map((approval, index) => (
              <motion.div
                key={approval.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="glass-panel p-6 rounded-xl border-l-4 border-l-yellow-500"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="p-3 bg-slate-800 rounded-xl">
                      {getActionIcon(approval.action)}
                    </div>
                    
                    <div className="flex-1">
                      <h3 className="font-semibold text-white mb-2">
                        {approval.action}
                      </h3>
                      
                      <p className="text-slate-400 text-sm mb-3">
                        {approval.reason}
                      </p>
                      
                      <div className="flex items-center gap-4 text-sm text-slate-500">
                        {approval.recipient && (
                          <span className="flex items-center gap-1">
                            <User className="w-3 h-3" />
                            {approval.recipient}
                          </span>
                        )}
                        {approval.amount && (
                          <span className="flex items-center gap-1">
                            <DollarSign className="w-3 h-3" />
                            ${approval.amount}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <FileText className="w-3 h-3" />
                          {new Date(approval.created).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleReject(approval.filename)}
                      disabled={processing === approval.filename}
                      className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <XCircle className="w-4 h-4" />
                      Reject
                    </button>
                    <button
                      onClick={() => handleApprove(approval.filename)}
                      disabled={processing === approval.filename}
                      className="px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      Approve
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
