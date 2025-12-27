import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout from './components/layout/Layout'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import ConnectDatabase from './pages/ConnectDatabase'
import ModelStudio from './pages/ModelStudio'
import Login from './pages/Login'

// Protected Route wrapper
function ProtectedRoute({ children }) {
    const { isAuthenticated, loading } = useAuth()

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        )
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />
    }

    return children
}

function AppRoutes() {
    // Global state for current analysis
    const [currentReport, setCurrentReport] = useState(null)
    const [currentSourceId, setCurrentSourceId] = useState(null)
    const { isAuthenticated } = useAuth()

    return (
        <Routes>
            {/* Public route */}
            <Route path="/login" element={
                isAuthenticated ? <Navigate to="/" replace /> : <Login />
            } />

            {/* Protected routes */}
            <Route path="/" element={
                <ProtectedRoute>
                    <Layout>
                        <Home
                            setCurrentReport={setCurrentReport}
                            setCurrentSourceId={setCurrentSourceId}
                        />
                    </Layout>
                </ProtectedRoute>
            } />
            <Route path="/dashboard" element={
                <ProtectedRoute>
                    <Layout>
                        <Dashboard
                            externalReport={currentReport}
                            sourceId={currentSourceId}
                        />
                    </Layout>
                </ProtectedRoute>
            } />
            <Route path="/upload" element={
                <ProtectedRoute>
                    <Layout>
                        <Upload
                            setCurrentReport={setCurrentReport}
                            setCurrentSourceId={setCurrentSourceId}
                        />
                    </Layout>
                </ProtectedRoute>
            } />
            <Route path="/connect-database" element={
                <ProtectedRoute>
                    <Layout>
                        <ConnectDatabase
                            setCurrentReport={setCurrentReport}
                            setCurrentSourceId={setCurrentSourceId}
                        />
                    </Layout>
                </ProtectedRoute>
            } />
            <Route path="/model-studio" element={
                <ProtectedRoute>
                    <Layout>
                        <ModelStudio
                            sourceId={currentSourceId}
                        />
                    </Layout>
                </ProtectedRoute>
            } />
        </Routes>
    )
}

function App() {
    return (
        <Router>
            <AuthProvider>
                <AppRoutes />
            </AuthProvider>
        </Router>
    )
}

export default App
