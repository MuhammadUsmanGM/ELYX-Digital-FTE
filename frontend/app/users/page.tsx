"use client";

import { useState, useEffect } from "react";
import { 
  Users, 
  UserPlus, 
  Shield, 
  Key, 
  MoreVertical, 
  Mail, 
  ShieldAlert, 
  Fingerprint,
  ChevronRight,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  Clock,
  Settings,
  UserCheck,
  Activity,
  BrainCircuit,
  Loader2,
  RefreshCw,
  Trash2,
  Sparkles,
  Crown,
  Zap,
  Eye
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { fetchTeamMembers, deleteTeamMember, createTeamMember } from "@/lib/api";
import LoadingDots from "@/components/LoadingDots";
import { motion, AnimatePresence } from "framer-motion";

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'active' | 'pending' | 'inactive';
  last_active: string;
  avatar: string;
  permissions: string[];
}

export default function UsersPage() {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'members' | 'roles' | 'access'>('members');
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [showRecruitModal, setShowRecruitModal] = useState(false);
  const [recruitName, setRecruitName] = useState("");
  const [recruitEmail, setRecruitEmail] = useState("");
  const [recruitRole, setRecruitRole] = useState("System Operator");
  const [recruiting, setRecruiting] = useState(false);

  const loadMembers = async () => {
    try {
      setRefreshing(true);
      const data = await fetchTeamMembers();
      setMembers(data);
    } catch (error) {
      console.error("Error loading team members:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadMembers();
  }, []);

  const handleDelete = async (id: string) => {
    if (confirm("Are you sure you want to remove this member from the system network?")) {
      const success = await deleteTeamMember(id);
      if (success) {
        setMembers(members.filter(m => m.id !== id));
      }
    }
  };

  const filteredMembers = members.filter(m => 
    m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.role.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <DashboardLayout>
      <div className="space-y-10">
        
        {/* Header Section */}
        <div className="flex flex-col xl:flex-row xl:items-end justify-between gap-8 px-2 relative group">
          <div className="absolute -top-20 -left-20 w-72 h-72 bg-primary/10 blur-[120px] rounded-full pointer-events-none group-hover:bg-primary/15 transition-all duration-1000" />
          <div className="space-y-3 relative z-10">
            <div className="flex items-center gap-3 mb-2">
              <span className="px-3 py-1 bg-primary/10 border border-primary/20 rounded-full text-[10px] font-black text-primary uppercase tracking-[0.2em] flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(6,182,212,1)]" />
                Team Network Active
              </span>
              <span className="text-[10px] font-black text-slate-600 uppercase tracking-[0.2em]">Capacity: {members.length}/10</span>
            </div>
            <h1 className="text-6xl font-black tracking-tighter text-white leading-none uppercase">
              Team <span className="text-primary italic relative">Management<div className="absolute -bottom-1 left-0 w-full h-1 bg-gradient-to-r from-primary to-transparent opacity-30" /></span>
            </h1>
            <p className="text-slate-500 font-bold max-w-2xl text-sm leading-relaxed">
              Delegate system authority and manage access across the <span className="text-slate-200">ELYX Business Network</span>. Currently <span className="text-accent underline underline-offset-4 decoration-accent/30">{members.filter(m => m.status === 'active').length} active</span> operators with distributed permissions.
            </p>
          </div>
          <div className="flex items-center gap-6 relative z-10 flex-wrap">
            <motion.button 
              whileHover={{ scale: 1.05, rotate: refreshing ? 0 : 180 }}
              whileTap={{ scale: 0.95 }}
              onClick={loadMembers}
              className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl text-slate-400 hover:text-primary hover:border-primary/30 transition-all flex items-center justify-center min-w-[60px] shadow-xl"
            >
              <RefreshCw size={20} className={refreshing ? 'animate-spin' : ''} />
            </motion.button>
            <motion.button 
              whileHover={{ scale: 1.02, translateY: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowRecruitModal(true)}
              className="btn-premium-primary !px-8 !py-5 shadow-2xl shadow-primary/20 border border-white/10 group"
            >
              <UserPlus size={18} className="group-hover:scale-110 transition-transform" />
              <span className="font-outfit text-xs font-black uppercase tracking-[0.2em]">Recruit Member</span>
            </motion.button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 p-1.5 bg-white/[0.03] border border-white/10 rounded-2xl w-fit shadow-2xl backdrop-blur-xl">
          <TabButton active={activeTab === 'members'} onClick={() => setActiveTab('members')} icon={<Users size={16} />} label="Team Members" />
          <TabButton active={activeTab === 'roles'} onClick={() => setActiveTab('roles')} icon={<Shield size={16} />} label="Permissions & Roles" />
          <TabButton active={activeTab === 'access'} onClick={() => setActiveTab('access')} icon={<Key size={16} />} label="Access Controls" />
        </div>

        {/* Content Area */}
        <div className="min-h-[600px]">
          {loading ? (
            <div className="flex flex-col items-center justify-center p-40 gap-8">
              <div className="relative">
                <div className="absolute inset-0 bg-primary/20 blur-3xl animate-pulse" />
                <div className="w-20 h-20 rounded-full border-t-4 border-primary animate-spin relative" />
              </div>
              <div className="space-y-2 text-center">
                <p className="text-sm font-black text-slate-400 uppercase tracking-[0.4em]">Syncing Team Metadata<LoadingDots /></p>
                <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest italic">System handshake in progress</p>
              </div>
            </div>
          ) : (
            <>
              {activeTab === 'members' && (
                <div className="space-y-8">
                  {/* Controls Bar */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 px-2">
                    <div className="relative group flex-1 max-w-md">
                      <Search size={18} className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-primary transition-colors" />
                      <input 
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search members by name, email, or role..." 
                        className="w-full bg-white/[0.03] border border-white/10 rounded-2xl py-4 pl-14 pr-6 text-sm font-bold text-slate-300 outline-none focus:border-primary/50 transition-all shadow-xl placeholder:text-slate-600"
                      />
                    </div>
                    <div className="flex items-center gap-4">
                      <motion.button 
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="flex items-center gap-3 px-6 py-4 bg-white/[0.03] border border-white/10 rounded-2xl text-[11px] font-black text-slate-400 uppercase tracking-[0.2em] hover:text-white hover:border-primary/30 transition-all shadow-xl"
                      >
                        <Filter size={16} />
                        Filter
                      </motion.button>
                      <div className="hidden sm:block text-[11px] font-black text-slate-500 uppercase tracking-[0.2em] border-l border-white/10 pl-6">
                        Total: <span className="text-primary">{filteredMembers.length}</span>
                      </div>
                    </div>
                  </div>

                  {/* Members Table */}
                  <div className="glass-panel border border-white/5 rounded-[3rem] overflow-hidden shadow-2xl">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left">
                        <thead className="bg-white/[0.02] border-b border-white/5">
                          <tr>
                            <th className="p-8 font-black text-[10px] uppercase text-slate-500 tracking-[0.3em]">Team Member</th>
                            <th className="p-8 font-black text-[10px] uppercase text-slate-500 tracking-[0.3em]">Assigned Role</th>
                            <th className="p-8 font-black text-[10px] uppercase text-slate-500 tracking-[0.3em]">Access Status</th>
                            <th className="p-8 font-black text-[10px] uppercase text-slate-500 tracking-[0.3em]">Last Access</th>
                            <th className="p-8 text-right"></th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                          <AnimatePresence mode="popLayout">
                            {filteredMembers.map((member, idx) => (
                              <motion.tr 
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                                transition={{ delay: idx * 0.05 }}
                                key={member.id} 
                                className="group hover:bg-primary/[0.03] transition-all"
                              >
                                <td className="p-8">
                                  <div className="flex items-center gap-5">
                                    <div className="relative w-14 h-14 rounded-2xl overflow-hidden border-2 border-white/10 bg-slate-900 group-hover:border-primary/40 transition-all shadow-xl">
                                      <img src={member.avatar} alt={member.name} className="w-full h-full object-cover" />
                                      {member.status === 'active' && (
                                        <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-slate-950 shadow-[0_0_12px_rgba(16,185,129,0.8)]" />
                                      )}
                                    </div>
                                    <div>
                                      <p className="text-sm font-black text-slate-100 group-hover:text-primary transition-colors mb-1">{member.name}</p>
                                      <div className="flex items-center gap-2">
                                        <Mail size={12} className="text-slate-600" />
                                        <p className="text-[11px] text-slate-500 font-medium">{member.email}</p>
                                      </div>
                                    </div>
                                  </div>
                                </td>
                                <td className="p-8">
                                  <div className="space-y-2">
                                    <span className="text-sm font-bold text-slate-300 group-hover:text-slate-100 transition-colors">{member.role}</span>
                                    <div className="flex gap-2 flex-wrap">
                                      {member.permissions?.slice(0, 2).map((p, i) => (
                                        <span key={i} className="text-[9px] font-black text-primary/60 uppercase tracking-wider bg-primary/10 px-2 py-0.5 rounded-lg border border-primary/20">
                                          {p.replace('_', '-')}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                </td>
                                <td className="p-8">
                                  <span className={`px-4 py-2 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] border ${
                                    member.status === 'active' ? 'text-emerald-500 border-emerald-500/20 bg-emerald-500/10 shadow-emerald-500/10' :
                                    member.status === 'pending' ? 'text-primary border-primary/20 bg-primary/10 shadow-primary/10' :
                                    'text-slate-500 border-slate-500/20 bg-slate-500/5'
                                  } shadow-xl`}>
                                    {member.status}
                                  </span>
                                </td>
                                <td className="p-8">
                                  <div className="flex items-center gap-2 text-[11px] font-bold text-slate-500">
                                    <Clock size={14} />
                                    {new Date(member.last_active).toLocaleDateString() === new Date().toLocaleDateString() 
                                      ? new Date(member.last_active).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                      : new Date(member.last_active).toLocaleDateString()}
                                  </div>
                                </td>
                                <td className="p-8 text-right">
                                  <div className="flex items-center justify-end gap-2">
                                    <motion.button 
                                      whileHover={{ scale: 1.1 }}
                                      whileTap={{ scale: 0.9 }}
                                      onClick={() => handleDelete(member.id)}
                                      className="text-slate-600 hover:text-red-500 transition-colors p-3 rounded-xl hover:bg-red-500/10 border border-transparent hover:border-red-500/20"
                                    >
                                      <Trash2 size={16} />
                                    </motion.button>
                                    <motion.button 
                                      whileHover={{ scale: 1.1 }}
                                      whileTap={{ scale: 0.9 }}
                                      className="text-slate-600 hover:text-white transition-colors p-3 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10"
                                    >
                                      <MoreVertical size={16} />
                                    </motion.button>
                                  </div>
                                </td>
                              </motion.tr>
                            ))}
                          </AnimatePresence>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'roles' && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                  {/* Left: Role Definitions */}
                  <div className="lg:col-span-8 space-y-8">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shadow-xl shadow-primary/5">
                          <Shield size={24} />
                        </div>
                        <h3 className="text-3xl font-black text-white tracking-tight">Authority Tiers</h3>
                      </div>
                      <motion.button 
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="text-[11px] font-black text-primary uppercase tracking-[0.2em] hover:underline px-6 py-3 bg-primary/10 border border-primary/20 rounded-2xl"
                      >
                        Define Custom Role
                      </motion.button>
                    </div>
                    
                    <div className="space-y-6">
                      {[
                        { title: "Master Admin", desc: "Full system authority. Unrestricted data anchoring and core overrides.", members: 1, icon: <Crown className="text-red-500" />, color: "red" },
                        { title: "System Operator", desc: "Management of automation workflows and operations.", members: 2, icon: <BrainCircuit className="text-primary" />, color: "primary" },
                        { title: "Strategic Analyst", desc: "Read and analyze performance reports. Restricted from core overrides.", members: 1, icon: <Activity className="text-emerald-500" />, color: "emerald" }
                      ].map((role, i) => (
                        <motion.div 
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.1 }}
                          key={i} 
                          className="glass-panel p-10 rounded-[3rem] border border-white/5 hover:border-primary/20 transition-all group shadow-2xl"
                        >
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-8">
                            <div className="flex items-center gap-6">
                              <div className="w-20 h-20 rounded-[2rem] bg-white/[0.02] border border-white/10 flex items-center justify-center text-slate-400 group-hover:scale-110 transition-transform shadow-2xl">
                                {role.icon}
                              </div>
                              <div>
                                <h4 className="text-xl font-black text-white mb-2 tracking-tight">{role.title}</h4>
                                <p className="text-sm text-slate-500 font-medium max-w-lg leading-relaxed">{role.desc}</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-3">Assigned</p>
                              <div className="flex items-center justify-end -space-x-3">
                                {[...Array(role.members)].map((_, j) => (
                                  <div key={j} className="w-10 h-10 rounded-full border-2 border-slate-950 bg-gradient-to-br from-slate-800 to-slate-900 shadow-xl" />
                                ))}
                                <motion.div 
                                  whileHover={{ scale: 1.1 }}
                                  className="w-10 h-10 rounded-full border-2 border-slate-950 bg-primary/20 flex items-center justify-center text-sm font-black text-primary cursor-pointer hover:bg-primary hover:text-white transition-all shadow-xl"
                                >
                                  +
                                </motion.div>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  {/* Right: Permission Checklist */}
                  <div className="lg:col-span-4 space-y-8">
                    <div className="glass-panel p-10 rounded-[2.5rem] border border-white/5 shadow-2xl">
                      <div className="flex items-center gap-3 mb-10">
                        <div className="w-11 h-11 rounded-2xl bg-accent/10 border border-accent/20 flex items-center justify-center text-accent shadow-xl shadow-accent/5">
                          <CheckCircle2 size={20} />
                        </div>
                        <h3 className="text-xl font-black text-white tracking-tight">Permission Groups</h3>
                      </div>
                      <div className="space-y-8">
                        <PermissionGroup 
                          label="System Integrity" 
                          perms={['State Override', 'Sync Protocol', 'Cache Flush']} 
                          active={true}
                        />
                        <PermissionGroup 
                          label="Workflow Ops" 
                          perms={['Process Anchoring', 'Security Audit', 'Task Reset']} 
                          active={false}
                        />
                        <PermissionGroup 
                          label="System Access" 
                          perms={['Team Recruitment', 'Audit Export', 'Billing Lead']} 
                          active={false}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'access' && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                  <div className="lg:col-span-7 space-y-8">
                    <div className="glass-panel p-12 rounded-[3rem] border border-white/5 shadow-2xl relative overflow-hidden group">
                      <div className="absolute inset-0 bg-gradient-to-br from-primary/[0.02] via-transparent to-accent/[0.02] pointer-events-none" />
                      <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Fingerprint size={80} className="text-primary" />
                      </div>
                      
                      <div className="relative z-10">
                        <div className="flex items-center gap-4 mb-6">
                          <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shadow-xl shadow-primary/5">
                            <Fingerprint size={28} />
                          </div>
                          <div>
                            <h3 className="text-3xl font-black text-white tracking-tight uppercase">System Access Directives</h3>
                            <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.3em]">Security Protocols</p>
                          </div>
                        </div>
                        <p className="text-sm text-slate-500 font-medium leading-relaxed mb-12">
                          Configure unified security protocols for all system terminal access points.
                        </p>

                        <div className="space-y-6">
                          <AccessToggle 
                            title="Multi-Factor System Auth" 
                            desc="Require biometric and physical key verification for all operational logins."
                            active={true}
                          />
                          <AccessToggle 
                            title="Session Timeout Protection" 
                            desc="Automatically terminate sessions after a period of inactivity."
                            active={true}
                          />
                          <AccessToggle 
                            title="IP Geofencing" 
                            desc="Restrict terminal access to verified geographic and network nodes."
                            active={false}
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="lg:col-span-5 space-y-8">
                    <div className="glass-panel p-10 rounded-[2.5rem] border border-red-500/20 bg-gradient-to-br from-red-500/[0.05] to-transparent shadow-2xl relative overflow-hidden group">
                      <div className="absolute -top-10 -right-10 w-40 h-40 bg-red-500/10 blur-[60px] rounded-full pointer-events-none group-hover:bg-red-500/15 transition-all duration-700" />
                      
                      <div className="relative z-10">
                        <div className="flex items-center gap-3 mb-8">
                          <div className="w-12 h-12 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-500 shadow-xl shadow-red-500/5">
                            <ShieldAlert size={22} />
                          </div>
                          <h3 className="text-xl font-black text-white tracking-tight">Security Redline</h3>
                        </div>
                        
                        <div className="p-8 rounded-3xl bg-red-500/10 border border-red-500/20 backdrop-blur-xl">
                          <div className="flex items-center gap-3 mb-6">
                            <ShieldAlert className="text-red-500" size={24} />
                            <h4 className="text-sm font-black text-slate-100 uppercase tracking-tight">Panic Lock Protocol</h4>
                          </div>
                          <p className="text-xs text-slate-500 font-medium leading-relaxed mb-8">
                            Immediately revokes all delegated system authorities except for the Master Admin. Use only in emergency situations.
                          </p>
                          <motion.button 
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="w-full py-5 bg-gradient-to-r from-red-600 to-red-500 text-white rounded-3xl font-black text-[11px] uppercase tracking-[0.2em] hover:from-white hover:to-white hover:text-red-500 transition-all shadow-2xl shadow-red-500/20 border border-red-400/20"
                          >
                            Initiate Panic Lock
                          </motion.button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Recruit Member Modal */}
        <AnimatePresence>
          {showRecruitModal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
              onClick={() => setShowRecruitModal(false)}
            >
              <motion.div
                initial={{ scale: 0.9, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.9, y: 20 }}
                onClick={(e) => e.stopPropagation()}
                className="glass-panel p-12 rounded-[3rem] border border-white/10 shadow-2xl max-w-2xl w-full relative overflow-hidden"
              >
                <div className="absolute -top-20 -right-20 w-64 h-64 bg-primary/10 blur-[100px] rounded-full pointer-events-none" />
                
                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shadow-xl shadow-primary/5">
                        <UserPlus size={28} />
                      </div>
                      <div>
                        <h3 className="text-3xl font-black text-white tracking-tight uppercase">Recruit Member</h3>
                        <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.3em]">Business Network Invitation</p>
                      </div>
                    </div>
                    <motion.button
                      whileHover={{ scale: 1.1, rotate: 90 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={() => setShowRecruitModal(false)}
                      className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-slate-400 hover:text-white hover:border-red-500/30 transition-all"
                    >
                      ✕
                    </motion.button>
                  </div>

                  <div className="space-y-6">
                    <div>
                      <label className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-3 block">Member Name</label>
                      <input
                        type="text"
                        placeholder="Enter full name..."
                        value={recruitName}
                        onChange={(e) => setRecruitName(e.target.value)}
                        className="w-full bg-white/[0.03] border border-white/10 rounded-2xl py-4 px-6 text-sm font-bold text-slate-300 outline-none focus:border-primary/50 transition-all"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-3 block">Email Address</label>
                      <input
                        type="email"
                        placeholder="member@elyx.ai..."
                        value={recruitEmail}
                        onChange={(e) => setRecruitEmail(e.target.value)}
                        className="w-full bg-white/[0.03] border border-white/10 rounded-2xl py-4 px-6 text-sm font-bold text-slate-300 outline-none focus:border-primary/50 transition-all"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-3 block">Authority Role</label>
                      <select
                        value={recruitRole}
                        onChange={(e) => setRecruitRole(e.target.value)}
                        className="w-full bg-white/[0.03] border border-white/10 rounded-2xl py-4 px-6 text-sm font-bold text-slate-300 outline-none focus:border-primary/50 transition-all"
                      >
                        <option>System Operator</option>
                        <option>Strategic Analyst</option>
                        <option>Master Admin</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-3 block">Invitation Message (Optional)</label>
                      <textarea
                        placeholder="Welcome to the ELYX Business Network..."
                        rows={3}
                        className="w-full bg-white/[0.03] border border-white/10 rounded-2xl py-4 px-6 text-sm font-bold text-slate-300 outline-none focus:border-primary/50 transition-all resize-none"
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-4 mt-10">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setShowRecruitModal(false)}
                      className="flex-1 py-5 bg-white/[0.03] border border-white/10 rounded-3xl text-sm font-black text-slate-400 uppercase tracking-[0.2em] hover:text-white hover:border-white/20 transition-all"
                    >
                      Cancel
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      disabled={recruiting || !recruitName.trim() || !recruitEmail.trim()}
                      onClick={async () => {
                        try {
                          setRecruiting(true);
                          await createTeamMember({ name: recruitName.trim(), email: recruitEmail.trim(), role: recruitRole });
                          setShowRecruitModal(false);
                          setRecruitName(""); setRecruitEmail(""); setRecruitRole("System Operator");
                          await loadMembers();
                        } catch (err) {
                          console.error("Failed to recruit member:", err);
                        } finally {
                          setRecruiting(false);
                        }
                      }}
                      className="flex-1 btn-premium-primary !py-5 shadow-2xl shadow-primary/20 disabled:opacity-50"
                    >
                      <span className="font-outfit text-sm font-black uppercase tracking-[0.2em]">{recruiting ? "Sending..." : "Send Invitation"}</span>
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </DashboardLayout>
  );
}

function TabButton({ active, onClick, icon, label }: any) {
  return (
    <motion.button 
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`flex items-center gap-3 px-8 py-4 rounded-xl text-[11px] font-black uppercase tracking-[0.2em] transition-all ${
        active 
          ? 'bg-gradient-to-r from-accent to-primary text-black shadow-[0_0_20px_rgba(6,182,212,0.4)]' 
          : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
      }`}
    >
      {icon}
      {label}
    </motion.button>
  );
}

function PermissionGroup({ label, perms, active }: any) {
  return (
    <div className={`space-y-4 transition-all ${!active && 'opacity-40 grayscale'}`}>
      <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">{label}</h4>
      <div className="space-y-3">
        {perms.map((p: string, i: number) => (
          <motion.div 
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
            key={i} 
            className="flex items-center justify-between p-4 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-accent/20 transition-all group"
          >
            <span className="text-xs font-bold text-slate-300 group-hover:text-slate-100 transition-colors">{p}</span>
            <CheckCircle2 size={14} className="text-emerald-500" />
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function AccessToggle({ title, desc, active }: any) {
  const [isActive, setIsActive] = useState(active);

  return (
    <div className="flex items-start justify-between gap-8 p-8 rounded-[2rem] hover:bg-white/[0.02] transition-colors border border-transparent hover:border-white/5">
      <div className="space-y-2">
        <h4 className="text-sm font-black text-slate-100 uppercase tracking-wide">{title}</h4>
        <p className="text-xs text-slate-500 font-medium max-w-sm leading-relaxed">{desc}</p>
      </div>
      <motion.button 
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsActive(!isActive)}
        className={`w-14 h-7 rounded-full relative transition-all shadow-xl ${isActive ? 'bg-primary shadow-primary/20' : 'bg-slate-800'}`}
      >
        <motion.div 
          animate={{ x: isActive ? 28 : 2 }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
          className="absolute top-1 w-5 h-5 rounded-full bg-slate-950 shadow-lg"
        />
      </motion.button>
    </div>
  );
}
