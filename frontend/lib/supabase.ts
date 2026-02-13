import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase credentials missing. Auth will fallback to demonstration mode.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
    storage: {
      getItem: (key) => {
        if (typeof document === 'undefined') return null;
        const cookie = document.cookie.split('; ').find(row => row.trim().startsWith(`${key}=`));
        if (cookie) return decodeURIComponent(cookie.split('=')[1]);
        return localStorage.getItem(key);
      },
      setItem: (key, value) => {
        if (typeof document === 'undefined') return;
        document.cookie = `${key}=${encodeURIComponent(value)}; path=/; max-age=31536000; SameSite=Lax`;
        localStorage.setItem(key, value);
      },
      removeItem: (key) => {
        if (typeof document === 'undefined') return;
        document.cookie = `${key}=; path=/; max-age=0`;
        localStorage.removeItem(key);
      },
    },
  },
});
