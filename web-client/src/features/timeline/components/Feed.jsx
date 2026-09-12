import { Inbox } from 'lucide-react'
import { AlertCard } from './AlertCard.jsx'

export function Feed({ operations, loading }) {
  if (loading && operations.length === 0) {
    return (
      <div className="space-y-3">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="h-28 rounded-2xl border border-slate-800/60 bg-slate-900/40 animate-pulse"
          />
        ))}
      </div>
    )
  }

  if (operations.length === 0) {
    return (
      <div className="rounded-2xl border border-slate-800/60 bg-slate-900/40 backdrop-blur-sm p-8 text-center">
        <Inbox className="size-6 text-slate-500 mx-auto" />
        <p className="font-sans text-sm text-slate-300 mt-2 font-semibold">Sin actividad todavía</p>
        <p className="font-sans text-xs text-slate-500 mt-1">
          Pulsa “Simular escenario de estafa” para ver a Guardián en acción.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {operations.map((operation) => (
        <AlertCard key={operation.id} operation={operation} />
      ))}
    </div>
  )
}
