import { useState } from 'react'
import { FlaskConical, Zap } from 'lucide-react'
import { runSimulation } from '../../../shared/api/client.js'
import { cn } from '../../../shared/lib/ui.js'

export function SimulateButton({ onDone }) {
  const [running, setRunning] = useState(false)
  const [error, setError] = useState(null)

  const handleClick = async () => {
    if (running) return
    setRunning(true)
    setError(null)
    try {
      const result = await runSimulation()
      onDone?.(result)
    } catch (err) {
      setError(
        err?.response?.status === 401
          ? 'Sesión expirada. Vuelve a iniciar sesión.'
          : 'No se pudo ejecutar la simulación.',
      )
    } finally {
      setRunning(false)
    }
  }

  return (
    <div>
      <button
        type="button"
        onClick={handleClick}
        disabled={running}
        className={cn(
          'w-full rounded-xl px-4 py-3 font-sans text-sm font-bold text-white',
          'disabled:opacity-60 disabled:cursor-wait',
          'transition-all duration-200 active:scale-[0.98]',
          'flex items-center justify-center gap-2 no-theme-transition',
        )}
        style={{
          backgroundColor: 'var(--primary)',
          boxShadow: '0 4px 14px color-mix(in srgb, var(--primary) 20%, transparent)',
        }}
        onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--primary-hover)' }}
        onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--primary)' }}
      >
        {running ? (
          <><FlaskConical className="size-4 animate-spin" /> Simulando…</>
        ) : (
          <><Zap className="size-4" /> Simular escenario de estafa</>
        )}
      </button>
      {error && <p className="text-xs t-high-text mt-1.5 text-center">{error}</p>}
    </div>
  )
}
