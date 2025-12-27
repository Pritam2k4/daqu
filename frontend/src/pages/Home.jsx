import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, Database, Sparkles, ArrowRight, Zap, Shield, Brain, ChevronDown } from 'lucide-react'
import { api } from '../services/api'
import ScrollReveal, { ScrollRevealStagger } from '../components/ScrollReveal'
import AnimatedCounter from '../components/AnimatedCounter'

export default function Home({ setCurrentReport, setCurrentSourceId }) {
    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState('')
    const navigate = useNavigate()
    const [wordIndex, setWordIndex] = useState(0)
    const words = ['Clean', 'Analyze', 'Transform', 'Train']

    useEffect(() => {
        const interval = setInterval(() => {
            setWordIndex((prev) => (prev + 1) % words.length)
        }, 2000)
        return () => clearInterval(interval)
    }, [])

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
                    setMessage('✅ Analysis complete!')
                    setCurrentSourceId(result.source_id)
                    const reportResponse = await api.getQualityReport(result.source_id)
                    if (reportResponse.status === 'success') {
                        setCurrentReport(reportResponse.report)
                    }
                    setTimeout(() => navigate('/dashboard'), 1000)
                }
            } catch (error) {
                setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`)
                setLoading(false)
            }
        }
        input.click()
    }

    const handleDatabaseConnect = () => navigate('/connect-database')

    const loadDemoData = async () => {
        setLoading(true)
        setMessage('Loading demo data...')
        try {
            const response = await api.getDemoReport()
            if (response.status === 'success') {
                setCurrentReport(response.report)
                setCurrentSourceId('demo')
                setMessage('✅ Demo loaded!')
                setTimeout(() => navigate('/dashboard'), 500)
            }
        } catch (error) {
            setMessage(`❌ Error: ${error.message}`)
            setLoading(false)
        }
    }

    return (
        <div className="relative min-h-screen overflow-hidden">
            {/* Background Video */}
            <div className="fixed inset-0 z-0">
                <video
                    autoPlay
                    loop
                    muted
                    playsInline
                    className="absolute w-full h-full object-cover opacity-30"
                >
                    <source src="https://cdn.pixabay.com/video/2020/05/25/40130-424930941_large.mp4" type="video/mp4" />
                </video>
                <div className="absolute inset-0 bg-gradient-to-b from-surface-dark via-surface-dark/90 to-surface-dark"></div>
            </div>

            {/* Grid Background */}
            <div className="fixed inset-0 grid-bg z-[1]"></div>

            {/* Animated Orbs */}
            <div className="orb orb-gold w-[600px] h-[600px] -top-40 -right-40 opacity-40 z-[1]"></div>
            <div className="orb orb-mocha w-[500px] h-[500px] top-1/2 -left-60 opacity-30 z-[1]"></div>
            <div className="orb orb-gold w-[400px] h-[400px] bottom-20 right-1/4 opacity-20 z-[1]"></div>

            {/* HERO SECTION - Text Only Style */}
            <section className="relative z-10 min-h-screen flex flex-col items-center justify-center px-6">
                {/* Massive Hero Text */}
                <ScrollReveal delay={100}>
                    <h1 className="text-hero font-display font-bold text-center mb-6">
                        <span className="text-white">Know Your</span>
                        <br />
                        <span className="gradient-text-animated font-cyber">Data</span>
                    </h1>
                </ScrollReveal>

                {/* Animated Word Cycle */}
                <ScrollReveal delay={200}>
                    <div className="flex items-center gap-4 text-2xl md:text-3xl font-medium text-gray-400 mb-12">
                        <span>Upload.</span>
                        <span className="text-primary-500 font-bold min-w-[140px] transition-all duration-500">
                            {words[wordIndex]}.
                        </span>
                        <span>Deploy.</span>
                    </div>
                </ScrollReveal>

                {/* CTA Buttons */}
                <ScrollReveal delay={300}>
                    <div className="flex flex-col sm:flex-row gap-4 mb-16">
                        <button
                            onClick={handleFileUpload}
                            disabled={loading}
                            className="btn-primary flex items-center gap-3 group"
                        >
                            <span className="flex items-center gap-3">
                                <Upload className="w-5 h-5" />
                                Upload Data
                                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </span>
                        </button>
                        <button
                            onClick={handleDatabaseConnect}
                            disabled={loading}
                            className="btn-secondary flex items-center gap-3"
                        >
                            <Database className="w-5 h-5" />
                            Connect Database
                        </button>
                    </div>
                </ScrollReveal>

                {/* Status Message */}
                {message && (
                    <div className="mb-8 animate-fade-in">
                        <p className="text-lg text-white glass-gold rounded-2xl px-6 py-3 inline-flex items-center gap-3">
                            {loading && <span className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></span>}
                            {message}
                        </p>
                    </div>
                )}

                {/* Demo Link */}
                <ScrollReveal delay={400}>
                    <button onClick={loadDemoData} disabled={loading} className="text-gray-500 hover:text-primary-400 transition-colors">
                        or try with demo data →
                    </button>
                </ScrollReveal>
            </section>

            {/* STATS SECTION */}
            <section className="relative z-10 py-24 px-6">
                <div className="max-w-6xl mx-auto">
                    <ScrollRevealStagger staggerDelay={150}>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                            <StatCard
                                value={98.5}
                                suffix="%"
                                label="Accuracy Rate"
                                icon={<Shield className="w-6 h-6" />}
                            />
                            <StatCard
                                value={50}
                                suffix="+"
                                label="Quality Metrics"
                                icon={<Zap className="w-6 h-6" />}
                            />
                            <StatCard
                                value={10}
                                suffix="x"
                                label="Faster Prep"
                                icon={<Sparkles className="w-6 h-6" />}
                            />
                            <StatCard
                                value={15}
                                suffix="+"
                                label="ML Models"
                                icon={<Brain className="w-6 h-6" />}
                            />
                        </div>
                    </ScrollRevealStagger>
                </div>
            </section>

            {/* FEATURE BLOCKS - Vivid Contrast */}
            <section className="relative z-10 py-24 px-6">
                <div className="max-w-6xl mx-auto">
                    <ScrollReveal>
                        <h2 className="text-4xl md:text-5xl font-display font-bold text-center mb-4">
                            <span className="text-white">Enterprise-Grade</span>
                            <br />
                            <span className="gradient-text">Quality Analysis</span>
                        </h2>
                        <p className="text-gray-400 text-center max-w-2xl mx-auto mb-16">
                            Professional data quality assessment based on DAMA and ISO 25024 standards
                        </p>
                    </ScrollReveal>

                    <div className="grid md:grid-cols-2 gap-8">
                        <ScrollReveal variant="left">
                            <FeatureBlock
                                title="Smart Detection"
                                description="Automatically identify missing values, duplicates, outliers, and type mismatches across your entire dataset."
                                color="gold"
                                icon={<Zap className="w-8 h-8" />}
                            />
                        </ScrollReveal>
                        <ScrollReveal variant="right">
                            <FeatureBlock
                                title="One-Click Fixes"
                                description="Apply AI-recommended fixes instantly. Preview changes before applying and download clean data."
                                color="mocha"
                                icon={<Sparkles className="w-8 h-8" />}
                            />
                        </ScrollReveal>
                        <ScrollReveal variant="left">
                            <FeatureBlock
                                title="ML Readiness"
                                description="Class balance analysis, correlation detection, and feature engineering suggestions for optimal model training."
                                color="mocha"
                                icon={<Brain className="w-8 h-8" />}
                            />
                        </ScrollReveal>
                        <ScrollReveal variant="right">
                            <FeatureBlock
                                title="Model Training"
                                description="Train and compare 15+ ML models with automatic hyperparameter tuning and feature importance analysis."
                                color="gold"
                                icon={<Shield className="w-8 h-8" />}
                            />
                        </ScrollReveal>
                    </div>
                </div>
            </section>

            {/* CTA SECTION */}
            <section className="relative z-10 py-32 px-6">
                <div className="max-w-4xl mx-auto text-center">
                    <ScrollReveal>
                        <h2 className="text-4xl md:text-6xl font-display font-bold mb-8">
                            Ready to <span className="gradient-text">transform</span> your data?
                        </h2>
                        <button onClick={handleFileUpload} className="btn-primary text-lg group">
                            <span className="flex items-center gap-3">
                                Get Started Free
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </span>
                        </button>
                    </ScrollReveal>
                </div>
            </section>
        </div>
    )
}

// Stat Card Component
function StatCard({ value, suffix, label, icon }) {
    return (
        <div className="card text-center group">
            <div className="w-12 h-12 rounded-2xl bg-primary-500/10 flex items-center justify-center mx-auto mb-4 text-primary-500 group-hover:scale-110 transition-transform">
                {icon}
            </div>
            <div className="text-4xl font-bold text-white mb-1">
                <AnimatedCounter end={value} suffix={suffix} />
            </div>
            <div className="text-gray-500 text-sm">{label}</div>
        </div>
    )
}

// Feature Block Component  
function FeatureBlock({ title, description, color, icon }) {
    const bgColor = color === 'gold'
        ? 'bg-gradient-to-br from-primary-500/10 to-primary-600/5 border-primary-500/20'
        : 'bg-gradient-to-br from-mocha-500/10 to-mocha-600/5 border-mocha-500/20'

    const iconColor = color === 'gold' ? 'text-primary-500' : 'text-mocha-400'

    return (
        <div className={`feature-block ${bgColor} border hover-lift`}>
            <div className={`w-16 h-16 rounded-2xl bg-surface-dark/50 flex items-center justify-center mb-6 ${iconColor}`}>
                {icon}
            </div>
            <h3 className="text-2xl font-bold text-white mb-3">{title}</h3>
            <p className="text-gray-400 leading-relaxed">{description}</p>
        </div>
    )
}
