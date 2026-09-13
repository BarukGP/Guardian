import { useEffect, useMemo, useState } from 'react'
import { Activity, BadgeAlert, LayoutDashboard, TriangleAlert } from 'lucide-react'
import { Header } from '../features/dashboard/components/Header.jsx'
import { StatusSummary } from '../features/dashboard/components/StatusSummary.jsx'
import { KpiCards } from '../features/dashboard/components/KpiCards.jsx'
import { SafetyPause } from '../features/simulation/components/SafetyPause.jsx'
import { Feed } from '../features/timeline/components/Feed.jsx'
import { useTimeline } from '../features/timeline/hooks/useTimeline.js'
import { useCases } from '../features/cases/hooks/useCases.js'
import { CasePanel } from '../features/cases/components/CasePanel.jsx'
import { LoginScreen } from '../features/auth/components/LoginScreen.jsx'
import { fetchMe, logout } from '../shared/api/client.js'
import { useTheme } from '../shared/hooks/useTheme.js'
import { cn } from '../shared/lib/ui.js'

// ─── Tab bar ───────────────────────────────────────────────────────────────────
const TABS = [
  { id: 'dashboard', label: 'Panel',     icon: LayoutDashboard },
  { id: 'feed',      label: 'Actividad', icon: Activity },
  { id: 'cases',     label: 'Casos',     icon: BadgeAlert },
]

function TabBar({ active, onSelect, caseCount, highCount }) {
  return (
    <nav className="flex items-center gap-1 rounded-2xl border t-border t-surface p-1 t-shadow">
      {TABS.map((tab) => {
        const Icon = tab.icon
        const badge = tab.id === 'cases' ? caseCount : tab.id === 'feed' ? highCount : 0
        const isActive = active === tab.id
        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onSelect(tab.id)}
            className="flex-1 flex items-center justify-center gap-1.5 rounded-xl px-3 py-2.5 text-xs font-semibold transition-all duration-200 no-theme-transition"
            style={isActive
              ? { backgroundColor: 'var(--primary)', color: '#ffffff', boxShadow: '0 1px 4px color-mix(in srgb, var(--primary) 30%, transparent)' }
              : { backgroundColor: 'transparent', color: 'var(--text-muted)' }
            }
            onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.backgroundColor = 'var(--surface-2)'; if (!isActive) e.currentTarget.style.color = 'var(--text)' }}
            onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.backgroundColor = 'transparent'; if (!isActive) e.currentTarget.style.color = 'var(--text-muted)' }}
          >
            <Icon className="size-3.5" />
            <span className="hidden sm:inline">{tab.label}</span>
            {badge > 0 && (
              <span
                className="rounded-full px-1.5 py-0.5 text-[9px] font-bold leading-none"
                style={{
                  backgroundColor: tab.id === 'feed'
                    ? 'color-mix(in srgb, var(--high) 15%, transparent)'
                    : 'color-mix(in srgb, var(--alert) 15%, transparent)',
                  color: tab.id === 'feed' ? 'var(--high)' : 'var(--alert)',
                }}
              >
                {badge}
              </span>
            )}
          </button>
        )
      })}
    </nav>
  )
}

// ─── Tab views ─────────────────────────────────────────────────────────────────
function DashboardTab({ operations, onSimulated, onReset, user, pendingReview, pendingCount, refreshEverything }) {
  return (
    <div className="space-y-4">
      <KpiCards operations={operations} />
      <StatusSummary operations={operations} onSimulated={onSimulated} onReset={onReset} readOnly={user.role === 'analyst'} />
      {user.role === 'customer' && (
        <SafetyPause operation={pendingReview} pendingCount={pendingCount} onDecision={refreshEverything} />
      )}
    </div>
  )
}

function FeedTab({ operations, loading }) {
  const [filter, setFilter] = useState('all')
  return <Feed operations={operations} loading={loading} filter={filter} onFilterChange={setFilter} />
}

function CasesTab({ cases }) {
  if (!cases.length) {
    return (
      <div className="rounded-2xl border t-border t-surface p-10 text-center t-shadow">
        <BadgeAlert className="size-8 t-soft mx-auto" />
        <p className="text-sm font-semibold t-text mt-3">Sin casos de protección</p>
        <p className="text-xs t-muted mt-1">Los casos aparecen cuando una operación reporta presión externa.</p>
      </div>
    )
  }
  return <CasePanel cases={cases} />
}

