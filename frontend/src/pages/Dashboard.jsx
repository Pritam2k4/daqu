import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    BarChart3, AlertTriangle, CheckCircle,
    XCircle, Database, FileText, TrendingUp, AlertCircle,
    Table, Clock, Target, ArrowLeft, Download, Sparkles,
    Code, Zap, Check, X, Copy, ChevronRight, Shield,
    Activity, Layers, Calendar, GitBranch, Brain
} from 'lucide-react'
import { api } from '../services/api'

export default function Dashboard({ externalReport, sourceId }) {
    const [report, setReport] = useState(externalReport || null)
    const [loading, setLoading] = useState(!externalReport)
    const [activeTab, setActiveTab] = useState('overview')
    const [suggestions, setSuggestions] = useState([])
    const [suggestionsLoading, setSuggestionsLoading] = useState(false)
    const navigate = useNavigate()

    useEffect(() => {
        if (!externalReport) {
            loadDemoReport()
        }
    }, [externalReport])

    const loadDemoReport = async () => {
        try {
            const response = await api.getDemoReport()
            setReport(response.report)
        } catch (error) {
            console.error('Failed to load demo report:', error)
        } finally {
            setLoading(false)
        }
    }

    const loadSuggestions = async () => {
        setSuggestionsLoading(true)
        try {
            const response = await api.getSuggestions(sourceId || 'demo')
            setSuggestions(response.suggestions || [])
        } catch (error) {
            console.error('Failed to load suggestions:', error)
        } finally {
            setSuggestionsLoading(false)
        }
    }

    const handleExport = async () => {
        try {
            const response = await api.exportReport(sourceId || 'demo', 'json')
            const blob = new Blob([response.data], { type: 'application/json' })
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `quality_report_${sourceId || 'demo'}.json`
            a.click()
            window.URL.revokeObjectURL(url)
        } catch (error) {
            console.error('Export failed:', error)
        }
    }

    useEffect(() => {
        if (activeTab === 'suggestions' && suggestions.length === 0) {
            loadSuggestions()
        }
    }, [activeTab])

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-400">Analyzing your data...</p>
                </div>
            </div>
        )
    }

    if (!report) {
        return (
            <div className="min-h-screen p-8">
                <div className="max-w-4xl mx-auto text-center py-20">
                    <AlertCircle className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-white mb-2">No Data Loaded</h2>
                    <p className="text-gray-400 mb-6">Upload a file to see quality analysis</p>
                    <button onClick={() => navigate('/')} className="btn-primary">Go to Upload</button>
                </div>
            </div>
        )
    }

    const tabs = [
        { id: 'overview', label: 'Overview', icon: <BarChart3 className="w-4 h-4" /> },
        { id: 'dimensions', label: 'Quality Dimensions', icon: <Shield className="w-4 h-4" /> },
        { id: 'ml-readiness', label: 'ML Readiness', icon: <Brain className="w-4 h-4" /> },
        { id: 'columns', label: 'Column Profiles', icon: <Table className="w-4 h-4" /> },
        { id: 'suggestions', label: 'AI Fixes', icon: <Sparkles className="w-4 h-4" /> },
        { id: 'preview', label: 'Data Preview', icon: <FileText className="w-4 h-4" /> }
    ]

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <button
                            onClick={() => navigate('/')}
                            className="text-gray-400 hover:text-white flex items-center gap-2 mb-2 transition-colors"
                        >
                            <ArrowLeft className="w-4 h-4" /> Back to Upload
                        </button>
                        <h1 className="text-3xl font-bold text-white mb-2">Data Quality Report</h1>
                        <p className="text-gray-400 flex items-center gap-2 flex-wrap">
                            <FileText className="w-4 h-4" />
                            {report.overview?.filename || report.filename}
                            <span className="text-zinc-600">•</span>
                            <span>{report.overview?.rows?.toLocaleString()} rows × {report.overview?.columns} columns</span>
                            <span className="text-zinc-600">•</span>
                            <span className="text-xs px-2 py-0.5 rounded bg-zinc-800">DAMA Framework</span>
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        <button onClick={handleExport} className="btn-secondary flex items-center gap-2">
                            <Download className="w-4 h-4" /> Export
                        </button>
                        <QualityBadge
                            score={report.quality_score?.overall_score || 0}
                            grade={report.quality_score?.grade || 'N/A'}
                            description={report.quality_score?.grade_description}
                        />
                    </div>
                </div>

                {/* Tab Navigation */}
                <div className="flex gap-2 mb-8 border-b border-zinc-800 pb-2 overflow-x-auto">
                    {tabs.map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 whitespace-nowrap ${activeTab === tab.id
                                    ? 'bg-primary-600 text-white'
                                    : 'text-gray-400 hover:text-white hover:bg-zinc-800'
                                }`}
                        >
                            {tab.icon} {tab.label}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                {activeTab === 'overview' && <OverviewTab report={report} />}
                {activeTab === 'dimensions' && <DimensionsTab report={report} />}
                {activeTab === 'ml-readiness' && <MLReadinessTab mlReadiness={report.ml_readiness} />}
                {activeTab === 'columns' && <ColumnsTab columns={report.column_profiles} />}
                {activeTab === 'suggestions' && <SuggestionsTab suggestions={suggestions} loading={suggestionsLoading} onRefresh={loadSuggestions} />}
                {activeTab === 'preview' && <DataPreviewTab sample={report.sample_data} columns={report.overview?.column_names} />}
            </div>
        </div>
    )
}

// Quality Score Badge with Description
function QualityBadge({ score, grade, description }) {
    const gradeColors = {
        'A': 'from-green-500 to-emerald-600',
        'B': 'from-blue-500 to-cyan-600',
        'C': 'from-yellow-500 to-amber-600',
        'D': 'from-orange-500 to-red-500',
        'F': 'from-red-500 to-rose-600',
        'N/A': 'from-gray-500 to-gray-600'
    }
    return (
        <div className={`px-6 py-4 rounded-xl bg-gradient-to-r ${gradeColors[grade] || gradeColors['N/A']} shadow-lg`}>
            <div className="text-center">
                <div className="text-4xl font-bold text-white">{score}%</div>
                <div className="text-white/90 text-sm font-medium">Grade {grade}</div>
            </div>
        </div>
    )
}

// OVERVIEW TAB - Industry Standard Metrics Summary
function OverviewTab({ report }) {
    const { quality_score, overview, completeness, uniqueness, validity, consistency, accuracy, timeliness } = report

    const dimensions = [
        { key: 'completeness', label: 'Completeness', icon: <CheckCircle className="w-5 h-5" />, data: completeness, description: 'Data presence' },
        { key: 'uniqueness', label: 'Uniqueness', icon: <Layers className="w-5 h-5" />, data: uniqueness, description: 'No duplicates' },
        { key: 'validity', label: 'Validity', icon: <Shield className="w-5 h-5" />, data: validity, description: 'Format compliance' },
        { key: 'consistency', label: 'Consistency', icon: <GitBranch className="w-5 h-5" />, data: consistency, description: 'Data uniformity' },
        { key: 'accuracy', label: 'Accuracy', icon: <Target className="w-5 h-5" />, data: accuracy, description: 'Outlier analysis' },
        { key: 'timeliness', label: 'Timeliness', icon: <Calendar className="w-5 h-5" />, data: timeliness, description: 'Data freshness' }
    ]

    return (
        <div className="space-y-6">
            {/* Overall Score Card */}
            <div className="card bg-gradient-to-r from-zinc-900 to-zinc-800 border-zinc-700">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-xl font-bold text-white mb-1">Overall Data Quality</h3>
                        <p className="text-gray-400">{quality_score?.grade_description}</p>
                        <div className="flex items-center gap-2 mt-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${quality_score?.ml_readiness_status === 'ready' ? 'bg-green-500/20 text-green-400' :
                                    quality_score?.ml_readiness_status === 'needs_improvement' ? 'bg-yellow-500/20 text-yellow-400' :
                                        'bg-red-500/20 text-red-400'
                                }`}>
                                ML: {quality_score?.ml_readiness_status?.replace('_', ' ')}
                            </span>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-5xl font-bold text-white">{quality_score?.overall_score}%</div>
                        <div className="text-gray-400 text-sm mt-1">Based on DAMA Framework</div>
                    </div>
                </div>
            </div>

            {/* Dimension Scores Grid */}
            <div>
                <h3 className="text-lg font-semibold text-white mb-4">Quality Dimensions (ISO 25024)</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                    {dimensions.map(dim => (
                        <DimensionCard key={dim.key} {...dim} />
                    ))}
                </div>
            </div>

            {/* Dataset Overview */}
            <div className="grid md:grid-cols-2 gap-6">
                <div className="card">
                    <h3 className="text-lg font-semibold text-white mb-4">Dataset Overview</h3>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 bg-zinc-800/50 rounded-lg">
                            <div className="text-2xl font-bold text-white">{overview?.rows?.toLocaleString()}</div>
                            <div className="text-gray-400 text-sm">Total Rows</div>
                        </div>
                        <div className="p-3 bg-zinc-800/50 rounded-lg">
                            <div className="text-2xl font-bold text-white">{overview?.columns}</div>
                            <div className="text-gray-400 text-sm">Total Columns</div>
                        </div>
                        <div className="p-3 bg-zinc-800/50 rounded-lg">
                            <div className="text-2xl font-bold text-blue-400">{overview?.column_types?.numeric || 0}</div>
                            <div className="text-gray-400 text-sm">Numeric</div>
                        </div>
                        <div className="p-3 bg-zinc-800/50 rounded-lg">
                            <div className="text-2xl font-bold text-purple-400">{overview?.column_types?.categorical || 0}</div>
                            <div className="text-gray-400 text-sm">Categorical</div>
                        </div>
                    </div>
                </div>

                <div className="card">
                    <h3 className="text-lg font-semibold text-white mb-4">Quality Summary</h3>
                    <div className="space-y-3">
                        {dimensions.slice(0, 4).map(dim => (
                            <QualityBar
                                key={dim.key}
                                label={dim.label}
                                value={dim.data?.score}
                                status={dim.data?.status}
                            />
                        ))}
                    </div>
                </div>
            </div>

            {/* Key Issues */}
            <div className="card">
                <h3 className="text-lg font-semibold text-white mb-4">Key Issues Detected</h3>
                <div className="grid md:grid-cols-3 gap-4">
                    <IssueCard
                        icon={<AlertTriangle className="w-5 h-5" />}
                        title="Missing Data"
                        value={`${completeness?.null_cells?.toLocaleString()} cells`}
                        subtitle={`${completeness?.columns_below_threshold} columns below threshold`}
                        color="amber"
                    />
                    <IssueCard
                        icon={<XCircle className="w-5 h-5" />}
                        title="Duplicates"
                        value={`${uniqueness?.duplicate_rows?.toLocaleString()} rows`}
                        subtitle={`${uniqueness?.duplicate_percentage}% of dataset`}
                        color="red"
                    />
                    <IssueCard
                        icon={<TrendingUp className="w-5 h-5" />}
                        title="Validity Issues"
                        value={`${validity?.failed_checks} checks failed`}
                        subtitle={`${validity?.issues?.length || 0} columns affected`}
                        color="orange"
                    />
                </div>
            </div>
        </div>
    )
}

