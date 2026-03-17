"use client";

import { useState, useEffect } from "react";
import {
  Search,
  HelpCircle,
  MessageSquare,
  BookOpen,
  Send,
  CheckCircle2,
  Clock,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  LifeBuoy,
  Mail,
  FileText,
  MessageCircle
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { motion } from "framer-motion";
import { toast } from "react-hot-toast";

interface FAQ {
  id: number;
  question: string;
  answer: string;
  category: 'general' | 'technical' | 'billing' | 'security';
}

interface SupportTicket {
  id: string;
  subject: string;
  status: 'open' | 'in-progress' | 'resolved';
  created: string;
  messages: { from: string; content: string; timestamp: string }[];
}

const FAQS: FAQ[] = [
  {
    id: 1,
    question: "How does ELYX handle multiple communication channels?",
    answer: "ELYX uses unified system processing to monitor and respond across WhatsApp, LinkedIn, Email, and social media simultaneously. Every interaction is context-aware and maintains your unique brand voice.",
    category: 'general'
  },
  {
    id: 2,
    question: "How do I approve or reject AI actions?",
    answer: "Go to the Approvals page (/approvals) to see all pending actions. Click 'Approve' to allow the action or 'Reject' to deny it. Approved actions are processed automatically.",
    category: 'general'
  },
  {
    id: 3,
    question: "Where can I see completed tasks?",
    answer: "Visit the Tasks page (/tasks) and filter by 'Completed' to see all finished tasks. Each task shows the results and actions taken by the AI.",
    category: 'general'
  },
  {
    id: 4,
    question: "How do I set up Gmail integration?",
    answer: "1. Create OAuth credentials in Google Cloud Console. 2. Save as gmail_credentials.json in the project root. 3. Run: python config/setup_gmail_auth.py. 4. Follow the browser authentication flow.",
    category: 'technical'
  },
  {
    id: 5,
    question: "What is the Vault API?",
    answer: "The Vault API (port 8080) provides REST endpoints to interact with your Obsidian vault. Run it with: python scripts/start_frontend.py",
    category: 'technical'
  },
  {
    id: 6,
    question: "How do I configure MCP servers?",
    answer: "Run: python scripts/setup_mcp_config.py --agent all. This configures MCP servers for Claude, Qwen, Gemini, and Codex.",
    category: 'technical'
  },
  {
    id: 7,
    question: "Is my data secure?",
    answer: "Yes. ELYX uses enterprise-grade security with local-first architecture. Your credentials never leave your machine, and all data is stored locally in your Obsidian vault.",
    category: 'security'
  },
  {
    id: 8,
    question: "Can I customize AI decision-making?",
    answer: "Yes! Edit obsidian_vault/Company_Handbook.md to set custom rules for what actions require approval, response guidelines, and business policies.",
    category: 'general'
  }
];

export default function HelpPage() {
  const [activeFaq, setActiveFaq] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [showTicketForm, setShowTicketForm] = useState(false);
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [newTicket, setNewTicket] = useState({ subject: '', message: '', email: '' });

  const filteredFaqs = FAQS.filter(faq => {
    const matchesSearch = faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         faq.answer.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || faq.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const handleSubmitTicket = (e: React.FormEvent) => {
    e.preventDefault();
    
    const ticket: SupportTicket = {
      id: `TICKET_${Date.now()}`,
      subject: newTicket.subject,
      status: 'open',
      created: new Date().toISOString(),
      messages: [
        { from: 'You', content: newTicket.message, timestamp: new Date().toISOString() }
      ]
    };
    
    setTickets([ticket, ...tickets]);
    setNewTicket({ subject: '', message: '', email: '' });
    setShowTicketForm(false);
    toast.success('Support ticket created! We\'ll respond within 24 hours.');
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 rounded-full text-primary mb-6">
            <LifeBuoy className="w-4 h-4" />
            <span className="text-xs font-bold uppercase tracking-widest">Support Center</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white mb-4">
            How can we help you?
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Search our knowledge base or submit a support ticket
          </p>
        </motion.div>

        {/* Search */}
        <div className="max-w-3xl mx-auto relative">
          <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-6 h-6 text-slate-400" />
          <input
            type="text"
            placeholder="Search for answers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-16 pr-4 py-5 bg-slate-800/50 border border-slate-700 rounded-2xl text-white placeholder:text-slate-500 focus:outline-none focus:border-primary transition-all text-lg"
          />
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <button
            onClick={() => setShowTicketForm(true)}
            className="glass-panel p-6 rounded-2xl hover:border-primary/50 transition-all group text-left"
          >
            <div className="w-12 h-12 rounded-xl bg-primary/20 text-primary flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <MessageSquare className="w-6 h-6" />
            </div>
            <h3 className="font-semibold text-white mb-2">Submit a Ticket</h3>
            <p className="text-sm text-slate-400">Get help from our support team</p>
          </button>

          <a
            href="/docs"
            className="glass-panel p-6 rounded-2xl hover:border-primary/50 transition-all group text-left"
          >
            <div className="w-12 h-12 rounded-xl bg-green-500/20 text-green-400 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <BookOpen className="w-6 h-6" />
            </div>
            <h3 className="font-semibold text-white mb-2">Documentation</h3>
            <p className="text-sm text-slate-400">Read the full documentation</p>
          </a>

          <a
            href="/api-docs"
            className="glass-panel p-6 rounded-2xl hover:border-primary/50 transition-all group text-left"
          >
            <div className="w-12 h-12 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="font-semibold text-white mb-2">API Reference</h3>
            <p className="text-sm text-slate-400">Explore the API endpoints</p>
          </a>
        </div>

        {/* FAQ Section */}
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <HelpCircle className="w-6 h-6 text-primary" />
              Frequently Asked Questions
            </h2>
            
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-slate-300 focus:outline-none focus:border-primary"
            >
              <option value="all">All Categories</option>
              <option value="general">General</option>
              <option value="technical">Technical</option>
              <option value="security">Security</option>
            </select>
          </div>

          <div className="space-y-4">
            {filteredFaqs.map((faq, index) => (
              <motion.div
                key={faq.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="glass-panel rounded-xl overflow-hidden"
              >
                <button
                  onClick={() => setActiveFaq(activeFaq === faq.id ? null : faq.id)}
                  className="w-full p-6 text-left flex items-center justify-between gap-4"
                >
                  <span className="font-semibold text-white">{faq.question}</span>
                  {activeFaq === faq.id ? (
                    <ChevronUp className="w-5 h-5 text-slate-400 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-slate-400 flex-shrink-0" />
                  )}
                </button>
                
                {activeFaq === faq.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    className="px-6 pb-6 text-slate-400"
                  >
                    <div className="pt-4 border-t border-slate-800">
                      {faq.answer}
                    </div>
                  </motion.div>
                )}
              </motion.div>
            ))}
          </div>

          {filteredFaqs.length === 0 && (
            <div className="text-center py-12">
              <Search className="w-16 h-16 mx-auto text-slate-700 mb-4" />
              <p className="text-slate-400">No results found for "{searchQuery}"</p>
            </div>
          )}
        </div>

        {/* Support Tickets */}
        {tickets.length > 0 && (
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <MessageCircle className="w-6 h-6 text-primary" />
              Your Support Tickets
            </h2>
            
            <div className="space-y-4">
              {tickets.map((ticket) => (
                <div key={ticket.id} className="glass-panel p-6 rounded-xl">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-white">{ticket.subject}</h3>
                      <p className="text-sm text-slate-500 mt-1">
                        Created: {new Date(ticket.created).toLocaleString()}
                      </p>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
                      ticket.status === 'open' ? 'bg-green-500/20 text-green-400' :
                      ticket.status === 'in-progress' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-slate-500/20 text-slate-400'
                    }`}>
                      {ticket.status}
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    {ticket.messages.map((msg, i) => (
                      <div key={i} className={`p-4 rounded-lg ${
                        msg.from === 'You' ? 'bg-primary/10 ml-8' : 'bg-slate-800 mr-8'
                      }`}>
                        <p className="text-sm text-slate-300">{msg.content}</p>
                        <p className="text-xs text-slate-500 mt-2">
                          {msg.from} • {new Date(msg.timestamp).toLocaleString()}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Ticket Form Modal */}
        {showTicketForm && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass-panel rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            >
              <div className="p-6 border-b border-slate-800 flex items-center justify-between">
                <h2 className="text-xl font-bold text-white">Submit Support Ticket</h2>
                <button
                  onClick={() => setShowTicketForm(false)}
                  className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <Send className="w-5 h-5 text-slate-400 rotate-45" />
                </button>
              </div>
              
              <form onSubmit={handleSubmitTicket} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    required
                    value={newTicket.email}
                    onChange={(e) => setNewTicket({...newTicket, email: e.target.value})}
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-primary"
                    placeholder="your@email.com"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">
                    Subject
                  </label>
                  <input
                    type="text"
                    required
                    value={newTicket.subject}
                    onChange={(e) => setNewTicket({...newTicket, subject: e.target.value})}
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-primary"
                    placeholder="Brief description of your issue"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">
                    Message
                  </label>
                  <textarea
                    required
                    value={newTicket.message}
                    onChange={(e) => setNewTicket({...newTicket, message: e.target.value})}
                    rows={6}
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-primary resize-none"
                    placeholder="Describe your issue in detail..."
                  />
                </div>
                
                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowTicketForm(false)}
                    className="flex-1 px-4 py-3 bg-slate-800 hover:bg-slate-700 rounded-xl text-white transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-3 bg-primary hover:bg-primary/80 rounded-xl text-white font-semibold transition-colors flex items-center justify-center gap-2"
                  >
                    <Send className="w-4 h-4" />
                    Submit Ticket
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
