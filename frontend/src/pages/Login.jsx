import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Mail, Lock, User, ArrowRight, Sparkles, Eye, EyeOff } from 'lucide-react'
import ScrollReveal from '../components/ScrollReveal'

export default function Login() {
    const [isSignUp, setIsSignUp] = useState(false)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [fullName, setFullName] = useState('')
    const [showPassword, setShowPassword] = useState(false)
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const { signInWithGoogle, signInWithEmail, signUp } = useAuth()
    const navigate = useNavigate()

    const handleGoogleSignIn = async () => {
        setLoading(true)
        setError('')
        const { error } = await signInWithGoogle()
        if (error) {
            setError(error.message || 'Failed to sign in with Google')
        }
        setLoading(false)
    }

    const handleEmailSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        if (isSignUp) {
            const { error } = await signUp(email, password, fullName)
            if (error) {
                setError(error.message || 'Failed to sign up')
            } else {
                setError('')
                navigate('/')
            }
        } else {
            const { error } = await signInWithEmail(email, password)
            if (error) {
                setError(error.message || 'Failed to sign in')
            } else {
                navigate('/')
            }
        }
        setLoading(false)
    }

    return (
        <div className="relative min-h-screen flex items-center justify-center overflow-hidden noise-bg">
            {/* Grid Background */}
            <div className="fixed inset-0 grid-bg"></div>

            {/* Animated Orbs */}
            <div className="orb orb-gold w-[500px] h-[500px] top-1/4 right-1/3 opacity-50"></div>
            <div className="orb orb-mocha w-[400px] h-[400px] bottom-1/3 left-1/4 opacity-40"></div>

            {/* Login Card */}
            <div className="relative z-10 w-full max-w-md px-6">
                <ScrollReveal>
                    <div className="card border-white/10 p-10">
                        {/* Logo & Title */}
                        <div className="text-center mb-10">
                            <div className="flex justify-center mb-6">
                                <div className="relative">
                                    <img src="/daqu-logo.png" alt="DAQU" className="w-20 h-20" />
                                    <div className="absolute inset-0 bg-primary-500/30 rounded-full blur-2xl"></div>
                                </div>
                            </div>
                            <h1 className="text-4xl font-display font-bold mb-3">
                                {isSignUp ? (
                                    <>Join <span className="gradient-text">DAQU</span></>
                                ) : (
                                    <>Welcome <span className="gradient-text">Back</span></>
                                )}
                            </h1>
                            <p className="text-gray-500">
                                {isSignUp ? 'Create your account to get started' : 'Sign in to continue to your dashboard'}
                            </p>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-2xl text-red-400 text-sm text-center animate-fade-in">
                                {error}
                            </div>
                        )}

                        {/* Google Sign In */}
                        <button
                            onClick={handleGoogleSignIn}
                            disabled={loading}
                            className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-white text-gray-800 font-semibold rounded-2xl hover:bg-gray-50 transition-all duration-300 mb-8 disabled:opacity-50 group"
                        >
                            <svg className="w-5 h-5 group-hover:scale-110 transition-transform" viewBox="0 0 24 24">
                                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                            </svg>
                            Continue with Google
                        </button>

                        {/* Divider */}
                        <div className="relative my-8">
                            <div className="absolute inset-0 flex items-center">
                                <div className="w-full border-t border-white/10"></div>
                            </div>
                            <div className="relative flex justify-center text-sm">
                                <span className="px-4 bg-surface-card text-gray-600">or continue with email</span>
                            </div>
                        </div>

                        {/* Email Form */}
                        <form onSubmit={handleEmailSubmit} className="space-y-5">
                            {isSignUp && (
                                <div className="relative">
                                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                    <input
                                        type="text"
                                        placeholder="Full Name"
                                        value={fullName}
                                        onChange={(e) => setFullName(e.target.value)}
                                        className="input-field pl-12"
                                        required
                                    />
                                </div>
                            )}

                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                <input
                                    type="email"
                                    placeholder="Email address"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="input-field pl-12"
                                    required
                                />
                            </div>

                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    placeholder="Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="input-field pl-12 pr-12"
                                    required
                                    minLength={6}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-400"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full btn-primary flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <span className="w-5 h-5 border-2 border-surface-dark border-t-transparent rounded-full animate-spin"></span>
                                ) : (
                                    <span className="flex items-center gap-2">
                                        {isSignUp ? 'Create Account' : 'Sign In'}
                                        <ArrowRight className="w-4 h-4" />
                                    </span>
                                )}
                            </button>
                        </form>

                        {/* Toggle Sign Up / Sign In */}
                        <p className="mt-8 text-center text-gray-500 text-sm">
                            {isSignUp ? 'Already have an account?' : "Don't have an account?"}{' '}
                            <button
                                onClick={() => setIsSignUp(!isSignUp)}
                                className="text-primary-400 hover:text-primary-300 font-semibold transition-colors"
                            >
                                {isSignUp ? 'Sign In' : 'Sign Up'}
                            </button>
                        </p>
                    </div>
                </ScrollReveal>

                {/* Bottom Badge */}
                <p className="mt-8 text-center text-gray-600 text-xs flex items-center justify-center gap-2">
                    <Sparkles className="w-3 h-3 text-primary-500" />
                    Powered by DAQU AI
                </p>
            </div>
        </div>
    )
}
