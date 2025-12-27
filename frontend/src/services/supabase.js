import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
    console.warn('Supabase credentials not found. Auth features will be disabled.')
}

export const supabase = supabaseUrl && supabaseAnonKey
    ? createClient(supabaseUrl, supabaseAnonKey)
    : null

// Auth helper functions
export const auth = {
    // Sign in with Google
    signInWithGoogle: async () => {
        if (!supabase) return { error: 'Supabase not configured' }

        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: window.location.origin
            }
        })
        return { data, error }
    },

    // Sign in with email/password
    signInWithEmail: async (email, password) => {
        if (!supabase) return { error: 'Supabase not configured' }

        const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password
        })
        return { data, error }
    },

    // Sign up with email/password
    signUp: async (email, password, fullName) => {
        if (!supabase) return { error: 'Supabase not configured' }

        const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: { full_name: fullName }
            }
        })
        return { data, error }
    },

    // Sign out
    signOut: async () => {
        if (!supabase) return { error: 'Supabase not configured' }

        const { error } = await supabase.auth.signOut()
        return { error }
    },

    // Get current session
    getSession: async () => {
        if (!supabase) return { data: { session: null } }

        return await supabase.auth.getSession()
    },

    // Get current user
    getUser: async () => {
        if (!supabase) return { data: { user: null } }

        return await supabase.auth.getUser()
    },

    // Listen to auth changes
    onAuthStateChange: (callback) => {
        if (!supabase) return { data: { subscription: { unsubscribe: () => { } } } }

        return supabase.auth.onAuthStateChange(callback)
    }
}

export default supabase
