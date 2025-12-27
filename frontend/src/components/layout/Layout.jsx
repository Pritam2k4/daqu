import Header from './Header'
import FloatingChat from '../FloatingChat'

export default function Layout({ children }) {
    return (
        <div className="min-h-screen bg-black">
            <Header />
            <main className="pt-20">
                {children}
            </main>
            <FloatingChat />
        </div>
    )
}