// Dimension Card
function DimensionCard({ label, icon, data, description }) {
    const score = data?.score ?? 0
    const status = data?.status || 'unknown'

    const statusColors = {
        pass: 'border-green-500/50 bg-green-500/5',
        warning: 'border-yellow-500/50 bg-yellow-500/5',
        fail: 'border-red-500/50 bg-red-500/5',
        unknown: 'border-zinc-700 bg-zinc-800/50'
    }

    const scoreColors = {
        pass: 'text-green-400',
        warning: 'text-yellow-400',
        fail: 'text-red-400',
        unknown: 'text-gray-400'
    }

    return (
        <div className={`p-4 rounded-xl border ${statusColors[status]} transition-all hover:scale-105`}>
            <div className="flex items-center gap-2 text-gray-400 mb-2">
                {icon}
                <span className="text-sm font-medium">{label}</span>
            </div>
            <div className={`text-2xl font-bold ${scoreColors[status]}`}>{score}%</div>
            <div className="text-gray-500 text-xs mt-1">{description}</div>
        </div>
    )
}

// Issue Card
function IssueCard({ icon, title, value, subtitle, color }) {
    const colors = {
        amber: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
        red: 'text-red-500 bg-red-500/10 border-red-500/20',
        orange: 'text-orange-500 bg-orange-500/10 border-orange-500/20'
    }

    return (
        <div className={`p-4 rounded-lg border ${colors[color]}`}>
            <div className={`${colors[color].split(' ')[0]} mb-2`}>{icon}</div>
            <div className="text-white font-medium">{title}</div>
            <div className="text-2xl font-bold text-white mt-1">{value}</div>
            <div className="text-gray-400 text-sm">{subtitle}</div>
        </div>
    )
}

