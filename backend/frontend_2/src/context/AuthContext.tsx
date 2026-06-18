import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { SUPABASE_URL, SUPABASE_ANON_KEY } from "../services/api";
import type { AppUser, UserTier } from "../types";

interface AuthContextValue {
  user: AppUser | null;
  isPro: boolean;
  isDemo: boolean;
  tier: UserTier;
  planLabel: string;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<string | null>;
  signUp: (email: string, password: string) => Promise<string | null>;
  signOut: () => void;
  resetPassword: (email: string) => Promise<string | null>;
  signInWithGoogle: () => Promise<void>;
  supabase: SupabaseClient | null;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function extractTier(meta: Record<string, unknown> | undefined): UserTier {
  if (meta?.tier === "pro") return "pro";
  if (meta?.tier === "free") return "free";
  if (meta?.plan === "pro") return "pro";
  return "free";
}

function createDemoUser(): AppUser {
  return { email: "demo@nexgenweblab.com", user_metadata: { tier: "free" }, is_demo: true };
}

function mapSupabaseUser(sbUser: { email?: string | null; user_metadata?: Record<string, unknown> } | null): AppUser | null {
  if (!sbUser) return null;
  const meta = sbUser.user_metadata || {};
  return {
    email: sbUser.email || "user@nexgenweblab.com",
    user_metadata: { tier: extractTier(meta as Record<string, unknown>) },
    is_demo: false,
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AppUser | null>(null);
  const [supabase, setSupabase] = useState<SupabaseClient | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let sb: SupabaseClient | null = null;
    if (SUPABASE_URL && SUPABASE_ANON_KEY) {
      try {
        sb = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
          auth: {
            persistSession: true,
            autoRefreshToken: true,
          },
        });
        setSupabase(sb);
      } catch {
        sb = null;
      }
    }

    if (!sb) {
      setUser(createDemoUser());
      setLoading(false);
      return;
    }

    sb.auth.getUser().then((res) => {
      if (res.data?.user) {
        setUser(mapSupabaseUser(res.data.user));
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    const { data: listener } = sb.auth.onAuthStateChange((_event, session) => {
      if (session?.user) {
        setUser(mapSupabaseUser(session.user));
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    return () => listener?.subscription?.unsubscribe();
  }, []);

  const signIn = async (email: string, password: string): Promise<string | null> => {
    if (!supabase) {
      setUser(createDemoUser());
      return null;
    }
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) return error.message;
      if (data.user) setUser(mapSupabaseUser(data.user));
      return null;
    } catch {
      return "Invalid email or password.";
    }
  };

  const signUp = async (email: string, password: string): Promise<string | null> => {
    if (!supabase) return "Authentication is not configured.";
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { tier: "free" },
        },
      });
      if (error) return error.message;
      if (data.user) setUser(mapSupabaseUser(data.user));
      return null;
    } catch {
      return "Failed to create account. Please try again.";
    }
  };

  const signOut = () => {
    if (supabase) supabase.auth.signOut();
    setUser(null);
  };

  const resetPassword = async (email: string): Promise<string | null> => {
    if (!supabase) return "Authentication is not configured.";
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: 'https://tools.nexgenweblab.com/login',
      });
      if (error) return error.message;
      return null;
    } catch {
      return "Failed to send reset email. Please try again.";
    }
  };

  const signInWithGoogle = async () => {
    if (!supabase) return;
    try {
      await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: 'https://tools.nexgenweblab.com/login',
        },
      });
    } catch {
      // OAuth redirects away, so errors here are rare
    }
  };

  const currentTier: UserTier = user?.user_metadata?.tier || "free";
  const isPro = currentTier === "pro";
  const isDemo = user?.is_demo === true;
  const planLabel = isPro ? "Enterprise Pro" : "Starter";

  return (
    <AuthContext.Provider
      value={{
        user,
        isPro,
        isDemo,
        tier: currentTier,
        planLabel,
        loading,
        signIn,
        signUp,
        signOut,
        resetPassword,
        signInWithGoogle,
        supabase,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
