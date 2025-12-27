import { useState } from 'react'
import { Upload as UploadIcon, Database } from 'lucide-react'
import { api } from '../services/api'

export default function Upload() {
    const [uploading, setUploading] = useState(false)
    const [message, setMessage] = useState('')
    const [dragActive, setDragActive] = useState(false)

    const handleDrag = (e) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true)
        } else if (e.type === "dragleave") {
            setDragActive(false)
        }
    }

    const handleDrop = async (e) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            await handleFileUpload(e.dataTransfer.files[0])
        }
    }

    const handleFileChange = async (e) => {
        if (e.target.files && e.target.files[0]) {
            await handleFileUpload(e.target.files[0])
        }
    }

    const handleFileUpload = async (file) => {
        setUploading(true)
        setMessage('')

        try {
            const result = await api.uploadFile(file)
            setMessage(`✅ Success: ${result.message || 'File uploaded!'} - ${result.filename}`)
            console.log('Upload result:', result)
        } catch (error) {
            setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`)
            console.error('Upload error:', error)
        } finally {
            setUploading(false)
        }
    }

    const handleDatabaseConnect = async () => {
        setUploading(true)
        setMessage('')

        try {
            const result = await api.connectDatabase({
                type: 'postgresql',
                host: 'localhost',
                port: 5432
            })
            setMessage(`✅ ${result.message || 'Database connection initiated!'}`)
            console.log('Database result:', result)
        } catch (error) {
            setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`)
            console.error('Database error:', error)
        } finally {
            setUploading(false)
        }
    }

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold text-white mb-8">Upload Data</h1>

                {/* Status Message */}
                {message && (
                    <div className="mb-6 bg-zinc-900/80 border border-zinc-800 rounded-lg px-6 py-4">
                        <p className="text-white">{message}</p>
                    </div>
                )}

                {/* File Upload Area */}
                <div
                    className={`card border-2 border-dashed ${dragActive ? 'border-primary-600 bg-primary-600/5' : 'border-zinc-700'} hover:border-primary-600 transition-all duration-300 cursor-pointer mb-8`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => document.getElementById('file-input').click()}
                >
                    <div className="text-center py-12">
                        <div className={`w-16 h-16 rounded-full bg-primary-600/10 flex items-center justify-center mx-auto mb-4 ${uploading ? 'animate-pulse' : ''}`}>
                            <UploadIcon className="w-8 h-8 text-primary-500" />
                        </div>
                        <h3 className="text-xl font-semibold text-white mb-2">
                            {uploading ? 'Uploading...' : 'Drop your files here or click to browse'}
                        </h3>
                        <p className="text-gray-400 text-sm">
                            Supports CSV, Excel, and JSON files up to 100MB
                        </p>
                    </div>
                    <input
                        id="file-input"
                        type="file"
                        className="hidden"
                        accept=".csv,.xlsx,.xls,.json"
                        onChange={handleFileChange}
                        disabled={uploading}
                    />
                </div>

                {/* Or Divider */}
                <div className="relative my-8">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-zinc-800"></div>
                    </div>
                    <div className="relative flex justify-center text-sm">
                        <span className="px-4 bg-black text-gray-400">OR</span>
                    </div>
                </div>

                {/* Database Connection */}
                <button
                    onClick={handleDatabaseConnect}
                    disabled={uploading}
                    className="w-full card hover:border-primary-600 transition-all duration-300 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <div className="flex items-center space-x-4">
                        <div className={`w-14 h-14 rounded-full bg-primary-600/10 flex items-center justify-center ${uploading ? 'animate-pulse' : ''}`}>
                            <Database className="w-7 h-7 text-primary-500" />
                        </div>
                        <div className="text-left">
                            <h3 className="text-lg font-semibold text-white mb-1">
                                {uploading ? 'Connecting...' : 'Connect to Database'}
                            </h3>
                            <p className="text-gray-400 text-sm">
                                PostgreSQL, MySQL, MongoDB
                            </p>
                        </div>
                    </div>
                </button>
            </div>
        </div>
    )
}
