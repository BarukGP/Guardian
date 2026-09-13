import { useMemo } from 'react'
import { Activity, AlertTriangle, CheckCircle2, TrendingUp } from 'lucide-react'
import { cn } from '../../../shared/lib/ui.js'

function KpiCard({ icon: Icon, label, value, sub, variant = 'default', pulse = false }) {
  const variants = {
    default: { card: 't-surface t-border',    icon: 't-surface-2 t-border t-muted',     value: 't-text',        sub: 't-soft' },
    alert:   { card: 't-alert-bg t-alert-border', icon: 't-surface t-alert-border t-alert-accent', value: 't-alert-accent', sub: 't-alert-accent' },
    safe:    { card: 't-safe-bg t-safe-border',   icon: 't-surface t-safe-border t-safe-accent',   value: 't-safe-accent',  sub: 't-safe-accent' },
    warn:    { card: 't-alert-bg t-alert-border', icon: 't-surface t-alert-border t-alert-accent', value: 't-alert-accent', sub: 't-alert-accent' },
    high:    { card: 't-high-bg t-high-border',   icon: 't-surface t-high-border t-high-accent',   value: 't-high-accent',  sub: 't-high-accent' },
  }
  const v = variants[variant] ?? variants.default

  return (
    <div className={cn('rounded-2xl border p-4 flex items-start gap-3 t-shadow transition-all duration-300', v.card)}>
      <span className={cn('grid size-8 shrink-0 place-items-center rounded-xl border', v.icon)}>
        <Icon className={cn('size-4', pulse && 'animate-pulse')} />
      </span>
      <div className="min-w-0">
        <p className="text-[11px] font-semibold uppercase tracking-wider t-soft">{label}</p>
        <p className={cn('mt-1 text-xl font-bold font-mono tabular-nums leading-none', v.value)}>{value}</p>
        {sub && <p className={cn('mt-1 text-[11px] leading-tight opacity-75', v.sub)}>{sub}</p>}
      </div>
    </div>
  )
}

export function KpiCards({ operations }) {
  const stats = useMemo(() => {
    const total   = operations.length
    const high    = operations.filter((o) => o?.risk?.level === 'high').length
    const safe    = operations.filter((o) => o?.risk?.level === 'low').length
    const medium  = operations.filter((o) => o?.risk?.level === 'medium').length
    const pending = operations.filter((o) => o?.status === 'pending_review').length
    const scores  = operations.map((o) => o?.risk?.score ?? 0)
    const maxScore = scores.length ? Math.max(...scores) : 0
    return { total, high, safe, medium, pending, maxScore }
  }, [operations])

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <KpiCard icon={Activity}      label="Operaciones" value={stats.total}    sub="en el feed"                                              variant="default" />
      <KpiCard icon={AlertTriangle} label="Alto riesgo" value={stats.high}     sub={stats.pending > 0 ? `${stats.pending} en pausa` : 'sin pausa activa'} variant={stats.high > 0 ? 'high' : 'default'} pulse={stats.pending > 0} />
      <KpiCard icon={CheckCircle2}  label="Normales"    value={stats.safe}     sub={`${stats.medium} en revisión`}                          variant={stats.safe > 0 ? 'safe' : 'default'} />
      <KpiCard icon={TrendingUp}    label="Score máx."  value={stats.maxScore} sub="sobre 100 pts"                                          variant={stats.maxScore >= 60 ? 'high' : stats.maxScore >= 25 ? 'warn' : 'safe'} />
    </div>
  )
}
