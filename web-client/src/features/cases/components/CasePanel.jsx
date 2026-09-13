import { BadgeAlert, PhoneCall } from 'lucide-react'
import { cn, formatTime } from '../../../shared/lib/ui.js'

function CaseRow({ item }) {
  const isOpen = item.status === 'open'
  return (
    <li
      className="rounded-xl border px-3 py-2.5 flex items-center gap-3"
      style={{
        borderColor: isOpen ? 'var(--alert-border)' : 'var(--safe-border)',
        backgroundColor: isOpen ? 'var(--alert-light)' : 'var(--safe-light)',
      }}
    >
      <span
        className={cn('size-2 rounded-full shrink-0', isOpen && 'animate-pulse')}
        style={{ backgroundColor: isOpen ? 'var(--alert)' : 'var(--safe)' }}
      />
      <div className="flex-1 min-w-0">
        <p className="text-xs font-bold t-text leading-none truncate">
          {item.user_display_name ?? item.user_id}
        </p>
        <p className="text-[10px] t-soft mt-0.5 font-mono tabular-nums">
          Caso #{item.id} · {formatTime(item.created_at)}
        </p>
      </div>
      <span
        className="text-[10px] font-bold shrink-0"
        style={{ color: isOpen ? 'var(--alert)' : 'var(--safe)' }}
      >
        {isOpen ? 'Abierto' : 'Resuelto'}
      </span>
    </li>
  )
}

export function CasePanel({ cases }) {
  const open     = cases.filter((c) => c.status === 'open').length
  const resolved = cases.length - open
  if (!cases.length) return null

  return (
    <section className="rounded-2xl border t-alert-border t-alert-bg overflow-hidden t-shadow">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b t-alert-border"
        style={{ backgroundColor: 'color-mix(in srgb, var(--alert) 12%, var(--surface))' }}>
        <span className="grid size-8 shrink-0 place-items-center rounded-xl border t-alert-border t-surface">
          <BadgeAlert className="size-4 t-alert-accent" />
        </span>
        <div className="flex-1">
          <p className="text-sm font-bold t-alert-text">
            Casos de protección
            <span className="ml-2 font-mono t-alert-accent">{cases.length}</span>
          </p>
          <p className="text-[11px] t-alert-accent opacity-70 mt-0.5">
            {open > 0 ? `${open} abierto${open > 1 ? 's' : ''}` : 'Sin casos abiertos'}
            {' · '}{resolved} resuelto{resolved !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      <div className="p-4 space-y-3">
        {/* Alert message */}
        <div className="flex items-start gap-2.5 rounded-xl border t-border t-surface px-3 py-2.5">
          <PhoneCall className="size-3.5 t-alert-accent shrink-0 mt-0.5" />
          <div>
            <p className="text-xs t-muted leading-relaxed">
              La transferencia quedó detenida y se registró presión externa.
            </p>
            <p className="text-[11px] font-bold t-alert-accent mt-1">
              No respondas al número que te contactó — llama tú al número oficial de tu banco.
            </p>
          </div>
        </div>

        <ul className="space-y-2">
          {cases.map((item) => <CaseRow key={item.id} item={item} />)}
        </ul>
      </div>
    </section>
  )
}
