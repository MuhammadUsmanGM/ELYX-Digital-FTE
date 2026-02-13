"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  ShieldCheck, 
  Fingerprint, 
  Zap, 
  Mail, 
  Lock, 
  ArrowRight, 
  Loader2, 
  Github, 
  Chrome,
  AlertCircle,
  Cpu,
  User,
  CheckSquare,
  Square,
  Eye,
  EyeOff
} from "lucide-react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import Link from "next/link";
import { toast } from "react-hot-toast";

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [agreed, setAgreed] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scanVisible, setScanVisible] = useState(false);
  const router = useRouter();

  useEffect(() => {
    let isMounted = true;

    const checkUser = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session && isMounted) {
        router.push("/dashboard");
      }
    };
    checkUser();
    
    const timer = setTimeout(() => {
      if (isMounted) setScanVisible(true);
    }, 1000);

    return () => {
      isMounted = false;
      clearTimeout(timer);
    };
  }, [router]);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!isLogin) {
      const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$/;
      if (!passwordRegex.test(password)) {
        const msg = "Security key must be 8+ characters with uppercase, lowercase, numbers, and symbols.";
        setError(msg);
        toast.error(msg);
        setLoading(false);
        return;
      }
      if (password !== confirmPassword) {
        const msg = "Neural keys do not match. Please verify your security sequence.";
        setError(msg);
        toast.error(msg);
        setLoading(false);
        return;
      }
      if (!agreed) {
        const msg = "You must accept the Sovereign Intelligence Directives.";
        setError(msg);
        toast.error(msg);
        setLoading(false);
        return;
      }
    }

    try {
      if (isLogin) {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        toast.success("Authentication sequence successful. Welcome back.");
      } else {
        const { error } = await supabase.auth.signUp({ 
          email, 
          password,
          options: {
            data: {
              full_name: name,
            }
          }
        });
        if (error) throw error;
        toast.success("Verification sequence initiated. Please check your inbox.", {
          duration: 6000
        });
      }
      router.push("/dashboard");
    } catch (err: any) {
      const msg = err.message || "Neural authentication failed. Access denied.";
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const socialLogin = async (provider: 'github' | 'google') => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({ provider });
      if (error) throw error;
    } catch (err: any) {
      toast.error(`OAuth relay failed: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] flex items-center justify-center p-6 relative overflow-hidden font-sans selection:bg-primary/30">
      
      {/* Background Ambience */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary/5 blur-[150px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-emerald-500/5 blur-[150px] rounded-full" />
      </div>

      <div className="w-full max-w-[1200px] grid grid-cols-1 lg:grid-cols-2 gap-16 items-center relative z-10">
        
        {/* Left Side: Branding & Premium Visuals */}
        <motion.div 
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="hidden lg:flex flex-col space-y-12"
        >
          <Link href="/" className="flex flex-col gap-6 group w-fit">
            <div className="relative w-16 h-16 transition-transform group-hover:scale-110 duration-500">
               <div className="absolute inset-0 bg-primary/20 blur-2xl rounded-full animate-pulse" />
               <Image src="/icon.png" alt="ELYX Icon" fill className="object-contain relative z-10" />
            </div>
            <div className="relative h-8 w-32">
               <Image src="/text.png" alt="ELYX" fill className="object-contain" />
            </div>
          </Link>

          <div className="space-y-8">
            <h2 className="text-6xl font-black text-white leading-[0.9] tracking-tighter font-outfit">
              Scale Your <br />
              <span className="emerald-blue-text italic">Sovereignty.</span>
            </h2>
            <p className="text-xl text-slate-400 font-medium max-w-md leading-relaxed">
              Access the baseline for autonomous business intelligence. Zero-latency coordination for the modern sovereign entity.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-8 pt-6">
            <div className="glass-panel p-8 rounded-[2.5rem] border-white/5 relative overflow-hidden group hover:border-primary/30 transition-all duration-500">
              <div className="absolute -right-4 -top-4 w-12 h-12 bg-primary/5 rounded-full blur-xl group-hover:bg-primary/10 transition-colors" />
              <ShieldCheck className="text-primary mb-4" size={28} />
              <p className="text-xs font-black text-white uppercase tracking-[0.2em] mb-2 font-outfit">AES-256 VAULT</p>
              <p className="text-[10px] text-slate-500 font-bold leading-loose">Military-grade memory compartmentalization.</p>
            </div>
            <div className="glass-panel p-8 rounded-[2.5rem] border-white/5 relative overflow-hidden group hover:border-emerald-500/30 transition-all duration-500">
              <div className="absolute -right-4 -top-4 w-12 h-12 bg-emerald-500/5 rounded-full blur-xl group-hover:bg-emerald-500/10 transition-colors" />
              <Zap className="text-emerald-400 mb-4" size={28} />
              <p className="text-xs font-black text-white uppercase tracking-[0.2em] mb-2 font-outfit">NEURAL SYNC</p>
              <p className="text-[10px] text-slate-500 font-bold leading-loose">Synchronous causal-chain verification.</p>
            </div>
          </div>
        </motion.div>

        {/* Right Side: Professional Auth Form */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="relative max-w-xl mx-auto lg:ml-auto w-full"
        >
          <div className="absolute -inset-10 bg-primary/10 blur-[100px] rounded-full -z-10 pulse-soft" />
          
          <div className="glass-panel border-white/5 rounded-[3.5rem] p-10 md:p-14 shadow-2xl relative overflow-hidden">
            
            <AnimatePresence>
              {scanVisible && (
                <motion.div 
                  initial={{ top: "0%" }}
                  animate={{ top: "100%" }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 3.5, repeat: Infinity, ease: "linear" }}
                  className="absolute left-0 right-0 h-px bg-primary/50 shadow-[0_0_20px_rgba(6,182,212,0.6)] z-20 pointer-events-none"
                />
              )}
            </AnimatePresence>

            <div className="text-center mb-12">
               <Link href="/" className="mb-8 inline-block lg:hidden group">
                 <Image src="/icon.png" alt="ELYX" width={48} height={48} className="mx-auto transition-transform group-hover:scale-110 duration-500" />
               </Link>
               <h3 className="text-4xl font-black text-white tracking-tight mb-3 font-outfit">
                 {isLogin ? "Neural Terminal" : "Initialize Node"}
               </h3>
               <div className="inline-flex items-center gap-3 px-4 py-1.5 rounded-full bg-white/5 border border-white/10">
                 <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                 <span className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em]">Status: Awaiting Handshake</span>
               </div>
            </div>

            <form onSubmit={handleAuth} className="space-y-5">
              <AnimatePresence mode="popLayout">
                {!isLogin && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="relative group"
                  >
                    <User className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-primary transition-colors" size={18} />
                    <input 
                      type="text"
                      required
                      placeholder="FULL ENTITY NAME"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full bg-white/[0.03] border border-white/10 rounded-[1.25rem] py-4 pl-14 pr-6 text-[10px] font-bold text-white outline-none focus:border-primary/50 transition-all tracking-[0.1em] placeholder:text-slate-600 font-outfit uppercase"
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="relative group">
                <Mail className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-primary transition-colors" size={18} />
                <input 
                  type="email"
                  required
                  placeholder="AUTHORIZATION EMAIL"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-white/[0.03] border border-white/10 rounded-[1.25rem] py-4 pl-14 pr-6 text-[10px] font-bold text-white outline-none focus:border-primary/50 transition-all tracking-[0.1em] placeholder:text-slate-600 font-outfit uppercase"
                />
              </div>

              <div className="relative group">
                <Lock className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-primary transition-colors" size={18} />
                <input 
                  type={showPassword ? "text" : "password"}
                  required
                  placeholder="SECURITY KEY"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-white/[0.03] border border-white/10 rounded-[1.25rem] py-4 pl-14 pr-12 text-[10px] font-bold text-white outline-none focus:border-primary/50 transition-all tracking-[0.1em] placeholder:text-slate-600 font-outfit"
                />
                <button 
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>

              <AnimatePresence mode="popLayout">
                {!isLogin && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="space-y-5 pt-1"
                  >
                    <div className="relative group">
                      <ShieldCheck className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-primary transition-colors" size={18} />
                      <input 
                        type={showConfirmPassword ? "text" : "password"}
                        required
                        placeholder="VERIFY SECURITY KEY"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="w-full bg-white/[0.03] border border-white/10 rounded-[1.25rem] py-4 pl-14 pr-12 text-[10px] font-bold text-white outline-none focus:border-primary/50 transition-all tracking-[0.1em] placeholder:text-slate-600 font-outfit"
                      />
                      <button 
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white transition-colors"
                      >
                        {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                      </button>
                    </div>
                    
                    <button 
                      type="button"
                      onClick={() => setAgreed(!agreed)}
                      className="flex items-center gap-4 px-2 group cursor-pointer select-none"
                    >
                      <div className={`transition-all duration-300 ${agreed ? 'text-primary' : 'text-slate-600 group-hover:text-slate-400'}`}>
                         {agreed ? <CheckSquare size={20} /> : <Square size={20} />}
                      </div>
                      <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest text-left leading-relaxed font-outfit">
                        I accept the <Link href="/terms" className="text-slate-300 hover:text-primary transition-colors cursor-pointer italic underline underline-offset-4 decoration-primary/20">Neural Access Protocol</Link> and <Link href="/privacy" className="text-slate-300 hover:text-primary transition-colors cursor-pointer italic underline underline-offset-4 decoration-primary/20">Privacy Directives</Link>
                      </span>
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>

              {error && (
                <motion.div 
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-3 p-4 bg-red-500/5 border border-red-500/20 rounded-2xl text-red-400 text-[9px] font-bold uppercase tracking-widest leading-relaxed"
                >
                  <AlertCircle size={16} className="shrink-0" />
                  {error}
                </motion.div>
              )}

              <button 
                type="submit"
                disabled={loading}
                className="w-full btn-premium-primary !py-5 !rounded-2xl shadow-xl shadow-primary/10 flex items-center justify-center gap-4 group mt-4"
              >
                {loading ? (
                  <Loader2 className="animate-spin" size={20} />
                ) : (
                  <>
                    <span className="tracking-[.3em] font-outfit text-xs font-black uppercase">{isLogin ? "Synchronize" : "Create Node"}</span>
                    <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-12">
              <div className="relative flex items-center justify-center mb-10">
                <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-white/5" /></div>
                <span className="relative px-6 bg-[#020617] text-[9px] font-black text-slate-600 uppercase tracking-[0.4em]">Bridged Bridge</span>
              </div>

              <div className="grid grid-cols-2 gap-5">
                <button 
                  onClick={() => socialLogin('github')}
                  className="flex items-center justify-center gap-4 p-4 bg-white/[0.02] border border-white/5 rounded-2xl hover:bg-white/[0.05] transition-all text-slate-400 font-bold text-[10px] tracking-widest font-outfit group"
                >
                  <Github size={18} className="group-hover:text-white transition-colors" />
                  GITHUB
                </button>
                <button 
                  onClick={() => socialLogin('google')}
                  className="flex items-center justify-center gap-4 p-4 bg-white/[0.02] border border-white/5 rounded-2xl hover:bg-white/[0.05] transition-all text-slate-400 font-bold text-[10px] tracking-widest font-outfit group"
                >
                  <Chrome size={18} className="group-hover:text-white transition-colors" />
                  GOOGLE
                </button>
              </div>
            </div>

            <div className="mt-12 text-center">
              <button 
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError(null);
                }}
                className="text-[10px] font-black text-slate-500 hover:text-primary uppercase tracking-[0.3em] transition-all duration-300 font-outfit underline-offset-8 decoration-primary/30 hover:underline"
              >
                {isLogin ? "Initialize New Core Entity?" : "Return to Baseline Terminal"}
              </button>
            </div>
          </div>

          {/* Bottom Security Labels */}
          <div className="mt-10 flex items-center justify-center gap-8 text-[9px] font-black text-slate-600 uppercase tracking-[0.4em] font-outfit">
            <div className="flex items-center gap-2.5">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_#10b981]" />
              Gateway Robust
            </div>
            <div className="w-px h-4 bg-white/10" />
            <div className="flex items-center gap-2.5">
              <Fingerprint size={12} className="text-primary" />
              Diamond-v4.0
            </div>
          </div>
        </motion.div>

      </div>
    </div>
  );
}
