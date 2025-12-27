import { useState, useRef, useEffect } from 'react'
import { MessageCircle, X, Send, Sparkles, Bot, User } from 'lucide-react'
import { api } from '../services/api'

export default function FloatingChat() {
    const [isOpen, setIsOpen] = useState(false)
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: "Hi! I'm your DAQU assistant. Ask me about data quality, ML training, or your uploaded datasets."
        }
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const sendMessage = async () => {
        if (!input.trim() || loading) return

        const userMessage = { role: 'user', content: input }
        setMessages(prev => [...prev, userMessage])
        setInput('')
        setLoading(true)

        try {
            const response = await api.sendAssistantMessage(input)
            if (response.status === 'success') {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: response.response
                }])
            }
        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "I'm having trouble connecting. Please try again."
            }])
        }
        setLoading(false)
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    return (
        <>
            {/* Floating Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`fixed bottom-6 left-6 z-50 w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-500 group ${isOpen
                        ? 'bg-surface-elevated border border-white/10 rotate-0'
                        : 'bg-gradient-to-br from-primary-500 to-primary-600 shadow-lg shadow-primary-500/30 hover:shadow-primary-500/50 hover:scale-105'
                    }`}
            >
                {isOpen ? (
                    <X className="w-5 h-5 text-gray-400" />
                ) : (
                    <MessageCircle className="w-6 h-6 text-surface-dark" />
                )}
                {!isOpen && (
                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse"></span>
                )}
            </button>

            {/* Chat Window */}
            {isOpen && (
                <div className="fixed bottom-24 left-6 z-50 w-[380px] max-w-[calc(100vw-48px)] animate-scale-in">
                    <div className="card p-0 overflow-hidden border-white/10">
                        {/* Header */}
                        <div className="px-5 py-4 border-b border-white/5 bg-gradient-to-r from-primary-500/10 to-transparent">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-mocha-500 flex items-center justify-center">
                                    <Sparkles className="w-5 h-5 text-surface-dark" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-white">DAQU Assistant</h3>
                                    <p className="text-xs text-gray-500">Powered by AI</p>
                                </div>
                            </div>
                        </div>

                        {/* Messages */}
                        <div className="h-80 overflow-y-auto p-4 space-y-4 scrollbar-thin">
                            {messages.map((msg, i) => (
                                <div
                                    key={i}
                                    className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''} animate-fade-in`}
                                >
                                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${msg.role === 'user'
                                            ? 'bg-primary-500/20 text-primary-500'
                                            : 'bg-surface-elevated text-gray-400'
                                        }`}>
                                        {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                                    </div>
                                    <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm ${msg.role === 'user'
                                            ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-surface-dark rounded-br-md'
                                            : 'bg-surface-elevated text-gray-300 rounded-bl-md'
                                        }`}>
                                        {msg.content}
                                    </div>
                                </div>
                            ))}
                            {loading && (
                                <div className="flex gap-3 animate-fade-in">
                                    <div className="w-8 h-8 rounded-lg bg-surface-elevated flex items-center justify-center text-gray-400">
                                        <Bot className="w-4 h-4" />
                                    </div>
                                    <div className="px-4 py-3 bg-surface-elevated rounded-2xl rounded-bl-md">
                                        <div className="flex gap-1">
                                            <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                            <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                            <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input */}
                        <div className="p-4 border-t border-white/5">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Ask anything..."
                                    className="flex-1 px-4 py-3 bg-surface-elevated border border-white/5 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-primary-500/50 text-sm transition-colors"
                                />
                                <button
                                    onClick={sendMessage}
                                    disabled={loading || !input.trim()}
                                    className="px-4 py-3 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl text-surface-dark disabled:opacity-50 hover:shadow-lg hover:shadow-primary-500/30 transition-all disabled:hover:shadow-none"
                                >
                                    <Send className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}
