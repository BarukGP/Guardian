import { useMemo, useState } from 'react'
import { RotateCcw } from 'lucide-react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, YAxis } from 'recharts'
import { SimulateButton } from '../../simulation/components/SimulateButton.jsx'
import { resetDemo } from '../../../shared/api/client.js'
import { LEVEL_STYLES, cn } from '../../../shared/lib/ui.js'

export function StatusSummary({ operations, onSimulated, onReset, readOnly = false }) {
  const [resetting, setResetting] = useState(false)
  const [resetError, setResetError] = useState(null)

  const stats = useMemo(() => {
    const scores = operations.map((a) => a?.risk?.score ?? 0)
    const max    = scores.length ? Math.max(...scores) : 0
    const level  = max >= 60 ? 'high' : max >= 25 ? 'medium' : 'low'
    const trend  = [...operations].reverse().slice(-20).map((a, i) => ({ i: i + 1, score: a?.risk?.score ?? 0 }))
    return { max, level, trend }
  }, [operations])

  const style = LEVEL_STYLES[stats.level]

  // Color del gráfico según nivel — usa CSS var directamente
  const chartColorVar = stats.level === 'high' ? 'var(--high)' : stats.level === 'medium' ? 'var(--alert)' : 'var(--safe)'

  const handleReset = async () => {
    if (resetting) return
    setResetting(true)
    setResetError(null)
    try {
      await resetDemo()
      await onReset?.()
    } catch {
      setResetError('No se pudo reiniciar el escenario.')
    } finally {
      setResetting(false)
    }
  }

  return (
    <div className="rounded-2xl border t-border t-surface t-shadow p-5 transition-all duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center gap-5">
        {/* Score */}
        <div className="shrink-0">
          <p className="text-[11px] font-bold uppercase tracking-wider t-soft mb-2">
            Riesgo máximo detectado
          </p>
          <div className="flex items-end gap-3">
            <span className={cn('font-mono tabular-nums text-5xl font-bold leading-none', style.text)}>
              {stats.max}
            </span>
            <div className="pb-1">
              <span className="text-sm t-soft font-mono">/ 100</span>
              <div className={cn('mt-1 inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-bold', style.pill)}>
                <span className={cn('size-1.5 rounded-full', style.dot)} />
                {style.label}
              </div>
            </div>
          </div>
        </div>

        {/* Trend chart */}
        <div className="flex-1 h-20 min-w-0">
          {stats.trend.length > 1 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats.trend} margin={{ top: 2, right: 2, bottom: 0, left: -20 }}>
                <defs>
                  <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={chartColorVar} stopOpacity={0.28} />
                    <stop offset="100%" stopColor={chartColorVar} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 9, fill: 'var(--text-soft)' }} width={28} />
                <Tooltip
                  contentStyle={{
                    background: 'var(--surface)',
                    border: '1px solid var(--border)',
                    borderRadius: 10,
                    fontSize: 11,
                    color: 'var(--text)',
                  }}
                  labelFormatter={(v) => `Evento #${v}`}
                  formatter={(v) => [`${v} pts`, 'Score']}
                />
                <Area
                  type="monotone"
                  dataKey="score"
                  stroke={chartColorVar}
                  strokeWidth={2}
                  fill="url(#trendGrad)"
                  isAnimationActive={false}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full rounded-xl border t-border t-surface-2 flex items-center justify-center">
              <p className="text-[11px] t-soft">Simula para ver la tendencia</p>
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      {readOnly ? (
        <div className="mt-4 rounded-xl border t-border t-primary-light px-3 py-2.5 flex items-center gap-2"
          style={{ borderColor: 'color-mix(in srgb, var(--primary) 30%, transparent)' }}>
          <span className="size-1.5 rounded-full t-primary-bg shrink-0" style={{ backgroundColor: 'var(--primary)' }} />
          <p className="text-xs t-primary-text">
            Vista de analista — puedes auditar actividad y casos, pero no iniciar ni resolver transferencias.
          </p>
        </div>
      ) : (
        <div className="mt-4 flex flex-col sm:flex-row gap-2.5">
          <div className="flex-1">
            <SimulateButton onDone={onSimulated} />
          </div>
          <button
            type="button"
            onClick={handleReset}
            disabled={resetting}
            className="flex items-center justify-center gap-1.5 rounded-xl border t-border t-surface-2 px-4 py-2.5 text-xs font-medium t-muted hover:t-text hover:t-surface disabled:opacity-60 transition-all"
          >
            <RotateCcw className={cn('size-3.5', resetting && 'animate-spin')} />
            {resetting ? 'Reiniciando…' : 'Reiniciar demo'}
          </button>
        </div>
      )}
      {resetError && <p className="text-xs t-high-text mt-2 text-center">{resetError}</p>}
    </div>
  )
}