// DIMENSIONS TAB - Detailed breakdown of each dimension
function DimensionsTab({ report }) {
    const { completeness, uniqueness, validity, consistency, accuracy, timeliness } = report

    return (
        <div className="space-y-6">
            {/* Completeness */}
            <div className="card">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <CheckCircle className="w-6 h-6 text-primary-500" />
                        <div>
                            <h3 className="text-lg font-semibold text-white">Completeness</h3>
                            <p className="text-gray-400 text-sm">{completeness?.description}</p>
                        </div>
                    </div>
                    <StatusBadge score={completeness?.score} status={completeness?.status} />
                </div>
                <div className="grid md:grid-cols-4 gap-4 mb-4">
                    <MetricBox label="Total Cells" value={completeness?.total_cells?.toLocaleString()} />
                    <MetricBox label="Non-Null" value={completeness?.non_null_cells?.toLocaleString()} />
                    <MetricBox label="Null Cells" value={completeness?.null_cells?.toLocaleString()} color="red" />
                    <MetricBox label="Columns Below Threshold" value={completeness?.columns_below_threshold} color="amber" />
                </div>
                {completeness?.column_details?.filter(c => c.status !== 'pass').length > 0 && (
                    <div className="mt-4">
                        <h4 className="text-white font-medium mb-2">Columns Needing Attention</h4>
                        <div className="space-y-2">
                            {completeness.column_details.filter(c => c.status !== 'pass').map((col, i) => (
                                <div key={i} className="flex items-center justify-between p-2 bg-zinc-800/50 rounded-lg">
                                    <span className="text-white">{col.column}</span>
                                    <div className="flex items-center gap-4">
                                        <span className="text-gray-400">{col.null_count} null</span>
                                        <span className={col.status === 'fail' ? 'text-red-400' : 'text-yellow-400'}>
                                            {col.completeness_ratio}%
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Uniqueness */}
            <div className="card">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <Layers className="w-6 h-6 text-primary-500" />
                        <div>
                            <h3 className="text-lg font-semibold text-white">Uniqueness</h3>
                            <p className="text-gray-400 text-sm">{uniqueness?.description}</p>
                        </div>
                    </div>
                    <StatusBadge score={uniqueness?.score} status={uniqueness?.status} />
                </div>
                <div className="grid md:grid-cols-4 gap-4">
                    <MetricBox label="Total Rows" value={uniqueness?.total_rows?.toLocaleString()} />
                    <MetricBox label="Unique Rows" value={uniqueness?.unique_rows?.toLocaleString()} color="green" />
                    <MetricBox label="Duplicates" value={uniqueness?.duplicate_rows?.toLocaleString()} color="red" />
                    <MetricBox label="Duplicate %" value={`${uniqueness?.duplicate_percentage}%`} color="amber" />
                </div>
                {uniqueness?.potential_key_columns?.length > 0 && (
                    <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                        <span className="text-green-400">✓ Potential Key Columns: </span>
                        <span className="text-white">{uniqueness.potential_key_columns.join(', ')}</span>
                    </div>
                )}
            </div>

            {/* Validity */}
            <div className="card">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <Shield className="w-6 h-6 text-primary-500" />
                        <div>
                            <h3 className="text-lg font-semibold text-white">Validity</h3>
                            <p className="text-gray-400 text-sm">{validity?.description}</p>
                        </div>
                    </div>
                    <StatusBadge score={validity?.score} status={validity?.status} />
                </div>
                <div className="grid md:grid-cols-3 gap-4 mb-4">
                    <MetricBox label="Total Checks" value={validity?.total_checks} />
                    <MetricBox label="Passed" value={validity?.passed_checks} color="green" />
                    <MetricBox label="Failed" value={validity?.failed_checks} color="red" />
                </div>
                {validity?.issues?.length > 0 && (
                    <div className="space-y-2">
                        {validity.issues.map((issue, i) => (
                            <div key={i} className={`p-3 rounded-lg border ${issue.severity === 'high' ? 'border-red-500/30 bg-red-500/5' : 'border-yellow-500/30 bg-yellow-500/5'}`}>
                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-white font-medium">{issue.column}</span>
                                    <span className={`text-xs px-2 py-0.5 rounded ${issue.severity === 'high' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                                        {issue.severity}
                                    </span>
                                </div>
                                <div className="text-gray-400 text-sm">{issue.issues.join(', ')}</div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Consistency */}
            <div className="card">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <GitBranch className="w-6 h-6 text-primary-500" />
                        <div>
                            <h3 className="text-lg font-semibold text-white">Consistency</h3>
                            <p className="text-gray-400 text-sm">{consistency?.description}</p>
                        </div>
                    </div>
                    <StatusBadge score={consistency?.score} status={consistency?.status} />
                </div>
                {consistency?.issues?.length > 0 ? (
                    <div className="space-y-2">
                        {consistency.issues.map((issue, i) => (
                            <div key={i} className="p-3 bg-zinc-800/50 rounded-lg">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-white font-medium">{issue.column}</span>
                                    <span className="text-red-400 text-sm">{issue.impact} points</span>
                                </div>
                                <div className="text-gray-400 text-sm">{issue.issue}: {issue.description}</div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-green-400">✓ No consistency issues detected</p>
                )}
            </div>

            {/* Accuracy */}
            <div className="card">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <Target className="w-6 h-6 text-primary-500" />
                        <div>
                            <h3 className="text-lg font-semibold text-white">Accuracy (Outlier Analysis)</h3>
                            <p className="text-gray-400 text-sm">{accuracy?.description}</p>
                        </div>
                    </div>
                    <StatusBadge score={accuracy?.score} status={accuracy?.status} />
                </div>
                <p className="text-gray-500 text-sm mb-4">{accuracy?.note}</p>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead>
                            <tr className="border-b border-zinc-800">
                                <th className="px-3 py-2 text-gray-400">Column</th>
                                <th className="px-3 py-2 text-gray-400">Outliers</th>
                                <th className="px-3 py-2 text-gray-400">Valid Range</th>
                                <th className="px-3 py-2 text-gray-400">Mean</th>
                                <th className="px-3 py-2 text-gray-400">Skewness</th>
                                <th className="px-3 py-2 text-gray-400">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {accuracy?.outlier_analysis?.map((col, i) => (
                                <tr key={i} className="border-b border-zinc-800/50">
                                    <td className="px-3 py-2 text-white">{col.column}</td>
                                    <td className="px-3 py-2 text-gray-300">{col.outlier_count} ({col.outlier_percentage}%)</td>
                                    <td className="px-3 py-2 text-gray-300">{col.lower_bound} - {col.upper_bound}</td>
                                    <td className="px-3 py-2 text-gray-300">{col.mean}</td>
                                    <td className="px-3 py-2 text-gray-300">{col.skewness}</td>
                                    <td className="px-3 py-2">
                                        <span className={`px-2 py-0.5 rounded text-xs ${col.status === 'pass' ? 'bg-green-500/20 text-green-400' :
                                                col.status === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                                                    'bg-red-500/20 text-red-400'
                                            }`}>{col.status}</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}

// Status Badge
function StatusBadge({ score, status }) {
    const colors = {
        pass: 'bg-green-500/20 text-green-400 border-green-500/30',
        warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
        fail: 'bg-red-500/20 text-red-400 border-red-500/30'
    }
    return (
        <div className={`px-4 py-2 rounded-lg border ${colors[status] || colors.warning}`}>
            <span className="text-2xl font-bold">{score}%</span>
        </div>
    )
}

// Metric Box
function MetricBox({ label, value, color }) {
    const textColors = { green: 'text-green-400', red: 'text-red-400', amber: 'text-amber-400' }
    return (
        <div className="p-3 bg-zinc-800/50 rounded-lg">
            <div className={`text-xl font-bold ${textColors[color] || 'text-white'}`}>{value}</div>
            <div className="text-gray-400 text-sm">{label}</div>
        </div>
    )
}

// Quality Bar
function QualityBar({ label, value, status }) {
    const colors = { pass: 'bg-green-500', warning: 'bg-yellow-500', fail: 'bg-red-500' }
    return (
        <div>
            <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">{label}</span>
                <span className="text-white font-medium">{value?.toFixed(1) || 0}%</span>
            </div>
            <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                <div className={`h-full ${colors[status] || 'bg-gray-500'} transition-all duration-500`} style={{ width: `${value || 0}%` }} />
            </div>
        </div>
    )
}

// ML READINESS TAB
function MLReadinessTab({ mlReadiness }) {
    if (!mlReadiness) return <div className="text-gray-400">No ML readiness data available</div>

    return (
        <div className="space-y-6">
            {/* Overall ML Readiness */}
            <div className="card">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <Brain className="w-8 h-8 text-primary-500" />
                        <div>
                            <h3 className="text-xl font-bold text-white">ML Readiness Assessment</h3>
                            <p className="text-gray-400">{mlReadiness.description}</p>
                        </div>
                    </div>
                    <div className={`px-6 py-3 rounded-xl ${mlReadiness.status === 'ready' ? 'bg-green-500/20 text-green-400' :
                            mlReadiness.status === 'needs_improvement' ? 'bg-yellow-500/20 text-yellow-400' :
                                'bg-red-500/20 text-red-400'
                        }`}>
                        <div className="text-3xl font-bold">{mlReadiness.score}%</div>
                        <div className="text-sm capitalize">{mlReadiness.status?.replace('_', ' ')}</div>
                    </div>
                </div>
            </div>

            {/* Class Balance Analysis */}
            {mlReadiness.class_balance_analysis?.length > 0 && (
                <div className="card">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Target className="w-5 h-5 text-primary-500" />
                        Class Balance Analysis
                    </h3>
                    <div className="space-y-4">
                        {mlReadiness.class_balance_analysis.map((cls, i) => (
                            <div key={i} className="p-4 bg-zinc-800/50 rounded-lg">
                                <div className="flex items-center justify-between mb-3">
                                    <span className="text-white font-medium">{cls.column}</span>
                                    <span className={`px-2 py-1 rounded text-xs ${cls.status === 'balanced' ? 'bg-green-500/20 text-green-400' :
                                            cls.status === 'imbalanced' ? 'bg-yellow-500/20 text-yellow-400' :
                                                'bg-red-500/20 text-red-400'
                                        }`}>{cls.status}</span>
                                </div>
                                <div className="grid grid-cols-4 gap-4 text-sm">
                                    <div><span className="text-gray-400">Classes:</span> <span className="text-white">{cls.num_classes}</span></div>
                                    <div><span className="text-gray-400">Imbalance:</span> <span className="text-white">{cls.imbalance_ratio}:1</span></div>
                                    <div><span className="text-gray-400">Majority:</span> <span className="text-white">{cls.majority_class_pct}%</span></div>
                                    <div><span className="text-gray-400">Minority:</span> <span className="text-white">{cls.minority_class_pct}%</span></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* High Correlations */}
            {mlReadiness.high_correlations?.length > 0 && (
                <div className="card">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-orange-500" />
                        High Feature Correlations
                    </h3>
                    <div className="space-y-2">
                        {mlReadiness.high_correlations.map((corr, i) => (
                            <div key={i} className="flex items-center justify-between p-3 bg-zinc-800/50 rounded-lg">
                                <div>
                                    <span className="text-white">{corr.column1}</span>
                                    <span className="text-gray-500 mx-2">↔</span>
                                    <span className="text-white">{corr.column2}</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <span className={`px-2 py-1 rounded text-xs ${corr.risk === 'multicollinearity' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
                                        }`}>{corr.risk}</span>
                                    <span className="text-white font-mono">{corr.correlation}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Recommendations */}
            {mlReadiness.recommendations?.length > 0 && (
                <div className="card">
                    <h3 className="text-lg font-semibold text-white mb-4">Recommendations</h3>
                    <ul className="space-y-2">
                        {mlReadiness.recommendations.map((rec, i) => (
                            <li key={i} className="flex items-start gap-2 text-gray-400">
                                <CheckCircle className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
                                {rec}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    )
}

// COLUMNS TAB
function ColumnsTab({ columns }) {
    if (!columns || columns.length === 0) return <div className="text-gray-400">No column data available</div>

    return (
        <div className="card overflow-hidden">
            <h3 className="text-lg font-semibold text-white mb-4">Column Profiles ({columns.length} columns)</h3>
            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead>
                        <tr className="border-b border-zinc-800">
                            <th className="px-4 py-3 text-gray-400">Column</th>
                            <th className="px-4 py-3 text-gray-400">Type</th>
                            <th className="px-4 py-3 text-gray-400">Non-Null</th>
                            <th className="px-4 py-3 text-gray-400">Null %</th>
                            <th className="px-4 py-3 text-gray-400">Unique</th>
                            <th className="px-4 py-3 text-gray-400">Stats / Top Values</th>
                        </tr>
                    </thead>
                    <tbody>
                        {columns.map((col, i) => (
                            <tr key={i} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                                <td className="px-4 py-3 text-white font-medium">{col.name}</td>
                                <td className="px-4 py-3">
                                    <span className={`px-2 py-1 rounded text-xs ${col.is_numeric ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400'}`}>
                                        {col.dtype}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-gray-300">{col.non_null_count?.toLocaleString()}</td>
                                <td className="px-4 py-3"><span className={col.null_percentage > 5 ? 'text-red-400' : 'text-gray-400'}>{col.null_percentage}%</span></td>
                                <td className="px-4 py-3 text-gray-300">{col.unique_count?.toLocaleString()}</td>
                                <td className="px-4 py-3 text-gray-400 text-xs">
                                    {col.is_numeric && col.stats ? (
                                        <span>μ={col.stats.mean}, σ={col.stats.std}, range=[{col.stats.min}, {col.stats.max}]</span>
                                    ) : col.value_distribution ? (
                                        <span>{col.value_distribution.slice(0, 3).map(v => `${v.value}: ${v.percentage}%`).join(', ')}</span>
                                    ) : null}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

// SUGGESTIONS TAB
function SuggestionsTab({ suggestions, loading, onRefresh }) {
    const [selectedFixes, setSelectedFixes] = useState([])
    const [copiedId, setCopiedId] = useState(null)

    const toggleFix = (id) => setSelectedFixes(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
    const copyCode = (code, id) => { navigator.clipboard.writeText(code); setCopiedId(id); setTimeout(() => setCopiedId(null), 2000) }

    if (loading) return (
        <div className="text-center py-12">
            <Sparkles className="w-12 h-12 text-primary-500 animate-pulse mx-auto mb-4" />
            <p className="text-gray-400">Generating AI suggestions...</p>
        </div>
    )

    if (suggestions.length === 0) return (
        <div className="card text-center py-12">
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">No Issues Found!</h3>
            <p className="text-gray-400">Your data looks great. No fixes needed.</p>
        </div>
    )

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-primary-500" /> AI-Powered Fix Suggestions
                    </h3>
                    <p className="text-gray-400 text-sm mt-1">{suggestions.length} suggestions generated</p>
                </div>
                <div className="flex gap-3">
                    <button onClick={onRefresh} className="btn-secondary flex items-center gap-2"><Zap className="w-4 h-4" /> Refresh</button>
                    {selectedFixes.length > 0 && (
                        <button className="btn-primary flex items-center gap-2"><Check className="w-4 h-4" /> Apply {selectedFixes.length} Fix{selectedFixes.length > 1 ? 'es' : ''}</button>
                    )}
                </div>
            </div>
            <div className="space-y-4">
                {suggestions.map((s) => (
                    <div key={s.id} className={`card border-l-4 ${s.severity === 'high' ? 'border-red-500' : s.severity === 'medium' ? 'border-yellow-500' : 'border-blue-500'} ${selectedFixes.includes(s.id) ? 'ring-2 ring-primary-600' : ''}`}>
                        <div className="flex items-start gap-4">
                            <button onClick={() => toggleFix(s.id)} className={`w-6 h-6 rounded border-2 flex items-center justify-center shrink-0 mt-1 ${selectedFixes.includes(s.id) ? 'bg-primary-600 border-primary-600' : 'border-zinc-600 hover:border-primary-600'}`}>
                                {selectedFixes.includes(s.id) && <Check className="w-4 h-4 text-white" />}
                            </button>
                            <div className="flex-1">
                                <div className="flex items-start justify-between mb-2">
                                    <div>
                                        <span className={`text-xs px-2 py-0.5 rounded-full uppercase font-medium mr-2 ${s.severity === 'high' ? 'bg-red-500/20 text-red-400' : s.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-blue-500/20 text-blue-400'}`}>{s.severity}</span>
                                        <span className="text-xs text-gray-500 uppercase">{s.issue_type.replace('_', ' ')}</span>
                                    </div>
                                    <span className="text-gray-400 text-sm">{Math.round(s.confidence * 100)}% confidence</span>
                                </div>
                                <h4 className="text-white font-medium mb-2">{s.description}</h4>
                                <div className="bg-zinc-800/50 rounded-lg p-3 mb-3">
                                    <div className="flex items-center gap-2 text-green-400 text-sm mb-1"><ChevronRight className="w-4 h-4" /><span className="font-medium">Suggested Fix:</span></div>
                                    <p className="text-gray-300 text-sm">{s.suggested_fix}</p>
                                </div>
                                <div className="bg-black rounded-lg p-3 relative">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-xs text-gray-500 flex items-center gap-1"><Code className="w-3 h-3" /> Python</span>
                                        <button onClick={() => copyCode(s.code_snippet, s.id)} className="text-gray-500 hover:text-white">{copiedId === s.id ? <span className="text-green-400 text-xs">Copied!</span> : <Copy className="w-4 h-4" />}</button>
                                    </div>
                                    <code className="text-sm text-primary-400 font-mono">{s.code_snippet}</code>
                                </div>
                                <p className="text-gray-500 text-xs mt-2">Impact: {s.impact}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

// DATA PREVIEW TAB
function DataPreviewTab({ sample, columns }) {
    if (!sample || sample.length === 0) return <div className="text-gray-400">No sample data available</div>
    return (
        <div className="card overflow-hidden">
            <h3 className="text-lg font-semibold text-white mb-4">Data Preview (First {sample.length} rows)</h3>
            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead>
                        <tr className="border-b border-zinc-800">
                            {columns?.slice(0, 7).map((col, i) => (
                                <th key={i} className="px-4 py-3 text-gray-400 font-medium whitespace-nowrap">{col}</th>
                            ))}
                            {columns?.length > 7 && <th className="px-4 py-3 text-gray-500">+{columns.length - 7} more</th>}
                        </tr>
                    </thead>
                    <tbody>
                        {sample.map((row, i) => (
                            <tr key={i} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                                {columns?.slice(0, 7).map((col, j) => (
                                    <td key={j} className="px-4 py-3 text-gray-300 whitespace-nowrap max-w-xs truncate">{row[col] || '-'}</td>
                                ))}
                                {columns?.length > 7 && <td className="px-4 py-3 text-gray-500">...</td>}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
