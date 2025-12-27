import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Brain, ArrowLeft, Send, Loader2, Bot, User, Sparkles,
    BarChart3, Play, Zap, Check, Target, TrendingUp,
    ChevronRight, Download, RefreshCw
} from 'lucide-react'
import { api } from '../services/api'

export default function ModelStudio({ sourceId }) {
    const [step, setStep] = useState('landing') // landing, chat, training, results
    const [messages, setMessages] = useState([])
    const [inputValue, setInputValue] = useState('')
    const [loading, setLoading] = useState(false)
    const [recommendations, setRecommendations] = useState([])
    const [dataProfile, setDataProfile] = useState(null)
    const [trainingResults, setTrainingResults] = useState(null)
    const [targetColumn, setTargetColumn] = useState('')
    const [currentSourceId, setCurrentSourceId] = useState(sourceId || 'demo')
    const messagesEndRef = useRef(null)
    const navigate = useNavigate()

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const startAssistant = async () => {
        setStep('chat')
        setLoading(true)

        // Add initial system message
        setMessages([{
            type: 'system',
            content: "Welcome to Model Studio! Let me analyze your data and suggest the best ML models for your needs."
        }])

        try {
            // Get demo analysis
            const response = await api.getDemoModelAnalysis()

            setDataProfile(response.data_profile)
            setRecommendations(response.recommendations)
            setTargetColumn(response.data_profile?.target_column || 'churn')

            // Add analysis message
            setTimeout(() => {
                setMessages(prev => [...prev, {
                    type: 'bot',
                    content: response.message,
                    actions: response.actions
                }])
                setLoading(false)
            }, 500)
        } catch (error) {
            console.error('Failed to load analysis:', error)
            setMessages(prev => [...prev, {
                type: 'bot',
                content: "I couldn't analyze your data. Please make sure you have uploaded a dataset first.",
                isError: true
            }])
            setLoading(false)
        }
    }

    const sendMessage = async () => {
        if (!inputValue.trim() || loading) return

        const userMessage = inputValue
        setInputValue('')
        setMessages(prev => [...prev, { type: 'user', content: userMessage }])
        setLoading(true)

        try {
            const response = await api.chatWithModelAssistant({
                source_id: currentSourceId,
                target_column: targetColumn,
                question: userMessage
            })

            setMessages(prev => [...prev, {
                type: 'bot',
                content: response.answer || response.message
            }])
        } catch (error) {
            setMessages(prev => [...prev, {
                type: 'bot',
                content: "Sorry, I encountered an error. Please try again.",
                isError: true
            }])
        }

        setLoading(false)
    }

    const handleAction = async (action) => {
        if (action.action === 'train') {
            setStep('training')
            setMessages(prev => [...prev, {
                type: 'system',
                content: `Training ${action.model.replace('_', ' ').toUpperCase()}...`
            }])

            try {
                const response = await api.trainModel({
                    source_id: currentSourceId,
                    model_name: action.model,
                    target_column: targetColumn
                })

                setTrainingResults(response.results)
                setStep('results')
            } catch (error) {
                setStep('chat')
                setMessages(prev => [...prev, {
                    type: 'bot',
                    content: `Training failed: ${error.response?.data?.detail || 'Unknown error'}. This model may not be installed. Try installing: pip install ${action.model}`,
                    isError: true
                }])
            }
        } else if (action.action === 'compare') {
            setStep('training')
            setMessages(prev => [...prev, {
                type: 'system',
                content: "Comparing multiple models..."
            }])

            try {
                const response = await api.compareModels({
                    source_id: currentSourceId,
                    target_column: targetColumn
                })

                setTrainingResults({
                    comparison: true,
                    best_model: response.best_model,
                    results: response.results,
                    chart: response.comparison_chart
                })
                setStep('results')
            } catch (error) {
                setStep('chat')
                setMessages(prev => [...prev, {
                    type: 'bot',
                    content: `Comparison failed: ${error.response?.data?.detail || 'Unknown error'}`,
                    isError: true
                }])
            }
        }
    }

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <button
                    onClick={() => navigate('/')}
                    className="text-gray-400 hover:text-white flex items-center gap-2 mb-6 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" /> Back to Home
                </button>

                {/* Landing */}
                {step === 'landing' && (
                    <div className="text-center py-16">
                        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-600 to-purple-600 flex items-center justify-center mx-auto mb-6">
                            <Brain className="w-10 h-10 text-white" />
                        </div>
                        <h1 className="text-4xl font-bold text-white mb-4">Model Studio</h1>
                        <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
                            Your AI-powered assistant for training machine learning models.
                            I'll analyze your data and recommend the best models for your use case.
                        </p>

                        <div className="grid md:grid-cols-3 gap-6 mb-10">
                            <FeatureCard
                                icon={<Sparkles className="w-8 h-8" />}
                                title="Smart Recommendations"
                                description="AI analyzes your data and suggests optimal models"
                            />
                            <FeatureCard
                                icon={<BarChart3 className="w-8 h-8" />}
                                title="Visual Results"
                                description="Charts for metrics, feature importance, and more"
                            />
                            <FeatureCard
                                icon={<Zap className="w-8 h-8" />}
                                title="AutoML Compare"
                                description="Train multiple models and find the best one"
                            />
                        </div>

                        <button onClick={startAssistant} className="btn-primary text-lg px-8 py-4">
                            <Play className="w-5 h-5 mr-2 inline" />
                            Start Model Assistant
                        </button>
                    </div>
                )}

                {/* Chat Interface */}
                {(step === 'chat' || step === 'training') && (
                    <div className="flex flex-col h-[calc(100vh-200px)]">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center">
                                <Brain className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-white">Model Assistant</h2>
                                <p className="text-gray-400 text-sm">Ask about models or train one</p>
                            </div>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
                            {messages.map((msg, i) => (
                                <MessageBubble key={i} message={msg} onAction={handleAction} />
                            ))}
                            {loading && (
                                <div className="flex items-center gap-3 p-4">
                                    <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
                                        <Bot className="w-4 h-4 text-white" />
                                    </div>
                                    <div className="flex gap-1">
                                        <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                        <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                        <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                    </div>
                                </div>
                            )}
                            {step === 'training' && (
                                <div className="card text-center py-8">
                                    <Loader2 className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
                                    <h3 className="text-xl font-bold text-white mb-2">Training in Progress</h3>
                                    <p className="text-gray-400">This may take a few moments...</p>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input */}
                        {step !== 'training' && (
                            <div className="flex gap-3">
                                <input
                                    type="text"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                                    placeholder="Ask about models or your data..."
                                    className="input-field flex-1"
                                    disabled={loading}
                                />
                                <button
                                    onClick={sendMessage}
                                    disabled={loading || !inputValue.trim()}
                                    className="btn-primary px-4"
                                >
                                    <Send className="w-5 h-5" />
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {/* Results */}
                {step === 'results' && trainingResults && (
                    <ResultsView
                        results={trainingResults}
                        onBack={() => setStep('chat')}
                        onNewTraining={() => {
                            setStep('chat')
                            setMessages(prev => [...prev, {
                                type: 'bot',
                                content: "Great work! Would you like to train another model or compare different algorithms?"
                            }])
                        }}
                    />
                )}
            </div>
        </div>
    )
}

// Feature Card
function FeatureCard({ icon, title, description }) {
    return (
        <div className="card text-center hover:border-primary-600/50 transition-colors">
            <div className="text-primary-500 mb-3 flex justify-center">{icon}</div>
            <h3 className="text-white font-semibold mb-2">{title}</h3>
            <p className="text-gray-400 text-sm">{description}</p>
        </div>
    )
}

// Message Bubble
function MessageBubble({ message, onAction }) {
    if (message.type === 'system') {
        return (
            <div className="text-center py-2">
                <span className="text-gray-500 text-sm bg-zinc-800/50 px-3 py-1 rounded-full">
                    {message.content}
                </span>
            </div>
        )
    }

    const isBot = message.type === 'bot'

    return (
        <div className={`flex items-start gap-3 ${isBot ? '' : 'flex-row-reverse'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isBot ? 'bg-primary-600' : 'bg-zinc-700'
                }`}>
                {isBot ? <Bot className="w-4 h-4 text-white" /> : <User className="w-4 h-4 text-white" />}
            </div>
            <div className={`max-w-[80%] ${isBot ? '' : 'text-right'}`}>
                <div className={`p-4 rounded-2xl ${isBot
                        ? message.isError
                            ? 'bg-red-500/10 border border-red-500/30'
                            : 'bg-zinc-800'
                        : 'bg-primary-600'
                    }`}>
                    <div className="text-white whitespace-pre-wrap text-sm leading-relaxed prose prose-invert prose-sm max-w-none"
                        dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }} />

                    {message.actions && (
                        <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-zinc-700">
                            {message.actions.map((action, i) => (
                                <button
                                    key={i}
                                    onClick={() => onAction(action)}
                                    className="px-3 py-1.5 bg-primary-600/20 hover:bg-primary-600/40 text-primary-400 rounded-lg text-sm flex items-center gap-1 transition-colors"
                                >
                                    {action.action === 'train' ? <Play className="w-3 h-3" /> : <BarChart3 className="w-3 h-3" />}
                                    {action.label}
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

// Format message with markdown-like syntax
function formatMessage(text) {
    if (!text) return ''
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/_(.*?)_/g, '<em>$1</em>')
        .replace(/\n/g, '<br/>')
}

// Results View
function ResultsView({ results, onBack, onNewTraining }) {
    const isComparison = results.comparison

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <button onClick={onBack} className="text-gray-400 hover:text-white flex items-center gap-2">
                    <ArrowLeft className="w-4 h-4" /> Back to Chat
                </button>
                <button onClick={onNewTraining} className="btn-secondary flex items-center gap-2">
                    <RefreshCw className="w-4 h-4" /> Train Another
                </button>
            </div>

            {isComparison ? (
                // Comparison Results
                <div>
                    <div className="card mb-6">
                        <div className="flex items-center gap-4">
                            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                                <Target className="w-8 h-8 text-white" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white">Best Model: {results.best_model?.name?.replace('_', ' ').toUpperCase()}</h2>
                                <p className="text-gray-400">
                                    Accuracy: {(results.best_model?.metrics?.accuracy * 100)?.toFixed(1)}% |
                                    F1: {(results.best_model?.metrics?.f1_score * 100)?.toFixed(1)}%
                                </p>
                            </div>
                        </div>
                    </div>

                    {results.chart && (
                        <div className="card">
                            <h3 className="text-lg font-semibold text-white mb-4">Model Comparison</h3>
                            <img src={results.chart} alt="Model Comparison" className="w-full rounded-lg" />
                        </div>
                    )}
                </div>
            ) : (
                // Single Model Results
                <div>
                    <div className="card mb-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <h2 className="text-2xl font-bold text-white">
                                    {results.model_name?.replace('_', ' ').toUpperCase()}
                                </h2>
                                <p className="text-gray-400">
                                    {results.task_type?.charAt(0).toUpperCase() + results.task_type?.slice(1)} •
                                    Trained in {results.training_time_seconds}s
                                </p>
                            </div>
                            <div className="text-right">
                                <div className="text-4xl font-bold text-green-400">
                                    {results.task_type === 'classification'
                                        ? `${(results.metrics?.accuracy * 100)?.toFixed(1)}%`
                                        : results.metrics?.r2_score?.toFixed(3)
                                    }
                                </div>
                                <div className="text-gray-400">
                                    {results.task_type === 'classification' ? 'Accuracy' : 'R² Score'}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        {Object.entries(results.metrics || {}).filter(([k]) => k !== 'confusion_matrix').map(([key, value]) => (
                            <div key={key} className="card text-center">
                                <div className="text-2xl font-bold text-white">
                                    {typeof value === 'number' ? (value > 1 ? value.toFixed(2) : (value * 100).toFixed(1) + '%') : value}
                                </div>
                                <div className="text-gray-400 text-sm">{key.replace('_', ' ').toUpperCase()}</div>
                            </div>
                        ))}
                    </div>

                    {/* CV Scores */}
                    {results.cv_scores && (
                        <div className="card mb-6">
                            <h3 className="text-lg font-semibold text-white mb-3">Cross-Validation</h3>
                            <div className="flex items-center gap-4">
                                <div className="text-3xl font-bold text-primary-400">{(results.cv_scores.mean * 100).toFixed(1)}%</div>
                                <div className="text-gray-400">± {(results.cv_scores.std * 100).toFixed(1)}%</div>
                            </div>
                        </div>
                    )}

                    {/* Feature Importance */}
                    {results.feature_importance && Object.keys(results.feature_importance).length > 0 && (
                        <div className="card mb-6">
                            <h3 className="text-lg font-semibold text-white mb-4">Feature Importance</h3>
                            <div className="space-y-3">
                                {Object.entries(results.feature_importance).slice(0, 10).map(([feature, importance], i) => (
                                    <div key={feature} className="flex items-center gap-3">
                                        <span className="text-gray-400 text-sm w-4">{i + 1}</span>
                                        <span className="text-white flex-1 truncate">{feature}</span>
                                        <div className="w-32 h-2 bg-zinc-800 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-gradient-to-r from-primary-600 to-purple-600 rounded-full"
                                                style={{ width: `${importance * 100}%` }}
                                            />
                                        </div>
                                        <span className="text-gray-400 text-sm w-16 text-right">{(importance * 100).toFixed(1)}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Charts */}
                    {results.charts?.summary && (
                        <div className="card">
                            <h3 className="text-lg font-semibold text-white mb-4">Training Summary</h3>
                            <img src={results.charts.summary} alt="Training Summary" className="w-full rounded-lg" />
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
