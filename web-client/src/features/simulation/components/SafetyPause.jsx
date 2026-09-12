import { Hand, ShieldCheck, XCircle } from 'lucide-react'
import { useState } from 'react'
import { decideOperation } from '../../../shared/api/client.js'
import { formatMoney, formatTime } from '../../../shared/lib/ui.js'

export function SafetyPause({ operation, pendingCount = 0, onDecision }) {
  const [saving, setSaving] = useState(null)
  const [error, setError] = useState(null)

  if (!operation) return null

  const choose = async (decision) => {
    if (saving) return
    setSaving(decision)
    setError(null)
    try {
      await decideOperation(operation.id, decision)
      await onDecision?.()
    } catch (requestError) {
      setError(
        requestError?.response?.status === 409
          ? 'Esta operación ya fue decidida. Actualizando feed.'
          : 'No se pudo guardar tu decisión. Intenta de nuevo.',
      )
      if (requestError?.response?.status === 409) await onDecision?.()
    } finally {
      setSaving(null)
    }
  }

  return (
    <section className="rounded-2xl border border-rose-800/40 bg-rose-950/40 backdrop-blur-sm p-5 transition-all duration-300 ease-out">
      <div className="flex items-center gap-2.5">
        <span className="grid place-items-center size-10 rounded-xl bg-rose-950/60 border border-rose-800/40">
          <Hand className="size-5 text-rose-400" />
        </span>
        <div>
          <h2 className="font-sans text-base font-bold text-rose-200">Pausa de seguridad</h2>
          <p className="font-sans text-xs text-rose-300/80">
            Antes de continuar, respira y verifica.
          </p>
          {pendingCount > 1 && (
            <p className="font-sans text-xs text-rose-300/70 mt-1">
              Hay {pendingCount} operaciones en pausa; se muestra la más reciente.
            </p>
          )}
        </div>
      </div>

      <p className="font-sans text-sm text-slate-200 mt-3">
        Detectamos una transferencia de{' '}
        <span className="font-mono tabular-nums font-bold">{formatMoney(operation.amount)}</span>{' '}
        con puntaje{' '}
        <span className="font-mono tabular-nums font-bold text-rose-400">{operation.risk.score}/100</span>{' '}
        <span className="font-mono tabular-nums text-slate-400">({formatTime(operation.occurred_at)})</span>.
      </p>

      <blockquote className="mt-3 rounded-xl border border-rose-800/40 bg-slate-950/40 px-4 py-3">
        <p className="font-sans text-sm font-semibold text-slate-100">
          “¿Conoces a esta persona en la vida real? ¿Fuiste tú quien decidió este envío, sin
          presión por teléfono o mensaje?”
        </p>
      </blockquote>

      <p className="font-sans text-xs text-slate-400 mt-3">
        Los fraudes de ingeniería social funcionan con prisa. Si alguien dice ser tu banco y te
        pide transferir para “verificar” tu cuenta, cuelga y marca tú al número oficial.
      </p>

      <div className="mt-4 grid gap-2 sm:grid-cols-2">
        <button
          type="button"
          onClick={() => choose('cancelled')}
          disabled={Boolean(saving)}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-rose-700/60 bg-rose-500/10 px-3 py-2.5 font-sans text-xs font-bold text-rose-200 hover:bg-rose-500/20 disabled:opacity-60"
        >
          <XCircle className="size-4" />
          {saving === 'cancelled' ? 'Cancelando…' : 'Cancelar y revisar'}
        </button>
        <button
          type="button"
          onClick={() => choose('reported_pressure')}
          disabled={Boolean(saving)}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-amber-700/60 bg-amber-500/10 px-3 py-2.5 font-sans text-xs font-bold text-amber-100 hover:bg-amber-500/20 disabled:opacity-60"
        >
          <Hand className="size-4" />
          {saving === 'reported_pressure' ? 'Guardando…' : 'Alguien me está presionando'}
        </button>
      </div>
      <button
        type="button"
        onClick={() => choose('confirmed')}
        disabled={Boolean(saving)}
        className="mt-2 inline-flex items-center gap-1.5 font-sans text-xs text-slate-400 hover:text-slate-200 disabled:opacity-60"
      >
        <ShieldCheck className="size-3.5" />
        {saving === 'confirmed' ? 'Confirmando…' : 'Confirmar que conozco el destino'}
      </button>
      {error && <p className="font-sans text-xs text-rose-300 mt-2">{error}</p>}
    </section>
  )
}
