import { AlertTriangle, ArrowRight, CheckCircle2, Clock, Eye } from 'lucide-react'
import { LEVEL_STYLES, cn, formatMoney, formatTime } from '../../../shared/lib/ui.js'

function explain(reason) {
  if (reason.includes('Beneficiario nuevo'))
    return { why: 'Destinatario nuevo: nunca habías transferido a esta persona.', action: 'Confirma por otro canal que conoces a esta persona.' }
  if (reason.includes('Monto alto'))
    return { why: 'El monto supera el umbral de $10,000.', action: 'Verifica que fuiste tú quien autorizó esta cantidad.' }
  if (reason.includes('Actividad rápida'))
    return { why: 'Tres o más movimientos en menos de 10 minutos.', action: 'Pausa: verifica que reconoces cada cargo.' }
  if (reason.includes('Volumen elevado'))
    return { why: 'Acumulado de 10 min supera $5,000.', action: 'Revisa si estos cargos salieron de forma voluntaria.' }
  if (reason.includes('Monto atípico'))
    return { why: 'El monto supera 3× tu promedio habitual.', action: 'Si alguien te pidió esta transferencia por teléfono, detente.' }
  if (reason.includes('Dispositivo nuevo'))
    return { why: 'Transferencia iniciada desde un dispositivo no habitual.', action: 'Si no reconoces el dispositivo, cancela y revisa tus sesiones.' }
  if (reason.includes('Horario inusual'))
    return { why: 'Operación fuera de tu patrón horario.', action: 'Si te metieron prisa por mensaje, detente.' }
  if (reason.includes('Destino señalado'))
    return { why: 'El beneficiario tiene señales previas de riesgo.', action: 'No continúes sin verificar por un canal oficial.' }
  return { why: 'Sin señales de riesgo con las reglas actuales.', action: null }
}

const STATUS_CONFIG = {
  completed:         { label: 'Completada',        varColor: 'var(--text-soft)',  varDot: 'var(--text-soft)' },
  pending_review:    { label: 'En pausa',           varColor: 'var(--alert)',      varDot: 'var(--alert)',    pulse: true },
  confirmed:         { label: 'Confirmada por ti',  varColor: 'var(--safe)',       varDot: 'var(--safe)' },
  cancelled:         { label: 'Cancelada',          varColor: 'var(--high)',       varDot: 'var(--high)' },
  reported_pressure: { label: 'Presión reportada', varColor: 'var(--alert)',      varDot: 'var(--alert)' },
}

export function AlertCard({ operation }) {
  const risk = operation?.risk ?? { score: 0, level: 'low', reasons: [] }
  const style = LEVEL_STYLES[risk.level] ?? LEVEL_STYLES.low
  const Icon = risk.level === 'low' ? CheckCircle2 : risk.level === 'medium' ? Eye : AlertTriangle
  const isTransfer = operation?.kind === 'transfer'
  const statusCfg = STATUS_CONFIG[operation?.status] ?? { label: 'Registrada', varColor: 'var(--text-soft)', varDot: 'var(--text-soft)' }

  return (
    <article className="rounded-2xl border t-border t-surface t-shadow transition-all duration-300 hover:t-shadow-lg">
      {/* Header */}
      <div className="flex items-start gap-3 p-4 pb-3">
        <span className={cn('grid size-9 shrink-0 place-items-center rounded-xl border mt-0.5', style.bg, style.border)}>
          <Icon className={cn('size-4', style.text)} />
        </span>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="text-sm font-bold t-text leading-tight">
                {isTransfer ? 'Transferencia' : 'Movimiento'}
                {' '}
                <span className="font-mono tabular-nums">{formatMoney(operation.amount)}</span>
              </p>
              {operation.payee_name && (
                <p className="flex items-center gap-1 text-[11px] t-muted mt-0.5">
                  <ArrowRight className="size-3" />
                  {operation.payee_name}
                </p>
              )}
              <p className="text-[11px] t-soft mt-0.5 truncate">{operation.description}</p>
            </div>

            {/* Score badge */}
            <div className={cn('shrink-0 rounded-xl border px-2.5 py-1.5 text-center min-w-[52px]', style.bg, style.border)}>
              <p className={cn('font-mono tabular-nums text-lg font-bold leading-none', style.text)}>
                {risk.score}
              </p>
              <p className={cn('text-[9px] font-bold uppercase tracking-wide mt-0.5', style.text)}>
                {style.label}
              </p>
            </div>
          </div>

          {/* Meta */}
          <div className="flex items-center gap-3 mt-2 flex-wrap">
            <span className="flex items-center gap-1 text-[10px] t-soft font-mono tabular-nums">
              <Clock className="size-2.5" />
              {formatTime(operation.occurred_at)}
            </span>
            <span className="text-[10px] t-soft font-mono opacity-50">#{operation.id}</span>
            <span className="flex items-center gap-1 text-[10px] font-semibold"
              style={{ color: statusCfg.varColor }}>
              <span
                className={cn('size-1.5 rounded-full', statusCfg.pulse && 'animate-pulse')}
                style={{ backgroundColor: statusCfg.varDot }}
              />
              {statusCfg.label}
            </span>
          </div>
        </div>
      </div>

      {/* Risk reasons */}
      {risk.reasons && risk.reasons.length > 0 && (
        <div className="px-4 pb-4 space-y-2">
          {risk.reasons.map((reason, i) => {
            const { why, action } = explain(reason)
            const calm = risk.level === 'low'
            if (calm && i > 0) return null
            return (
              <div
                key={i}
                className={cn(
                  'rounded-xl border px-3 py-2.5',
                  calm ? 't-border t-surface-2' : cn(style.border, style.bg),
                )}
              >
                {!calm && (
                  <p className={cn('text-[10px] font-bold uppercase tracking-wider mb-1', style.text)}>
                    Señal {i + 1} · {reason}
                  </p>
                )}
                <p className="text-xs t-text leading-snug opacity-85">{why}</p>
                {action && (
                  <p className={cn('text-[11px] font-semibold mt-1.5 leading-snug', style.text)}>
                    → {action}
                  </p>
                )}
              </div>
            )
          })}
        </div>
      )}
    </article>
  )
}
