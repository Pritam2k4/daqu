import { createContext, useContext, useState, useEffect } from 'react'
import { auth } from '../services/supabase'

const AuthContext = createContext({})

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [session, setSession] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        // Get initial session
        auth.getSession().then(({ data: { session } }) => {
            setSession(session)
            setUser(session?.user ?? null)
            setLoading(false)
        })

        // Listen for auth changes
        const { data: { subscription } } = auth.onAuthStateChange((_event, session) => {
            setSession(session)
            setUser(session?.user ?? null)
            setLoading(false)
        })

        return () => subscription.unsubscribe()
    }, [])

    const signInWithGoogle = async () => {
        setLoading(true)
        const result = await auth.signInWithGoogle()
        setLoading(false)
        return result
    }

    const signInWithEmail = async (email, password) => {
        setLoading(true)
        const result = await auth.signInWithEmail(email, password)
        setLoading(false)
        return result
    }

    const signUp = async (email, password, fullName) => {
        setLoading(true)
        const result = await auth.signUp(email, password, fullName)
        setLoading(false)
        return result
    }

    const signOut = async () => {
        setLoading(true)
        const result = await auth.signOut()
        setUser(null)
        setSession(null)
        setLoading(false)
        return result
    }

    const value = {
        user,
        session,
        loading,
        signInWithGoogle,
        signInWithEmail,
        signUp,
        signOut,
        isAuthenticated: !!user
    }

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}

export default AuthContext
