import { useState } from 'react'
import { FlaskConical } from 'lucide-react'
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
          'w-full rounded-xl px-5 py-3.5 font-sans text-sm font-bold text-slate-950',
          'bg-amber-300 hover:bg-amber-200 disabled:opacity-60 disabled:cursor-wait',
          'transition-all duration-300 ease-out active:scale-[0.98]',
          'flex items-center justify-center gap-2',
        )}
      >
        <FlaskConical className={cn('size-4', running && 'animate-spin')} />
        {running ? 'Simulando movimientos…' : 'Simular escenario de estafa'}
      </button>
      {error && (
        <p className="font-sans text-xs text-rose-400 mt-2 text-center">{error}</p>
      )}
    </div>
  )
}
