import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, Database } from 'lucide-react'
import { api } from '../services/api'

export default function Home({ setCurrentReport, setCurrentSourceId }) {
    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState('')
    const navigate = useNavigate()

    const handleFileUpload = async () => {
        const input = document.createElement('input')
        input.type = 'file'
        input.accept = '.csv,.xlsx,.xls,.json'

        input.onchange = async (e) => {
            const file = e.target.files[0]
            if (!file) return

            setLoading(true)
            setMessage('Analyzing your data...')

            try {
                const result = await api.uploadFile(file)

                if (result.status === 'success') {
                    setMessage('✅ Analysis complete! Redirecting to dashboard...')

                    // Store the source ID
                    setCurrentSourceId(result.source_id)

                    // Get the full report
                    const reportResponse = await api.getQualityReport(result.source_id)
                    if (reportResponse.status === 'success') {
                        setCurrentReport(reportResponse.report)
                    }

                    // Navigate to dashboard after short delay
                    setTimeout(() => {
                        navigate('/dashboard')
                    }, 1000)
                }
            } catch (error) {
                setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`)
                setLoading(false)
            }
        }

        input.click()
    }

    const handleDatabaseConnect = () => {
        navigate('/connect-database')
    }

    const loadDemoData = async () => {
        setLoading(true)
        setMessage('Loading demo data...')

        try {
            const response = await api.getDemoReport()
            if (response.status === 'success') {
                setCurrentReport(response.report)
                setCurrentSourceId('demo')
                setMessage('✅ Demo loaded! Redirecting...')
                setTimeout(() => {
                    navigate('/dashboard')
                }, 500)
            }
        } catch (error) {
            setMessage(`❌ Error: ${error.message}`)
            setLoading(false)
        }
    }

    return (
        <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
            {/* Background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-black via-purple-950/20 to-black"></div>

            {/* Animated gradient orbs */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-700/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '700ms' }}></div>

            {/* Content */}
            <div className="relative z-10 w-full max-w-6xl px-6">
                {/* Hero Text */}
                <div className="text-center mb-16">
                    <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold text-white mb-6 leading-tight tracking-tight">
                        Transform Your Data
                        <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-purple-600">
                            Into Intelligence
                        </span>
                    </h1>
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                        AI-powered data preparation platform
                    </p>
                </div>

                {/* Status Message */}
                {message && (
                    <div className="mb-8 text-center">
                        <p className="text-lg text-white bg-zinc-900/80 backdrop-blur-sm border border-zinc-800 rounded-lg px-6 py-3 inline-block">
                            {loading && <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>}
                            {message}
                        </p>
                    </div>
                )}

                {/* Action Cards */}
                <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto mb-8">
                    {/* Upload File */}
                    <button
                        onClick={handleFileUpload}
                        disabled={loading}
                        className="group relative overflow-hidden rounded-2xl bg-zinc-900/50 backdrop-blur-sm border border-zinc-800 p-10 hover:border-primary-600 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-primary-600/20 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <div className="relative z-10 flex flex-col items-center text-center">
                            <div className="w-20 h-20 rounded-full bg-primary-600/10 flex items-center justify-center mb-6 group-hover:bg-primary-600/20 transition-all duration-300 group-hover:scale-110">
                                <Upload className={`w-10 h-10 text-primary-500 ${loading ? 'animate-bounce' : ''}`} />
                            </div>
                            <h2 className="text-2xl font-bold text-white mb-2">
                                {loading ? 'Analyzing...' : 'Upload File'}
                            </h2>
                            <p className="text-gray-400 text-sm">CSV, Excel, JSON</p>
                        </div>
                        <div className="absolute inset-0 bg-gradient-to-r from-primary-600/0 via-primary-600/5 to-primary-600/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    </button>

                    {/* Connect Database */}
                    <button
                        onClick={handleDatabaseConnect}
                        disabled={loading}
                        className="group relative overflow-hidden rounded-2xl bg-zinc-900/50 backdrop-blur-sm border border-zinc-800 p-10 hover:border-primary-600 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-primary-600/20 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <div className="relative z-10 flex flex-col items-center text-center">
                            <div className="w-20 h-20 rounded-full bg-primary-600/10 flex items-center justify-center mb-6 group-hover:bg-primary-600/20 transition-all duration-300 group-hover:scale-110">
                                <Database className={`w-10 h-10 text-primary-500 ${loading ? 'animate-pulse' : ''}`} />
                            </div>
                            <h2 className="text-2xl font-bold text-white mb-2">Connect Database</h2>
                            <p className="text-gray-400 text-sm">PostgreSQL, MySQL, MongoDB</p>
                        </div>
                        <div className="absolute inset-0 bg-gradient-to-r from-primary-600/0 via-primary-600/5 to-primary-600/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    </button>
                </div>

                {/* Demo Data Button */}
                <div className="text-center">
                    <button
                        onClick={loadDemoData}
                        disabled={loading}
                        className="text-gray-400 hover:text-primary-400 transition-colors underline underline-offset-4"
                    >
                        Or try with demo data →
                    </button>
                </div>
            </div>
        </div>
    )
}
