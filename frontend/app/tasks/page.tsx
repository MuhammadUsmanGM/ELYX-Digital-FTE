"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { 
  Inbox, 
  CheckCircle, 
  XCircle, 
  Clock, 
  RefreshCcw,
  FileText,
  Mail,
  MessageCircle,
  Linkedin,
  Twitter,
  Facebook,
  Instagram,
  AlertCircle,
  CheckCircle2,
  X
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { toast } from "react-hot-toast";
import { fetchVaultTasks } from "@/lib/api";

interface Task {
  id: string;
  filename: string;
  type: string;
  priority: string;
  status: string;
  from: string;
  subject: string;
  created: string;
  content: string;
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const [needsAction, completed] = await Promise.all([
        fetchVaultTasks("Needs_Action"),
        fetchVaultTasks("Done")
      ]);
      
      const allTasks = [
        ...needsAction.map((t: any) => ({ ...t, status: "pending" })),
        ...completed.map((t: any) => ({ ...t, status: "completed" }))
      ];
      
      setTasks(allTasks);
    } catch (error) {
      console.error("Failed to load tasks:", error);
      toast.error("Failed to load tasks. Is Vault API running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
    const interval = setInterval(loadTasks, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const filteredTasks = tasks.filter(task => {
    if (filter === "pending") return task.status === "pending";
    if (filter === "completed") return task.status === "completed";
    return true;
  });

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "email": return <Mail className="w-4 h-4" />;
      case "whatsapp": return <MessageCircle className="w-4 h-4" />;
      case "linkedin": return <Linkedin className="w-4 h-4" />;
      case "twitter": return <Twitter className="w-4 h-4" />;
      case "facebook": return <Facebook className="w-4 h-4" />;
      case "instagram": return <Instagram className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return "bg-red-500/20 text-red-400 border-red-500/30";
      case "critical": return "bg-red-500/30 text-red-300 border-red-500/50";
      case "medium": return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
      default: return "bg-blue-500/20 text-blue-400 border-blue-500/30";
    }
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
            <h1 className="text-3xl font-bold text-white">Tasks</h1>
            <p className="text-slate-400 mt-1">Manage AI employee tasks and approvals</p>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={loadTasks}
              className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition-all"
            >
              <RefreshCcw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </motion.div>

        {/* Filter Tabs */}
        <div className="flex gap-2 border-b border-slate-800">
          <button
            onClick={() => setFilter("all")}
            className={`px-4 py-2 text-sm font-medium transition-all ${
              filter === "all"
                ? "text-primary border-b-2 border-primary"
                : "text-slate-400 hover:text-slate-300"
            }`}
          >
            All Tasks ({tasks.length})
          </button>
          <button
            onClick={() => setFilter("pending")}
            className={`px-4 py-2 text-sm font-medium transition-all ${
              filter === "pending"
                ? "text-primary border-b-2 border-primary"
                : "text-slate-400 hover:text-slate-300"
            }`}
          >
            <Clock className="w-4 h-4 inline mr-1" />
            Pending ({tasks.filter(t => t.status === "pending").length})
          </button>
          <button
            onClick={() => setFilter("completed")}
            className={`px-4 py-2 text-sm font-medium transition-all ${
              filter === "completed"
                ? "text-primary border-b-2 border-primary"
                : "text-slate-400 hover:text-slate-300"
            }`}
          >
            <CheckCircle className="w-4 h-4 inline mr-1" />
            Completed ({tasks.filter(t => t.status === "completed").length})
          </button>
        </div>

        {/* Tasks Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <RefreshCcw className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-20">
            <Inbox className="w-16 h-16 mx-auto text-slate-700 mb-4" />
            <p className="text-slate-400">No tasks found</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {filteredTasks.map((task, index) => (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => setSelectedTask(task)}
                className="glass-panel p-4 rounded-xl cursor-pointer hover:border-primary/50 transition-all group"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={`p-2 rounded-lg ${
                      task.status === "completed" 
                        ? "bg-green-500/20 text-green-400" 
                        : "bg-primary/20 text-primary"
                    }`}>
                      {task.status === "completed" ? (
                        <CheckCircle2 className="w-5 h-5" />
                      ) : (
                        <Clock className="w-5 h-5" />
                      )}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {getTypeIcon(task.type)}
                        <h3 className="font-semibold text-white">{task.subject || "No Subject"}</h3>
                      </div>
                      
                      <p className="text-sm text-slate-400 mb-2">
                        From: {task.from || "Unknown"}
                      </p>
                      
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded text-xs border ${getPriorityColor(task.priority)}`}>
                          {task.priority}
                        </span>
                        <span className="text-xs text-slate-500">
                          {new Date(task.created).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {task.status === "pending" && (
                      <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded text-xs">
                        Needs Action
                      </span>
                    )}
                    {task.status === "completed" && (
                      <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">
                        Done
                      </span>
                    )}
                    <ChevronRight className="w-5 h-5 text-slate-600 group-hover:text-primary transition-colors" />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Task Detail Modal */}
        {selectedTask && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass-panel rounded-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden"
            >
              <div className="p-6 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-white">{selectedTask.subject}</h2>
                  <p className="text-sm text-slate-400 mt-1">
                    {selectedTask.type} • {selectedTask.from}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedTask(null)}
                  className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-slate-400" />
                </button>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                <pre className="whitespace-pre-wrap text-slate-300 text-sm font-mono">
                  {selectedTask.content}
                </pre>
              </div>
              
              <div className="p-6 border-t border-slate-800 flex justify-end gap-3">
                <button
                  onClick={() => setSelectedTask(null)}
                  className="px-4 py-2 text-slate-400 hover:text-white transition-colors"
                >
                  Close
                </button>
                {selectedTask.status === "pending" && (
                  <>
                    <button
                      onClick={async () => {
                        // TODO: Implement reject
                        toast.error("Reject functionality coming soon");
                      }}
                      className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-all flex items-center gap-2"
                    >
                      <XCircle className="w-4 h-4" />
                      Reject
                    </button>
                    <button
                      onClick={async () => {
                        // TODO: Implement approve
                        toast.error("Approve functionality coming soon");
                      }}
                      className="px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-all flex items-center gap-2"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Process
                    </button>
                  </>
                )}
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
