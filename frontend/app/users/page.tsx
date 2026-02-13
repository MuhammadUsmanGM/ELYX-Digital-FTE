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
  Trash2
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { fetchTeamMembers, deleteTeamMember } from "@/lib/api";
import LoadingDots from "@/components/LoadingDots";

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
    if (confirm("Are you sure you want to remove this member from the neural network?")) {
      const success = await deleteTeamMember(id);
      if (success) {
        setMembers(members.filter(m => m.id !== id));
      }
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 px-2">
          <div className="space-y-2">
            <h1 className="text-5xl font-black tracking-tighter text-white">
              Team <span className="text-primary italic">Intelligence</span>
            </h1>
            <p className="text-slate-500 font-medium max-w-xl">
              Delegate neural authority and manage access across the <span className="text-slate-300 font-bold">ELYX Neural Network</span>.
            </p>
          </div>
          <div className="flex items-center gap-4">
             <button 
               onClick={loadMembers}
               className="p-4 bg-slate-900 border border-card-border rounded-2xl text-slate-400 hover:text-primary transition-all active:scale-95"
             >
               {refreshing ? <Loader2 size={20} className="animate-spin" /> : <RefreshCw size={20} />}
             </button>
             <button className="btn-premium-primary !px-8 !py-4 shadow-[0_0_30px_rgba(6,182,212,0.2)] hover:shadow-[0_0_50px_rgba(6,182,212,0.4)] transition-all group">
               <UserPlus size={18} className="group-hover:scale-110 transition-transform" />
               Recruit New Member
             </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 p-1 bg-slate-900/50 border border-card-border/50 rounded-2xl w-fit">
           <TabButton active={activeTab === 'members'} onClick={() => setActiveTab('members')} icon={<Users size={16} />} label="Team Members" />
           <TabButton active={activeTab === 'roles'} onClick={() => setActiveTab('roles')} icon={<Shield size={16} />} label="Permissions & Roles" />
           <TabButton active={activeTab === 'access'} onClick={() => setActiveTab('access')} icon={<Key size={16} />} label="Access Controls" />
        </div>

        {/* Content Area */}
        <div className="min-h-[600px]">
          {loading ? (
            <div className="flex flex-col items-center justify-center p-40 gap-6">
              <div className="relative">
                <div className="absolute inset-0 bg-primary/20 blur-3xl animate-pulse" />
                <BrainCircuit size={64} className="text-primary animate-pulse relative" />
              </div>
              <p className="text-slate-500 font-black tracking-[0.3em] uppercase flex items-center">Syncing Team Metadata<LoadingDots /></p>
            </div>
          ) : (
            <>
              {activeTab === 'members' && (
                <div className="space-y-6 animate-in fade-in duration-500">
                   {/* Controls Bar */}
                   <div className="flex items-center justify-between px-2">
                      <div className="relative group w-80">
                         <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                         <input 
                           placeholder="Filter members..." 
                           className="w-full bg-slate-900/50 border border-card-border rounded-xl py-3 pl-11 pr-4 text-xs font-bold text-slate-300 outline-none focus:border-primary/50 transition-all"
                         />
                      </div>
                      <div className="flex items-center gap-3">
                         <button className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-card-border rounded-xl text-[10px] font-black text-slate-500 uppercase tracking-widest hover:text-white transition-all">
                            <Filter size={14} />
                            Filter
                         </button>
                         <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest border-l border-card-border pl-4 ml-1">
                            Total Capacity: <span className="text-primary">{members.length} / 10</span>
                         </p>
                      </div>
                   </div>

                   {/* Members Table-like List */}
                   <div className="glass-panel border-card-border/30 rounded-[2.5rem] overflow-hidden">
                      <table className="w-full text-left">
                         <thead className="bg-slate-900/50 border-b border-card-border/30">
                            <tr>
                               <th className="p-6 font-black text-[10px] uppercase text-slate-500 tracking-widest">Team Member</th>
                               <th className="p-6 font-black text-[10px] uppercase text-slate-500 tracking-widest">Assigned Role</th>
                               <th className="p-6 font-black text-[10px] uppercase text-slate-500 tracking-widest">Neural Status</th>
                               <th className="p-6 font-black text-[10px] uppercase text-slate-500 tracking-widest">Last Auth</th>
                               <th className="p-6 text-right"></th>
                            </tr>
                         </thead>
                         <tbody className="divide-y divide-card-border/20">
                            {members.map((member) => (
                               <tr key={member.id} className="group hover:bg-primary/[0.02] transition-all">
                                  <td className="p-6">
                                     <div className="flex items-center gap-4">
                                        <div className="relative w-11 h-11 rounded-2xl overflow-hidden border border-card-border bg-slate-800 p-0.5 group-hover:border-primary/30 transition-all">
                                           <img src={member.avatar} alt={member.name} className="w-full h-full object-cover rounded-xl" />
                                           {member.status === 'active' && (
                                             <div className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 border-2 border-slate-950 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                                           )}
                                        </div>
                                        <div>
                                           <p className="text-sm font-black text-slate-100 group-hover:text-primary transition-colors">{member.name}</p>
                                           <p className="text-[10px] text-slate-500 font-medium">{member.email}</p>
                                        </div>
                                     </div>
                                  </td>
                                  <td className="p-6">
                                     <span className="text-xs font-bold text-slate-400 group-hover:text-slate-200 transition-colors">{member.role}</span>
                                     <div className="flex gap-1 mt-1">
                                        {member.permissions?.slice(0, 2).map((p, i) => (
                                           <span key={i} className="text-[8px] font-black text-primary/60 uppercase tracking-tighter">
                                              #{p.replace('_', '-')}
                                           </span>
                                        ))}
                                     </div>
                                  </td>
                                  <td className="p-6">
                                     <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${
                                        member.status === 'active' ? 'text-emerald-500 border-emerald-500/20 bg-emerald-500/5' :
                                        member.status === 'pending' ? 'text-primary border-primary/20 bg-primary/5' :
                                        'text-slate-500 border-slate-500/20 bg-slate-500/5'
                                     }`}>
                                        {member.status}
                                     </span>
                                  </td>
                                  <td className="p-6">
                                     <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500">
                                        <Clock size={12} />
                                        {new Date(member.last_active).toLocaleDateString() === new Date().toLocaleDateString() 
                                          ? new Date(member.last_active).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                          : new Date(member.last_active).toLocaleDateString()}
                                     </div>
                                  </td>
                                  <td className="p-6 text-right">
                                     <div className="flex items-center justify-end gap-2">
                                        <button 
                                          onClick={() => handleDelete(member.id)}
                                          className="text-slate-600 hover:text-red-500 transition-colors p-2 rounded-lg hover:bg-slate-900 border border-transparent hover:border-red-500/20"
                                        >
                                           <Trash2 size={16} />
                                        </button>
                                        <button className="text-slate-600 hover:text-white transition-colors p-2 rounded-lg hover:bg-slate-900 border border-transparent hover:border-card-border">
                                           <MoreVertical size={16} />
                                        </button>
                                     </div>
                                  </td>
                               </tr>
                            ))}
                         </tbody>
                      </table>
                   </div>
                </div>
              )}

              {activeTab === 'roles' && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in duration-500">
                   {/* Left: Role Definitions */}
                   <div className="lg:col-span-8 space-y-6">
                      <div className="flex items-center justify-between mb-2">
                         <h3 className="text-xl font-black text-white flex items-center gap-3">
                            <Shield className="text-primary" size={24} />
                            Active Authority Tiers
                         </h3>
                         <button className="text-[10px] font-black text-primary uppercase tracking-widest hover:underline">Define Custom Role</button>
                      </div>
                      
                      {[
                        { title: "Master Admin", desc: "Full neural authority. Unrestricted reality anchoring and core overrides.", members: 1, icon: <ShieldAlert className="text-red-500" /> },
                        { title: "Neural Operator", desc: "Management of consciousness chains and operations workflows.", members: 2, icon: <BrainCircuit className="text-primary" /> },
                        { title: "Strategic Analyst", desc: "Read and analyze reality forecasts. Restricted from neural overrides.", members: 1, icon: <Activity className="text-emerald-500" /> }
                      ].map((role, i) => (
                        <div key={i} className="glass-panel p-8 rounded-[2.5rem] border-card-border/30 hover:border-primary/20 transition-all group">
                           <div className="flex items-center justify-between gap-6">
                              <div className="flex items-center gap-6">
                                 <div className="w-16 h-16 rounded-3xl bg-slate-900 border border-card-border flex items-center justify-center text-slate-400 group-hover:text-primary transition-colors">
                                    {role.icon}
                                 </div>
                                 <div>
                                    <h4 className="text-lg font-black text-white mb-1">{role.title}</h4>
                                    <p className="text-sm text-slate-500 font-medium max-w-lg leading-relaxed">{role.desc}</p>
                                 </div>
                              </div>
                              <div className="text-right">
                                 <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Assigned</p>
                                 <div className="flex items-center justify-end -space-x-2">
                                    {[...Array(role.members)].map((_, j) => (
                                       <div key={j} className="w-8 h-8 rounded-full border-2 border-slate-950 bg-slate-800" />
                                    ))}
                                    <div className="w-8 h-8 rounded-full border-2 border-slate-950 bg-slate-900 flex items-center justify-center text-[10px] font-black text-slate-600">
                                       +
                                    </div>
                                 </div>
                              </div>
                           </div>
                        </div>
                      ))}
                   </div>

                   {/* Right: Permission Checklist */}
                   <div className="lg:col-span-4 space-y-8">
                      <div className="glass-panel p-8 rounded-[2rem] border-card-border/30">
                         <h3 className="text-lg font-black text-white mb-6">Permission Groups</h3>
                         <div className="space-y-6">
                            <PermissionGroup 
                               label="Neural Integrity" 
                               perms={['State Override', 'Phi Synchronization', 'Introspection Flush']} 
                               active={true}
                            />
                            <PermissionGroup 
                               label="Temporal Ops" 
                               perms={['Timeline Anchoring', 'Causal Forecast', 'Sim-Reset']} 
                               active={false}
                            />
                            <PermissionGroup 
                               label="System Access" 
                               perms={['Team Recruit', 'Audit Export', 'Billing Lead']} 
                               active={false}
                            />
                         </div>
                      </div>
                   </div>
                </div>
              )}

              {activeTab === 'access' && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in duration-500">
                   <div className="lg:col-span-7 space-y-8">
                      <div className="glass-panel p-10 rounded-[3rem] border-primary/20 bg-primary/[0.01]">
                         <h3 className="text-2xl font-black text-white mb-4 flex items-center gap-3">
                            <Fingerprint className="text-primary" size={28} />
                            Global Access Directives
                         </h3>
                         <p className="text-sm text-slate-500 font-medium leading-relaxed mb-10">
                            Configure unified security protocols for all neural terminal access points.
                         </p>

                         <div className="space-y-6">
                            <AccessToggle 
                               title="Multi-Factor Neural Auth" 
                               desc="Require biometric and physical key verification for all operational logins."
                               active={true}
                            />
                            <AccessToggle 
                               title="Temporal Session Drift" 
                               desc="Automatically terminate sessions if detected access time drifts from primary continuity."
                               active={true}
                            />
                            <AccessToggle 
                               title="IP Causal Perimeter" 
                               desc="Restrict terminal access to verified geographic and causal nodes."
                               active={false}
                            />
                         </div>
                      </div>
                   </div>

                   <div className="lg:col-span-5 space-y-8">
                      <div className="glass-panel p-8 rounded-[2rem] border-card-border/30">
                         <h3 className="text-lg font-black text-white mb-6">Security Redline</h3>
                         <div className="p-6 rounded-3xl bg-red-500/5 border border-red-500/20">
                            <div className="flex items-center gap-3 mb-4">
                               <ShieldAlert className="text-red-500" size={20} />
                               <h4 className="text-sm font-black text-slate-100 uppercase tracking-tight">Panic Lock Protocol</h4>
                            </div>
                            <p className="text-[11px] text-slate-500 font-medium leading-relaxed mb-6">
                               Immediately revokes all delegated neural authorities except for the Master Admin.
                            </p>
                            <button className="w-full py-4 bg-red-500 text-white rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-white hover:text-red-500 transition-all shadow-xl shadow-red-500/10">
                               Initiate Panic Lock
                            </button>
                         </div>
                      </div>
                   </div>
                </div>
              )}
            </>
          )}
        </div>

      </div>
    </DashboardLayout>
  );
}

function TabButton({ active, onClick, icon, label }: any) {
  return (
    <button 
      onClick={onClick}
      className={`flex items-center gap-3 px-6 py-3 rounded-xl text-xs font-black uppercase tracking-widest transition-all ${
        active 
          ? 'bg-primary text-slate-950 shadow-[0_0_20px_rgba(6,182,212,0.3)]' 
          : 'text-slate-500 hover:text-slate-300'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

function PermissionGroup({ label, perms, active }: any) {
  return (
    <div className={`space-y-3 ${!active && 'opacity-60 grayscale'}`}>
       <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">{label}</h4>
       <div className="space-y-2">
          {perms.map((p: string, i: number) => (
            <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/50 border border-card-border/30">
               <span className="text-[11px] font-bold text-slate-300">{p}</span>
               <CheckCircle2 size={12} className="text-emerald-500" />
            </div>
          ))}
       </div>
    </div>
  );
}

function AccessToggle({ title, desc, active }: any) {
  return (
    <div className="flex items-start justify-between gap-8 p-6 rounded-[2rem] hover:bg-slate-900/50 transition-colors">
       <div className="space-y-1">
          <h4 className="text-md font-black text-slate-100 uppercase tracking-wide">{title}</h4>
          <p className="text-xs text-slate-500 font-medium max-w-sm leading-relaxed">{desc}</p>
       </div>
       <button className={`w-12 h-6 rounded-full relative transition-colors ${active ? 'bg-primary' : 'bg-slate-800'}`}>
          <div className={`absolute top-1 w-4 h-4 rounded-full bg-slate-950 transition-all ${active ? 'right-1' : 'left-1'}`} />
       </button>
    </div>
  );
}
