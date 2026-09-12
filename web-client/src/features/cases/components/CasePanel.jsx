import { BadgeAlert, PhoneCall } from 'lucide-react'
import { formatTime } from '../../../shared/lib/ui.js'

export function CasePanel({ cases }) {
  if (!cases.length) return null

  return (
    <section className="rounded-2xl border border-amber-700/50 bg-amber-950/35 p-5">
      <div className="flex gap-3">
        <span className="grid size-10 shrink-0 place-items-center rounded-xl border border-amber-700/50 bg-amber-950/50"><BadgeAlert className="size-5 text-amber-300" /></span>
        <div>
          <p className="text-sm font-bold text-amber-100">Casos de protección · {cases.length}</p>
          <p className="mt-1 text-xs leading-relaxed text-amber-100/75">La transferencia quedó detenida y se registró presión externa. Para una emergencia real, contacta directamente a tu banco mediante su número oficial.</p>
          <p className="mt-3 inline-flex items-center gap-1.5 text-xs font-semibold text-amber-200"><PhoneCall className="size-3.5" /> No respondas al número que te contactó.</p>
          <ul className="mt-3 space-y-1.5">
            {cases.map((item) => (
              <li key={item.id} className="text-xs text-amber-100/80">
                Caso #{item.id} · {item.user_display_name ?? item.user_id} · {formatTime(item.created_at)} · {item.status === 'open' ? 'Abierto' : 'Resuelto'}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
