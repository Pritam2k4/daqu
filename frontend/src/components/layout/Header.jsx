import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { LogOut, User, Menu, X } from 'lucide-react'

export default function Header() {
    const { user, isAuthenticated, signOut } = useAuth()
    const [scrolled, setScrolled] = useState(false)
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
    const location = useLocation()

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 20)
        }
        window.addEventListener('scroll', handleScroll)
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    const handleSignOut = async () => {
        await signOut()
    }

    const isActive = (path) => location.pathname === path

    const navLinks = [
        { path: '/', label: 'Home' },
        { path: '/dashboard', label: 'Dashboard' },
        { path: '/model-studio', label: 'Model Studio' },
        { path: '/upload', label: 'Upload' },
    ]

    return (
        <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled
                ? 'bg-surface-dark/90 backdrop-blur-xl border-b border-white/5 py-4'
                : 'bg-transparent py-6'
            }`}>
            <div className="max-w-7xl mx-auto px-6 lg:px-8">
                <div className="flex justify-between items-center">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-3 group">
                        <div className="relative">
                            <img
                                src="/daqu-logo.png"
                                alt="DAQU"
                                className="w-10 h-10 object-contain transition-transform duration-500 group-hover:scale-110 group-hover:rotate-6"
                            />
                            <div className="absolute inset-0 bg-primary-500/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                        </div>
                        <span className="text-2xl font-display font-bold text-primary-500 tracking-tight">DAQU</span>
                    </Link>

                    {/* Desktop Navigation */}
                    {isAuthenticated && (
                        <nav className="hidden md:flex items-center gap-2">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.path}
                                    to={link.path}
                                    className={`relative px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${isActive(link.path)
                                            ? 'text-primary-500 bg-primary-500/10'
                                            : 'text-gray-400 hover:text-white hover:bg-white/5'
                                        }`}
                                >
                                    {link.label}
                                    {isActive(link.path) && (
                                        <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary-500 rounded-full"></span>
                                    )}
                                </Link>
                            ))}
                        </nav>
                    )}

                    {/* User Section */}
                    <div className="flex items-center gap-4">
                        {isAuthenticated ? (
                            <>
                                {/* User Info */}
                                <div className="hidden sm:flex items-center gap-3 px-4 py-2 glass rounded-full">
                                    {user?.user_metadata?.avatar_url ? (
                                        <img
                                            src={user.user_metadata.avatar_url}
                                            alt="Avatar"
                                            className="w-8 h-8 rounded-full ring-2 ring-primary-500/30"
                                        />
                                    ) : (
                                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-mocha-500 flex items-center justify-center">
                                            <User className="w-4 h-4 text-surface-dark" />
                                        </div>
                                    )}
                                    <span className="text-sm text-white font-medium max-w-[120px] truncate">
                                        {user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'User'}
                                    </span>
                                </div>

                                {/* Sign Out Button */}
                                <button
                                    onClick={handleSignOut}
                                    className="p-2.5 text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all duration-300"
                                    title="Sign Out"
                                >
                                    <LogOut className="w-5 h-5" />
                                </button>

                                {/* Mobile Menu Button */}
                                <button
                                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                                    className="md:hidden p-2.5 text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all"
                                >
                                    {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                                </button>
                            </>
                        ) : (
                            <Link to="/login" className="btn-primary text-sm py-2.5 px-6">
                                <span>Get Started</span>
                            </Link>
                        )}
                    </div>
                </div>

                {/* Mobile Menu */}
                {mobileMenuOpen && isAuthenticated && (
                    <nav className="md:hidden mt-4 p-4 glass rounded-2xl animate-fade-in">
                        <div className="flex flex-col gap-2">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.path}
                                    to={link.path}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={`px-4 py-3 rounded-xl text-sm font-medium transition-all ${isActive(link.path)
                                            ? 'text-primary-500 bg-primary-500/10'
                                            : 'text-gray-400 hover:text-white hover:bg-white/5'
                                        }`}
                                >
                                    {link.label}
                                </Link>
                            ))}
                        </div>
                    </nav>
                )}
            </div>
        </header>
    )
}
