"use client";

import { useEffect, useState } from "react";
import { 
  Mail, 
  MessageCircle, 
  MessageSquare,
  Send, 
  Search,
  MoreVertical,
  Loader2,
  Trash2,
  CheckCircle,
  Hash,
  Twitter,
  AtSign,
  Smile,
  Paperclip,
  Activity
} from "lucide-react";
import { fetchCommunications, sendMessage } from "@/lib/api";
import { Communication, Message } from "@/lib/types";
import DashboardLayout from "@/components/DashboardLayout";
import LoadingDots from "@/components/LoadingDots";

export default function CommunicationsPage() {
  const [comms, setComms] = useState<Communication[]>([]);
  const [selectedComm, setSelectedComm] = useState<Communication | null>(null);
  const [loading, setLoading] = useState(true);
  const [replyText, setReplyText] = useState("");
  const [sending, setSending] = useState(false);

  const handleSendMessage = async () => {
    if (!replyText.trim() || !selectedComm || sending) return;

    setSending(true);
    const result = await sendMessage(
      selectedComm.id,
      selectedComm.platform,
      selectedComm.contact_identifier,
      replyText.trim(),
    );

    if (result.success) {
      const newMsg: Message = {
        id: `msg_${Date.now()}`,
        sender: "ELYX",
        content: replyText.trim(),
        timestamp: new Date().toISOString(),
        is_ai: true,
      };

      const updatedComm = {
        ...selectedComm,
        history: [...selectedComm.history, newMsg],
        last_message: replyText.trim(),
        last_timestamp: new Date().toISOString(),
      };

      setComms((prev) => prev.map((c) => (c.id === updatedComm.id ? updatedComm : c)));
      setSelectedComm(updatedComm);
      setReplyText("");
    } else {
      console.error("Send failed:", result.error);
    }
    setSending(false);
  };

  const loadData = async () => {
    try {
      setLoading(true);
      const fetchedComms = await fetchCommunications();
      setComms(fetchedComms);
      if (fetchedComms.length > 0) {
        setSelectedComm(fetchedComms[0]);
      }
    } catch (error) {
      console.error("Communications load error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'email': return <Mail size={18} className="text-primary" />;
      case 'whatsapp': return <MessageCircle size={18} className="text-emerald-500" />;
      case 'twitter': return <Twitter size={18} className="text-sky-500" />;
      case 'linkedin': return <Hash size={18} className="text-blue-500" />;
      case 'facebook': return <MessageSquare size={18} className="text-blue-400" />;
      case 'instagram': return <AtSign size={18} className="text-pink-500" />;
      default: return <AtSign size={18} className="text-slate-400" />;
    }
  };

  return (
    <DashboardLayout>
      <div className="h-[calc(100vh-140px)] flex flex-col animate-in fade-in duration-500">
        <div className="flex items-end justify-between mb-6">
          <div>
            <h1 className="text-4xl font-black tracking-tight mb-2">Communication Hub</h1>
            <p className="text-slate-400 font-medium">Unified AI interaction management across all platforms.</p>
          </div>
          <div className="flex items-center gap-4 bg-slate-900/50 border border-card-border rounded-xl px-4 py-2 w-64">
            <Search size={16} className="text-slate-500" />
            <input 
              type="text" 
              placeholder="Search messages..." 
              className="bg-transparent border-none outline-none text-sm text-slate-300 w-full"
            />
          </div>
        </div>

        <div className="flex-1 flex gap-6 min-h-0">
          {/* Sidebar - Conversations List */}
          <div className="w-80 flex flex-col gap-4 overflow-y-auto pr-2 custom-scrollbar">
            {loading ? (
              <div className="flex flex-col items-center justify-center p-20 gap-4 glass-panel rounded-2xl">
                <Loader2 size={32} className="text-primary animate-spin" />
              </div>
            ) : comms.map((comm) => (
              <div 
                key={comm.id}
                onClick={() => setSelectedComm(comm)}
                className={`glass-panel p-4 rounded-xl cursor-pointer transition-all relative ${
                  selectedComm?.id === comm.id 
                    ? 'border-primary bg-primary/5' 
                    : 'hover:border-primary/30'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="relative">
                    <div className="w-12 h-12 rounded-full bg-slate-800 border border-card-border flex items-center justify-center font-bold text-lg text-slate-300">
                      {comm.contact_name.charAt(0)}
                    </div>
                    <div className="absolute -bottom-1 -right-1 p-1 bg-[#020617] rounded-full border border-card-border">
                      {getPlatformIcon(comm.platform)}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-bold text-slate-200 truncate">{comm.contact_name}</h4>
                      <span className="text-[10px] text-slate-500 font-bold uppercase">
                        {new Date(comm.last_timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 truncate">{comm.last_message}</p>
                  </div>
                </div>
                {comm.unread_count > 0 && (
                  <div className="absolute top-2 right-2 w-5 h-5 bg-primary text-slate-950 text-[10px] font-black rounded-full flex items-center justify-center border-2 border-[#020617]">
                    {comm.unread_count}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Chat Area */}
          <div className="flex-1 glass-panel rounded-3xl flex flex-col min-w-0 border-card-border/50 relative overflow-hidden">
            {selectedComm ? (
              <>
                {/* Chat Header */}
                <div className="p-6 border-b border-card-border bg-slate-900/20 backdrop-blur-md flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-slate-800 border border-card-border flex items-center justify-center font-bold text-slate-200">
                      {selectedComm.contact_name.charAt(0)}
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-200">{selectedComm.contact_name}</h3>
                      <div className="flex items-center gap-2">
                         <span className="text-xs text-slate-500">{selectedComm.contact_identifier}</span>
                         <span className="w-1 h-1 rounded-full bg-slate-700" />
                         <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-tighter">
                           Sentiment: {(selectedComm.sentiment_score * 100).toFixed(0)}% Positive
                         </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button className="p-2 text-slate-500 hover:text-white transition-colors">
                      <Activity size={18} />
                    </button>
                    <button className="p-2 text-slate-500 hover:text-white transition-colors">
                      <MoreVertical size={18} />
                    </button>
                  </div>
                </div>

                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-8 space-y-6 custom-scrollbar">
                  {selectedComm.history.map((msg) => (
                    <div 
                      key={msg.id} 
                      className={`flex ${msg.is_ai ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[70%] group relative ${msg.is_ai ? 'items-end' : 'items-start'} flex flex-col`}>
                        <div className={`px-5 py-3 rounded-2xl text-sm leading-relaxed shadow-xl ${
                          msg.is_ai 
                            ? 'bg-primary text-slate-950 font-medium rounded-tr-none' 
                            : 'bg-slate-800/80 border border-card-border text-slate-200 rounded-tl-none'
                        }`}>
                          {msg.content}
                        </div>
                        <span className="text-[9px] font-bold text-slate-600 mt-2 uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">
                          {new Date(msg.timestamp).toLocaleTimeString()}
                          {msg.is_ai && " • Generated by ELYX"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Reply Area */}
                <div className="p-6 border-t border-card-border bg-[#020617]/50">
                  <div className="glass-panel p-2 rounded-2xl flex items-end gap-2 bg-slate-900/50">
                    <button className="p-2 text-slate-500 hover:text-primary transition-colors">
                      <Smile size={20} />
                    </button>
                    <button className="p-2 text-slate-500 hover:text-primary transition-colors">
                      <Paperclip size={20} />
                    </button>
                    <textarea
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                      placeholder={`Reply to ${selectedComm.contact_name} as ELYX...`}
                      className="flex-1 bg-transparent border-none outline-none text-sm text-slate-300 py-2 resize-none h-10 max-h-32"
                      disabled={sending}
                    />
                    <button
                      onClick={handleSendMessage}
                      disabled={sending || !replyText.trim()}
                      className="p-3 bg-primary text-slate-950 rounded-xl font-bold hover:bg-white transition-all shadow-lg shadow-primary/10 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      {sending ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                    </button>
                  </div>
                  <div className="mt-3 flex items-center justify-between px-2">
                     <p className="text-[10px] text-slate-600 font-bold uppercase tracking-tighter flex items-center">
                       ELYX is drafting a suggested response in the background
                       <LoadingDots />
                     </p>
                     <div className="flex items-center gap-1">
                       <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                       <span className="text-[10px] font-black text-primary uppercase">AI Logic Active</span>
                     </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center p-20 text-center">
                <div className="w-20 h-20 rounded-full bg-slate-900 border border-card-border flex items-center justify-center mb-6 opacity-20">
                  <MessageSquare size={40} className="text-slate-400" />
                </div>
                <h3 className="text-xl font-bold text-slate-500">Select a connection</h3>
                <p className="text-slate-600 text-sm max-w-xs">ELYX is monitoring WhatsApp, Email, and Slack for new interactions.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
