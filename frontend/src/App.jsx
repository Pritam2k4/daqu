import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useState } from 'react'
import Layout from './components/layout/Layout'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import ConnectDatabase from './pages/ConnectDatabase'
import ModelStudio from './pages/ModelStudio'

function App() {
    // Global state for current analysis
    const [currentReport, setCurrentReport] = useState(null)
    const [currentSourceId, setCurrentSourceId] = useState(null)

    return (
        <Router>
            <Layout>
                <Routes>
                    <Route path="/" element={
                        <Home
                            setCurrentReport={setCurrentReport}
                            setCurrentSourceId={setCurrentSourceId}
                        />
                    } />
                    <Route path="/dashboard" element={
                        <Dashboard
                            externalReport={currentReport}
                            sourceId={currentSourceId}
                        />
                    } />
                    <Route path="/upload" element={
                        <Upload
                            setCurrentReport={setCurrentReport}
                            setCurrentSourceId={setCurrentSourceId}
                        />
                    } />
                    <Route path="/connect-database" element={
                        <ConnectDatabase
                            setCurrentReport={setCurrentReport}
                            setCurrentSourceId={setCurrentSourceId}
                        />
                    } />
                    <Route path="/model-studio" element={
                        <ModelStudio
                            sourceId={currentSourceId}
                        />
                    } />
                </Routes>
            </Layout>
        </Router>
    )
}

export default App
