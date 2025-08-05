import type { Session, User } from "@supabase/supabase-js";
import type React from "react";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
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
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Demo mode for testing
  const _DEMO_MODE = localStorage.getItem("DEMO_MODE") === "true";

  const loadProfile = useCallback(
    async (userId: string) => {
      try {
        console.log("[AuthContext] Loading profile for user:", userId);

        // Use the backend API endpoint instead of direct Supabase
        const response = await fetch(`http://localhost:8008/profiles/${userId}`);

        if (!response.ok) {
          console.error("[AuthContext] Profile API error:", response.status, response.statusText);

          // If 404, create basic profile from user data
          if (response.status === 404) {
            console.log("[AuthContext] Profile not found, creating basic profile");

            // Check for demo user role
            const demoUser = localStorage.getItem("DEMO_USER");
            let defaultRole = "homeowner";
            if (demoUser) {
              const demoData = JSON.parse(demoUser);
              defaultRole = demoData.role || "homeowner";
            }

            setProfile({
              id: userId,
              email: user?.email || "",
              full_name: "",
              role: defaultRole,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            } as Profile);
            return;
          }

          throw new Error(`API error: ${response.status}`);
        }

        const profileData = await response.json();
        console.log("[AuthContext] Profile loaded from API:", profileData);
        setProfile(profileData);
      } catch (error) {
        console.error("[AuthContext] Error loading profile:", error);

        // Fallback to basic profile on any error
        console.log("[AuthContext] Using fallback basic profile");

        // Check for demo user role in fallback as well
        const demoUser = localStorage.getItem("DEMO_USER");
        let fallbackRole = "homeowner";
        if (demoUser) {
          const demoData = JSON.parse(demoUser);
          fallbackRole = demoData.role || "homeowner";
        }

        setProfile({
          id: userId,
          email: user?.email || "",
          full_name: "",
          role: fallbackRole,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        } as Profile);
      }
    },
    [user?.email]
  );

  useEffect(() => {
    // Check for demo user first
    const demoUser = localStorage.getItem("DEMO_USER");
    if (demoUser) {
      const demoData = JSON.parse(demoUser);
      setUser({ id: demoData.id, email: demoData.email } as any);
      setProfile({
        id: demoData.id,
        email: demoData.email,
        full_name: demoData.full_name,
        role: demoData.role,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      } as Profile);
      setLoading(false);
      return;
    }

    // Check active session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      if (session?.user) {
        loadProfile(session.user.id);
      }
      setLoading(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      if (session?.user) {
        await loadProfile(session.user.id);
      } else {
        setProfile(null);
      }
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, [loadProfile]);

  const signIn = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw error;
  };

  const signUp = async (
    email: string,
    password: string,
    fullName: string,
    role: "homeowner" | "contractor"
  ) => {
    // Sign up
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email,
      password,
    });
    if (authError) throw authError;

    // Create profile
    if (authData.user) {
      const { error: profileError } = await supabase.from("profiles").insert({
        id: authData.user.id,
        full_name: fullName,
        role: role,
        email: email,
      });

      if (profileError) throw profileError;

      // Create role-specific record
      if (role === "homeowner") {
        const { error } = await supabase.from("homeowners").insert({ id: authData.user.id });
        if (error) throw error;
      } else {
        // Check if there's an existing contractor_leads record with this email
        const { data: existingLead } = await supabase
          .from("contractor_leads")
          .select("*")
          .eq("email", email)
          .eq("lead_status", "qualified")
          .single();

        let contractorData = {
          id: authData.user.id,
          business_name: fullName,
        };

        // If we found a matching contractor lead from AI research, use that data
        if (existingLead) {
          console.log("Found existing contractor lead, linking account:", existingLead.id);
          contractorData = {
            id: authData.user.id,
            business_name: existingLead.company_name || fullName,
            email: existingLead.email,
            phone: existingLead.phone,
            website: existingLead.website,
          };

          // Update the contractor_leads record to link it to the auth user
          await supabase
            .from("contractor_leads")
            .update({
              raw_data: {
                ...existingLead.raw_data,
                auth_user_id: authData.user.id,
                account_linked: true,
                linked_at: new Date().toISOString(),
              },
            })
            .eq("id", existingLead.id);
        }

        const { error } = await supabase.from("contractors").insert(contractorData);
        if (error) throw error;
      }

      // Transfer anonymous conversations to new user
      const sessionId = localStorage.getItem("cia_session_id");
      if (sessionId) {
        try {
          const response = await fetch("http://localhost:8008/conversations/transfer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              session_id: sessionId,
              user_id: authData.user.id,
            }),
          });
          const result = await response.json();
          console.log("Conversation transfer result:", result);
        } catch (error) {
          console.error("Failed to transfer conversations:", error);
        }
      }
    }
  };

  const signOut = async () => {
    // Clear demo user data
    localStorage.removeItem("DEMO_USER");

    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    navigate("/");
  };

  const refreshProfile = async () => {
    if (user) {
      await loadProfile(user.id);
    }
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

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
