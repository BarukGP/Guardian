import { useEffect, useMemo, useState } from 'react'
import { TriangleAlert } from 'lucide-react'
import { Header } from '../features/dashboard/components/Header.jsx'
import { StatusSummary } from '../features/dashboard/components/StatusSummary.jsx'
import { SafetyPause } from '../features/simulation/components/SafetyPause.jsx'
import { Feed } from '../features/timeline/components/Feed.jsx'
import { useTimeline } from '../features/timeline/hooks/useTimeline.js'
import { useCases } from '../features/cases/hooks/useCases.js'
import { CasePanel } from '../features/cases/components/CasePanel.jsx'
import { LoginScreen } from '../features/auth/components/LoginScreen.jsx'
import { fetchMe, logout } from '../shared/api/client.js'

function Dashboard({ user, onLogout }) {
  const { operations, loading, error, lastSync, refresh } = useTimeline({ intervalMs: 2500 })
  const { cases, refresh: refreshCases } = useCases(lastSync)

  const refreshEverything = async () => {
    await Promise.all([refresh(), refreshCases()])
  }

  const pendingReviews = useMemo(
    () => operations.filter(
      (operation) => operation?.risk?.level === 'high' && operation?.status === 'pending_review',
    ),
    [operations],
  )
  const pendingReview = pendingReviews[0] ?? null

  return (
    <div className="min-h-screen bg-[#0a0f1d] font-sans text-slate-200 antialiased">
      <div className="mx-auto w-full max-w-3xl px-4 py-5 space-y-4">
        <Header lastSync={lastSync} user={user} onLogout={onLogout} />

        {error && (
          <div className="rounded-2xl border border-amber-800/40 bg-amber-950/40 backdrop-blur-sm px-4 py-3 flex items-start gap-2.5 transition-all duration-300 ease-out">
            <TriangleAlert className="size-4 text-amber-400 shrink-0 mt-0.5" />
            <p className="font-sans text-xs text-amber-200">{error}</p>
          </div>
        )}

        <StatusSummary operations={operations} onSimulated={refreshEverything} onReset={refreshEverything} readOnly={user.role === 'analyst'} />

        {user.role === 'customer' && (
          <SafetyPause operation={pendingReview} pendingCount={pendingReviews.length} onDecision={refreshEverything} />
        )}
        <CasePanel cases={cases} />

        <section>
          <h2 className="font-sans text-xs uppercase tracking-widest text-slate-400 mb-2">
            Vigilancia en vivo
          </h2>
          <Feed operations={operations} loading={loading} />
        </section>

        <footer className="pt-2 pb-6 text-center">
          <p className="font-mono tabular-nums text-[11px] text-slate-600">
            Guardián · Reglas explicables sobre Nessie · Demo local
          </p>
        </footer>
      </div>
    </div>
  )
}

function App() {
  const [user, setUser] = useState(null)
  const [checkingSession, setCheckingSession] = useState(true)

  useEffect(() => {
    if (!localStorage.getItem('guardian_session')) {
      setCheckingSession(false)
      return
    }
    fetchMe().then(setUser).catch(() => localStorage.removeItem('guardian_session')).finally(() => setCheckingSession(false))
  }, [])

  const handleLogout = async () => {
    await logout()
    setUser(null)
  }

  if (checkingSession) return <div className="min-h-screen bg-[#0a0f1d]" />
  if (!user) return <LoginScreen onLogin={setUser} />
  return <Dashboard user={user} onLogout={handleLogout} />
}

export default App
