import { AlertTriangle, CheckCircle2, Eye } from 'lucide-react'
import { LEVEL_STYLES, cn, formatMoney, formatTime } from '../../../shared/lib/ui.js'

function explain(reason) {
  if (reason.includes('Beneficiario nuevo'))
    return {
      why: 'El destinatario es nuevo: nunca habías transferido a esta persona.',
      action: 'Confirma por otro canal que conoces a esta persona antes de continuar.',
    }
  if (reason.includes('Monto alto'))
    return {
      why: 'El monto supera el umbral de $10,000.',
      action: 'Confirma que fuiste tú quien autorizó esta cantidad.',
    }
  if (reason.includes('Actividad rápida'))
    return {
      why: 'Detectamos tres o más movimientos en 10 minutos.',
      action: 'Pausa sugerida: verifica que reconozcas cada cargo.',
    }
  if (reason.includes('Volumen elevado'))
    return {
      why: 'El acumulado de 10 minutos supera $5,000.',
      action: 'Revisa si estos cargos salieron de tu cuenta de forma voluntaria.',
    }
  if (reason.includes('Monto atípico'))
    return {
      why: 'El monto supera tres veces tu promedio habitual.',
      action: 'Si alguien te pidió esta transferencia por teléfono o mensaje, detente.',
    }
  if (reason.includes('Dispositivo nuevo'))
    return {
      why: 'La transferencia se inició desde un dispositivo no habitual.',
      action: 'Si no reconoces el dispositivo, cancela y revisa tus sesiones.',
    }
  if (reason.includes('Horario inusual'))
    return {
      why: 'La operación ocurre fuera de tu patrón horario habitual.',
      action: 'Si te despertaron o te metieron prisa por mensaje, detente.',
    }
  if (reason.includes('Destino señalado'))
    return {
      why: 'El beneficiario tiene señales previas de riesgo.',
      action: 'No continúes sin verificar por un canal oficial.',
    }
  return {
    why: 'Sin señales de riesgo con las reglas actuales.',
    action: 'No se requiere acción.',
  }
}

export function AlertCard({ operation }) {
  const risk = operation?.risk ?? { score: 0, level: 'low', reasons: [] }
  const style = LEVEL_STYLES[risk.level] ?? LEVEL_STYLES.low
  const Icon = risk.level === 'low' ? CheckCircle2 : risk.level === 'medium' ? Eye : AlertTriangle
  const isTransfer = operation?.kind === 'transfer'
  const statusLabel = {
    completed: 'Completada',
    pending_review: 'En pausa',
    confirmed: 'Confirmada',
    cancelled: 'Cancelada',
    reported_pressure: 'Presión reportada',
  }[operation?.status] ?? 'Registrada'

  return (
    <article
      className={cn(
        'border rounded-2xl p-4 backdrop-blur-sm',
        'border-slate-800/60 bg-slate-900/40',
        'transition-all duration-300 ease-out',
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <span className={cn('grid place-items-center size-8 rounded-lg border', style.bg, style.border)}>
            <Icon className={cn('size-4', style.text)} />
          </span>
          <div>
            <p className="font-sans text-sm font-bold text-slate-100">
              {isTransfer ? 'Transferencia' : 'Movimiento'} de{' '}
              <span className="font-mono tabular-nums">{formatMoney(operation.amount)}</span>
            </p>
            <p className="font-mono tabular-nums text-[11px] text-slate-500">
              {formatTime(operation.occurred_at)} · #{operation.id}
            </p>
            <p className="font-sans text-[11px] text-slate-400 mt-0.5">
              {operation.description}
              {operation.payee_name && ` · Destino: ${operation.payee_name}`}
            </p>
          </div>
        </div>
        <div className="text-right shrink-0">
          <p className={cn('font-mono tabular-nums text-xl font-bold leading-none', style.text)}>
            {risk.score}
          </p>
          <span
            className={cn(
              'inline-block mt-1 font-sans text-[10px] font-bold px-2 py-0.5 rounded-full border',
              style.text,
              style.bg,
              style.border,
            )}
          >
            {style.label}
          </span>
        </div>
      </div>

      <p className={cn('mt-2 font-sans text-[11px] font-bold', style.text)}>
        {statusLabel}
      </p>

      <dl className="mt-3 space-y-2">
        {(risk.reasons ?? []).map((reason, i) => {
          const { why, action } = explain(reason)
          const calm = reason.includes('No se detectaron')
          return (
            <div
              key={i}
              className={cn('rounded-xl border px-3 py-2', calm ? 'border-slate-800/60' : style.border, calm ? '' : style.bg)}
            >
              <dt className="font-sans text-[11px] font-bold uppercase tracking-wide text-slate-400">
                {calm ? 'Estado' : `Señal ${i + 1}`}
              </dt>
              <dd className="font-sans text-xs text-slate-200 mt-0.5">{why}</dd>
              {!calm && (
                <dd className={cn('font-sans text-xs mt-1 font-semibold', style.text)}>{action}</dd>
              )}
            </div>
          )
        })}
      </dl>
    </article>
  )
}
