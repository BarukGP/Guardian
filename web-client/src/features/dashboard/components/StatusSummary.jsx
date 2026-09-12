import { useMemo, useState } from 'react'
import { Activity, RotateCcw } from 'lucide-react'
import { Area, AreaChart, ResponsiveContainer, Tooltip } from 'recharts'
import { SimulateButton } from '../../simulation/components/SimulateButton.jsx'
import { resetDemo } from '../../../shared/api/client.js'
import { LEVEL_STYLES, cn } from '../../../shared/lib/ui.js'

export function StatusSummary({ operations, onSimulated, onReset, readOnly = false }) {
  const [resetting, setResetting] = useState(false)
  const [resetError, setResetError] = useState(null)
  const stats = useMemo(() => {
    const high = operations.filter((a) => a?.risk?.level === 'high').length
    const scores = operations.map((a) => a?.risk?.score ?? 0)
    const max = scores.length ? Math.max(...scores) : 0
    const level = max >= 60 ? 'high' : max >= 25 ? 'medium' : 'low'
    const trend = [...operations]
      .reverse()
      .slice(-20)
      .map((a, i) => ({ i, score: a?.risk?.score ?? 0 }))
    return { high, max, level, trend }
  }, [operations])

  const style = LEVEL_STYLES[stats.level]

  const handleReset = async () => {
    if (resetting) return
    setResetting(true)
    setResetError(null)
    try {
      await resetDemo()
      await onReset?.()
    } catch {
      setResetError('No se pudo reiniciar el escenario local.')
    } finally {
      setResetting(false)
    }
  }

  return (
    <section className="border border-slate-800/60 bg-slate-900/40 backdrop-blur-sm rounded-2xl p-5 transition-all duration-300 ease-out">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <p className="font-sans text-xs uppercase tracking-widest text-slate-400 flex items-center gap-1.5">
            <Activity className="size-3.5" /> Riesgo máximo en el feed
          </p>
          <p className="mt-1 flex items-baseline gap-2">
            <span className={cn('font-mono tabular-nums text-4xl font-bold', style.text)}>
              {stats.max}
            </span>
            <span className="font-sans text-xs text-slate-400">/ 100</span>
            <span
              className={cn(
                'font-sans text-xs font-bold px-2 py-0.5 rounded-full border',
                style.text,
                style.bg,
                style.border,
              )}
            >
              {style.label}
            </span>
          </p>
          <p className="font-sans text-xs text-slate-400 mt-1">
            <span className="font-mono tabular-nums text-slate-200">{stats.high}</span>{' '}
            alertas prioritarias en el feed
          </p>
        </div>
        <div className="h-24 w-full sm:w-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={stats.trend} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="riskTrend" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#f43f5e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <Tooltip
                contentStyle={{
                  background: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: 12,
                  fontSize: 12,
                }}
                labelFormatter={() => 'Evento'}
                formatter={(v) => [v, 'Score']}
              />
              <Area
                type="monotone"
                dataKey="score"
                stroke="#fb7185"
                strokeWidth={2}
                fill="url(#riskTrend)"
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
      {readOnly ? (
        <p className="mt-5 rounded-xl border border-sky-800/40 bg-sky-950/20 px-3 py-2 text-center font-sans text-xs text-sky-200">
          Vista de analista: puedes auditar actividad y casos, pero no iniciar ni resolver transferencias.
        </p>
      ) : (
        <>
          <div className="mt-4">
            <SimulateButton onDone={onSimulated} />
          </div>
          <div className="mt-2 text-center">
            <button
              type="button"
              onClick={handleReset}
              disabled={resetting}
              className="inline-flex items-center gap-1.5 font-sans text-xs text-slate-400 hover:text-slate-200 disabled:opacity-60 transition-colors"
            >
              <RotateCcw className={cn('size-3.5', resetting && 'animate-spin')} />
              {resetting ? 'Reiniciando…' : 'Reiniciar demo'}
            </button>
            {resetError && <p className="font-sans text-xs text-rose-400 mt-1">{resetError}</p>}
          </div>
        </>
      )}
    </section>
  )
}
