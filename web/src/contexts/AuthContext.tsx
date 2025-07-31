import React, { createContext, useContext, useEffect, useState } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { supabase, Profile } from '@/lib/supabase'
import { useNavigate } from 'react-router-dom'

type AuthContextType = {
  user: User | null
  session: Session | null
  profile: Profile | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, fullName: string, role: 'homeowner' | 'contractor') => Promise<void>
  signOut: () => Promise<void>
  refreshProfile: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  
  // Demo mode for testing
  const DEMO_MODE = localStorage.getItem('DEMO_MODE') === 'true'

  useEffect(() => {
    // Check for demo user first
    const demoUser = localStorage.getItem('DEMO_USER')
    if (demoUser) {
      const demoData = JSON.parse(demoUser)
      setUser({ id: demoData.id, email: demoData.email } as any)
      setProfile({
        id: demoData.id,
        email: demoData.email,
        full_name: demoData.full_name,
        role: demoData.role,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      } as Profile)
      setLoading(false)
      return
    }
    
    // Check active session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      if (session?.user) {
        loadProfile(session.user.id)
      }
      setLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setSession(session)
      setUser(session?.user ?? null)
      if (session?.user) {
        await loadProfile(session.user.id)
      } else {
        setProfile(null)
      }
    })

    return () => subscription.unsubscribe()
  }, [])

  const loadProfile = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single()

      if (error) throw error
      setProfile(data)
    } catch (error) {
      console.error('Error loading profile:', error)
    }
  }

  const signIn = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) throw error
  }

  const signUp = async (
    email: string, 
    password: string, 
    fullName: string, 
    role: 'homeowner' | 'contractor'
  ) => {
    // Sign up
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email,
      password,
    })
    if (authError) throw authError

    // Create profile
    if (authData.user) {
      const { error: profileError } = await supabase
        .from('profiles')
        .insert({
          id: authData.user.id,
          full_name: fullName,
          role: role,
          email: email,
        })
      
      if (profileError) throw profileError

      // Create role-specific record
      if (role === 'homeowner') {
        const { error } = await supabase
          .from('homeowners')
          .insert({ id: authData.user.id })
        if (error) throw error
      } else {
        const { error } = await supabase
          .from('contractors')
          .insert({ 
            id: authData.user.id,
            business_name: fullName // Default to full name, can be updated later
          })
        if (error) throw error
      }
      
      // Transfer anonymous conversations to new user
      const sessionId = localStorage.getItem('cia_session_id')
      if (sessionId) {
        try {
          const response = await fetch('http://localhost:8003/api/conversations/transfer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              session_id: sessionId,
              user_id: authData.user.id
            })
          })
          const result = await response.json()
          console.log('Conversation transfer result:', result)
        } catch (error) {
          console.error('Failed to transfer conversations:', error)
        }
      }
    }
  }

  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    navigate('/')
  }

  const refreshProfile = async () => {
    if (user) {
      await loadProfile(user.id)
    }
  }

  const value = {
    user,
    session,
    profile,
    loading,
    signIn,
    signUp,
    signOut,
    refreshProfile,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}