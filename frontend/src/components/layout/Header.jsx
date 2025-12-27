import { Link } from 'react-router-dom'
import { Database } from 'lucide-react'

export default function Header() {
    return (
        <header className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-md border-b border-zinc-800">
            <div className="max-w-7xl mx-auto px-6 lg:px-8">
                <div className="flex justify-between items-center h-20">
                    {/* Logo - Far Left */}
                    <Link to="/" className="flex items-center space-x-3 group">
                        <Database className="w-8 h-8 text-primary-500 group-hover:text-primary-400 transition-colors" />
                        <span className="text-xl font-bold text-white">DataReady AI</span>
                    </Link>

                    {/* Center Navigation - Minimal */}
                    <nav className="hidden md:flex space-x-10">
                        <Link to="/" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
                            Home
                        </Link>
                        <Link to="/dashboard" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
                            Dashboard
                        </Link>
                        <Link to="/model-studio" className="text-gray-400 hover:text-white transition-colors text-sm font-medium flex items-center gap-1">
                            Model Studio
                        </Link>
                        <Link to="/upload" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
                            Upload
                        </Link>
                    </nav>

                    {/* Sign In - Far Right */}
                    <button className="btn-primary">
                        Get Started
                    </button>
                </div>
            </div>
        </header>
    )
}
