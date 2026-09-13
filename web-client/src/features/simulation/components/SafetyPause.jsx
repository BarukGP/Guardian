import { AlertTriangle, Hand, ShieldCheck, XCircle } from 'lucide-react'
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
          ? 'Esta operación ya fue decidida. Actualizando…'
          : 'No se pudo guardar tu decisión. Intenta de nuevo.',
      )
      if (requestError?.response?.status === 409) await onDecision?.()
    } finally {
      setSaving(null)
    }
  }

  return (
    <section className="rounded-2xl border t-alert-border t-alert-bg overflow-hidden t-shadow">
      {/* Banner */}
      <div className="border-b t-alert-border px-5 py-3 flex items-center gap-3"
        style={{ backgroundColor: 'color-mix(in srgb, var(--alert) 12%, var(--surface))' }}>
        <span className="grid size-8 place-items-center rounded-xl t-surface border t-alert-border">
          <Hand className="size-4 t-alert-accent" />
        </span>
        <div>
          <h2 className="text-sm font-bold t-alert-text">⚠️ Pausa de seguridad activa</h2>
          <p className="text-[11px] t-alert-accent opacity-80">
            {pendingCount > 1
              ? `${pendingCount} operaciones en pausa · mostrando la más reciente`
              : 'Una transferencia está detenida esperando tu decisión'}
          </p>
        </div>
      </div>

      <div className="p-5">
        {/* Operation details */}
        <div className="rounded-xl border t-border t-surface px-4 py-3 mb-4 t-shadow">
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div>
              <p className="text-xs t-soft mb-0.5">Transferencia detectada</p>
              <p className="text-xl font-mono font-bold tabular-nums t-text">
                {formatMoney(operation.amount)}
              </p>
              {operation.payee_name && (
                <p className="text-xs t-muted mt-0.5">Hacia: {operation.payee_name}</p>
              )}
              <p className="text-[11px] t-soft font-mono mt-0.5">{formatTime(operation.occurred_at)}</p>
            </div>
            <div className="text-center">
              <p className="text-[11px] t-alert-accent font-semibold uppercase tracking-wide">Puntaje de riesgo</p>
              <p className="text-3xl font-mono font-bold tabular-nums t-alert-accent">
                {operation.risk.score}
                <span className="text-sm opacity-50">/100</span>
              </p>
            </div>
          </div>
        </div>

        {/* Key question */}
        <div className="rounded-xl border t-alert-border px-4 py-3.5 mb-4"
          style={{ backgroundColor: 'color-mix(in srgb, var(--alert) 8%, var(--surface))' }}>
          <p className="text-sm font-bold t-alert-text leading-snug">
            "¿Conoces a esta persona en la vida real? ¿Fuiste <em>tú</em> quien decidió este envío, sin presión por teléfono o mensaje?"
          </p>
        </div>

        {/* Tip */}
        <div className="flex items-start gap-2.5 mb-5">
          <AlertTriangle className="size-3.5 t-alert-accent shrink-0 mt-0.5" />
          <p className="text-[11px] t-muted leading-relaxed">
            Los fraudes de ingeniería social usan la <strong className="t-text">urgencia</strong> como herramienta. Si alguien dice ser tu banco y te pide transferir para "verificar" tu cuenta, cuelga y llama tú al número oficial.
          </p>
        </div>

        {/* Buttons */}
        <div className="grid gap-2.5">
          <div className="grid gap-2 sm:grid-cols-2">
            <button
              type="button"
              onClick={() => choose('cancelled')}
              disabled={Boolean(saving)}
              className="flex items-center justify-center gap-2 rounded-xl border t-high-border t-high-bg px-4 py-3 text-sm font-bold t-high-text hover:opacity-80 active:scale-[0.98] disabled:opacity-60 transition-all"
            >
              <XCircle className="size-4" />
              {saving === 'cancelled' ? 'Cancelando…' : 'Cancelar transferencia'}
            </button>
            <button
              type="button"
              onClick={() => choose('reported_pressure')}
              disabled={Boolean(saving)}
              className="flex items-center justify-center gap-2 rounded-xl border t-alert-border t-alert-bg px-4 py-3 text-sm font-bold t-alert-text hover:opacity-80 active:scale-[0.98] disabled:opacity-60 transition-all"
            >
              <Hand className="size-4" />
              {saving === 'reported_pressure' ? 'Guardando…' : 'Me están presionando'}
            </button>
          </div>
          <button
            type="button"
            onClick={() => choose('confirmed')}
            disabled={Boolean(saving)}
            className="flex items-center justify-center gap-1.5 rounded-xl border t-safe-border t-safe-bg px-4 py-2.5 text-xs font-medium t-safe-text hover:opacity-80 active:scale-[0.98] disabled:opacity-60 transition-all"
          >
            <ShieldCheck className="size-3.5" />
            {saving === 'confirmed' ? 'Confirmando…' : 'Sí, reconozco este envío — confirmar'}
          </button>
        </div>

        {error && <p className="text-xs t-high-text mt-3 text-center">{error}</p>}
      </div>
    </section>
  )
}
