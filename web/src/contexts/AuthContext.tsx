import type { Session, User } from "@supabase/supabase-js";
import type React from "react";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { type Profile, supabase } from "@/lib/supabase";

type AuthContextType = {
  user: User | null;
  session: Session | null;
  profile: Profile | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (
    email: string,
    password: string,
    fullName: string,
    role: "homeowner" | "contractor"
  ) => Promise<void>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  console.log("[AuthContext] AuthProvider component initialized!");

  // MOCK AUTH - Always return test user to bypass authentication
  const mockUser = {
    id: "test-homeowner-id",
    email: "test@instabids.com",
  } as User;

  const mockProfile = {
    id: "test-homeowner-id",
    email: "test@instabids.com",
    full_name: "Test Homeowner",
    role: "homeowner",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  } as Profile;

  const [user, setUser] = useState<User | null>(mockUser);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<Profile | null>(mockProfile);
  const [loading, setLoading] = useState(false); // Never loading

  console.log("[AuthContext] Mock user setup:", { user: !!user, profile: !!profile, loading });

  const signIn = async (email: string, password: string) => {
    // Mock sign in - always succeeds
    console.log("[AuthContext] Mock sign in for:", email);
  };

  const signUp = async (
    email: string,
    password: string,
    fullName: string,
    role: "homeowner" | "contractor"
  ) => {
    // Mock sign up - always succeeds
    console.log("[AuthContext] Mock sign up for:", email, role);
  };

  const signOut = async () => {
    // Mock sign out - just log for now
    console.log("[AuthContext] Mock sign out");
    // In a real implementation, this would clear session and redirect
    // For mock purposes, we'll just log it
  };

  const refreshProfile = async () => {
    // Mock refresh - no-op
    console.log("[AuthContext] Mock refresh profile");
  };

  const value = {
    user,
    session,
    profile,
    loading,
    signIn,
    signUp,
    signOut,
    refreshProfile,
  };

  console.log("[AuthContext] Provider value:", {
    user: !!value.user,
    profile: !!value.profile,
    loading: value.loading,
  });

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
