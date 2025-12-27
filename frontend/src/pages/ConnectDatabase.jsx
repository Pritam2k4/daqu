import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Database, Server, Key, ArrowLeft, Check, AlertCircle,
    Table, ChevronRight, Loader2, Eye, EyeOff
} from 'lucide-react'
import { api } from '../services/api'

export default function ConnectDatabase({ setCurrentReport, setCurrentSourceId }) {
    const [step, setStep] = useState(1) // 1: config, 2: tables, 3: analyzing
    const [dbType, setDbType] = useState('postgresql')
    const [config, setConfig] = useState({
        host: 'localhost',
        port: '',
        database: '',
        username: '',
        password: ''
    })
    const [showPassword, setShowPassword] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [tables, setTables] = useState([])
    const [selectedTable, setSelectedTable] = useState('')
    const [connectionResult, setConnectionResult] = useState(null)

    const navigate = useNavigate()

    const dbTypes = [
        { id: 'postgresql', name: 'PostgreSQL', port: 5432, icon: '🐘' },
        { id: 'mysql', name: 'MySQL', port: 3306, icon: '🐬' },
        { id: 'mongodb', name: 'MongoDB', port: 27017, icon: '🍃' },
        { id: 'sqlite', name: 'SQLite', port: null, icon: '📁' }
    ]

    // Set default port when db type changes
    useEffect(() => {
        const selected = dbTypes.find(db => db.id === dbType)
        if (selected?.port) {
            setConfig(prev => ({ ...prev, port: selected.port.toString() }))
        }
    }, [dbType])

    const testConnection = async () => {
        setLoading(true)
        setError('')

        try {
            const response = await api.testDatabaseConnection({
                db_type: dbType,
                host: config.host,
                port: config.port ? parseInt(config.port) : undefined,
                database: config.database,
                username: config.username || undefined,
                password: config.password || undefined
            })

            setConnectionResult(response.connection)
            setTables(response.connection.tables || [])
            setStep(2)
        } catch (err) {
            setError(err.response?.data?.detail || 'Connection failed')
        } finally {
            setLoading(false)
        }
    }

    const analyzeTable = async () => {
        if (!selectedTable) {
            setError('Please select a table')
            return
        }

        setLoading(true)
        setError('')
        setStep(3)

        try {
            const response = await api.analyzeTable({
                db_type: dbType,
                host: config.host,
                port: config.port ? parseInt(config.port) : undefined,
                database: config.database,
                username: config.username || undefined,
                password: config.password || undefined,
                table_name: selectedTable
            })

            // Get the full report
            const reportResponse = await api.getQualityReport(response.source_id)
            if (reportResponse.status === 'success') {
                setCurrentReport(reportResponse.report)
                setCurrentSourceId(response.source_id)
                navigate('/dashboard')
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Analysis failed')
            setStep(2)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-2xl mx-auto">
                {/* Header */}
                <button
                    onClick={() => navigate('/')}
                    className="text-gray-400 hover:text-white flex items-center gap-2 mb-6 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" /> Back to Home
                </button>

                <h1 className="text-3xl font-bold text-white mb-2">Connect Database</h1>
                <p className="text-gray-400 mb-8">Connect to your database to analyze data quality</p>

                {/* Progress Steps */}
                <div className="flex items-center gap-4 mb-8">
                    {['Configure', 'Select Table', 'Analyze'].map((label, i) => (
                        <div key={i} className="flex items-center gap-2">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${step > i + 1 ? 'bg-green-600 text-white' :
                                    step === i + 1 ? 'bg-primary-600 text-white' :
                                        'bg-zinc-800 text-gray-500'
                                }`}>
                                {step > i + 1 ? <Check className="w-4 h-4" /> : i + 1}
                            </div>
                            <span className={step === i + 1 ? 'text-white' : 'text-gray-500'}>{label}</span>
                            {i < 2 && <ChevronRight className="w-4 h-4 text-gray-600" />}
                        </div>
                    ))}
                </div>

                {/* Error Message */}
                {error && (
                    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3">
                        <AlertCircle className="w-5 h-5 text-red-500" />
                        <span className="text-red-400">{error}</span>
                    </div>
                )}

                {/* Step 1: Configure */}
                {step === 1 && (
                    <div className="card">
                        {/* Database Type Selection */}
                        <div className="mb-6">
                            <label className="block text-gray-400 text-sm mb-2">Database Type</label>
                            <div className="grid grid-cols-4 gap-3">
                                {dbTypes.map(db => (
                                    <button
                                        key={db.id}
                                        onClick={() => setDbType(db.id)}
                                        className={`p-4 rounded-lg border text-center transition-all ${dbType === db.id
                                                ? 'border-primary-600 bg-primary-600/10'
                                                : 'border-zinc-800 hover:border-zinc-700'
                                            }`}
                                    >
                                        <div className="text-2xl mb-1">{db.icon}</div>
                                        <div className={dbType === db.id ? 'text-white' : 'text-gray-400'}>{db.name}</div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Connection Form */}
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-gray-400 text-sm mb-2">Host</label>
                                    <div className="relative">
                                        <Server className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                        <input
                                            type="text"
                                            value={config.host}
                                            onChange={(e) => setConfig({ ...config, host: e.target.value })}
                                            placeholder="localhost"
                                            className="input-field pl-10"
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-gray-400 text-sm mb-2">Port</label>
                                    <input
                                        type="text"
                                        value={config.port}
                                        onChange={(e) => setConfig({ ...config, port: e.target.value })}
                                        placeholder={dbTypes.find(d => d.id === dbType)?.port?.toString() || ''}
                                        className="input-field"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-gray-400 text-sm mb-2">Database Name</label>
                                <div className="relative">
                                    <Database className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                    <input
                                        type="text"
                                        value={config.database}
                                        onChange={(e) => setConfig({ ...config, database: e.target.value })}
                                        placeholder="my_database"
                                        className="input-field pl-10"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-gray-400 text-sm mb-2">Username</label>
                                    <input
                                        type="text"
                                        value={config.username}
                                        onChange={(e) => setConfig({ ...config, username: e.target.value })}
                                        placeholder="username"
                                        className="input-field"
                                    />
                                </div>
                                <div>
                                    <label className="block text-gray-400 text-sm mb-2">Password</label>
                                    <div className="relative">
                                        <input
                                            type={showPassword ? 'text' : 'password'}
                                            value={config.password}
                                            onChange={(e) => setConfig({ ...config, password: e.target.value })}
                                            placeholder="••••••••"
                                            className="input-field pr-10"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPassword(!showPassword)}
                                            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
                                        >
                                            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <button
                            onClick={testConnection}
                            disabled={loading || !config.database}
                            className="btn-primary w-full mt-6 flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <><Loader2 className="w-4 h-4 animate-spin" /> Testing Connection...</>
                            ) : (
                                <><Database className="w-4 h-4" /> Test Connection</>
                            )}
                        </button>
                    </div>
                )}

                {/* Step 2: Select Table */}
                {step === 2 && (
                    <div className="card">
                        {connectionResult && (
                            <div className="mb-6 p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                                <div className="flex items-center gap-2 text-green-400 mb-2">
                                    <Check className="w-5 h-5" />
                                    <span className="font-medium">Connected Successfully</span>
                                </div>
                                <p className="text-gray-400 text-sm">
                                    {connectionResult.database_type} • {connectionResult.version}
                                </p>
                            </div>
                        )}

                        <label className="block text-gray-400 text-sm mb-3">
                            Select a table to analyze ({tables.length} tables found)
                        </label>

                        <div className="max-h-80 overflow-y-auto space-y-2 mb-6">
                            {tables.map(table => (
                                <button
                                    key={table}
                                    onClick={() => setSelectedTable(table)}
                                    className={`w-full p-3 rounded-lg border text-left flex items-center gap-3 transition-all ${selectedTable === table
                                            ? 'border-primary-600 bg-primary-600/10'
                                            : 'border-zinc-800 hover:border-zinc-700'
                                        }`}
                                >
                                    <Table className={`w-5 h-5 ${selectedTable === table ? 'text-primary-500' : 'text-gray-500'}`} />
                                    <span className={selectedTable === table ? 'text-white' : 'text-gray-300'}>{table}</span>
                                </button>
                            ))}
                        </div>

                        <div className="flex gap-3">
                            <button onClick={() => setStep(1)} className="btn-secondary flex-1">
                                Back
                            </button>
                            <button
                                onClick={analyzeTable}
                                disabled={!selectedTable || loading}
                                className="btn-primary flex-1 flex items-center justify-center gap-2"
                            >
                                Analyze Table
                            </button>
                        </div>
                    </div>
                )}

                {/* Step 3: Analyzing */}
                {step === 3 && (
                    <div className="card text-center py-12">
                        <Loader2 className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-white mb-2">Analyzing {selectedTable}</h3>
                        <p className="text-gray-400">Running quality checks...</p>
                    </div>
                )}
            </div>
        </div>
    )
}