// ─── Main Dashboard ────────────────────────────────────────────────────────────
function Dashboard({ user, onLogout, dark, onToggleTheme }) {
  const { operations, loading, error, lastSync, refresh } = useTimeline({ intervalMs: 2500 })
  const { cases, refresh: refreshCases } = useCases(lastSync)
  const [activeTab, setActiveTab] = useState('dashboard')

  const refreshEverything = async () => {
    await Promise.all([refresh(), refreshCases()])
  }

  const pendingReviews = useMemo(
    () => operations.filter((op) => op?.risk?.level === 'high' && op?.status === 'pending_review'),
    [operations],
  )
  const pendingReview  = pendingReviews[0] ?? null
  const highCount      = useMemo(() => operations.filter((op) => op?.risk?.level === 'high').length, [operations])
  const openCaseCount  = useMemo(() => cases.filter((c) => c.status === 'open').length, [cases])

  useEffect(() => {
    if (pendingReview && user.role === 'customer') setActiveTab('dashboard')
  }, [pendingReview, user.role])

  return (
    <div className="min-h-screen t-bg font-sans antialiased">
      <div className="mx-auto w-full max-w-2xl px-4 py-5">

        <Header lastSync={lastSync} user={user} onLogout={onLogout} dark={dark} onToggleTheme={onToggleTheme} />

        {/* Error */}
        {error && (
          <div className="mt-3 rounded-2xl border t-alert-border t-alert-bg px-4 py-3 flex items-start gap-2.5">
            <TriangleAlert className="size-4 t-alert-accent shrink-0 mt-0.5" />
            <p className="text-xs t-alert-text">{error}</p>
          </div>
        )}

        {/* Safety pause banner (fuera del tab dashboard) */}
        {pendingReview && user.role === 'customer' && activeTab !== 'dashboard' && (
          <button
            type="button"
            onClick={() => setActiveTab('dashboard')}
            className="mt-3 w-full rounded-2xl border t-alert-border t-alert-bg px-4 py-3 flex items-center gap-2.5 hover:opacity-80 transition-all"
          >
            <span className="size-2 rounded-full animate-pulse shrink-0" style={{ backgroundColor: 'var(--high)' }} />
            <p className="text-xs font-bold t-alert-text text-left flex-1">
              Tienes una pausa de seguridad activa — toca para revisarla
            </p>
          </button>
        )}

        {/* Tabs */}
        <div className="mt-4">
          <TabBar active={activeTab} onSelect={setActiveTab} caseCount={openCaseCount} highCount={highCount} />
        </div>

        {/* Content */}
        <div className="mt-4 space-y-4">
          {activeTab === 'dashboard' && (
            <DashboardTab
              operations={operations}
              onSimulated={refreshEverything}
              onReset={refreshEverything}
              user={user}
              pendingReview={pendingReview}
              pendingCount={pendingReviews.length}
              refreshEverything={refreshEverything}
            />
          )}
          {activeTab === 'feed'  && <FeedTab  operations={operations} loading={loading} />}
          {activeTab === 'cases' && <CasesTab cases={cases} />}
        </div>

        <footer className="pt-6 pb-8 text-center">
          <p className="font-mono text-[10px] t-soft opacity-40">
            Guardián · Reglas explicables sobre Nessie · Demo local
          </p>
        </footer>
      </div>
    </div>
  )
}

// ─── Root ──────────────────────────────────────────────────────────────────────
function App() {
  const [user, setUser]                     = useState(null)
  const [checkingSession, setCheckingSession] = useState(true)
  const { dark, toggle }                    = useTheme()

  useEffect(() => {
    if (!localStorage.getItem('guardian_session')) { setCheckingSession(false); return }
    fetchMe()
      .then(setUser)
      .catch(() => localStorage.removeItem('guardian_session'))
      .finally(() => setCheckingSession(false))
  }, [])

  const handleLogout = async () => {
    await logout()
    setUser(null)
  }

  if (checkingSession) return <div className="min-h-screen t-bg" />
  if (!user) return <LoginScreen onLogin={setUser} />
  return <Dashboard user={user} onLogout={handleLogout} dark={dark} onToggleTheme={toggle} />
}

export default App
