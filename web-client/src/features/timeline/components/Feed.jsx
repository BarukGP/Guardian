import { Inbox } from 'lucide-react'
import { useMemo, useState } from 'react'
import { AlertCard } from './AlertCard.jsx'
import { cn } from '../../../shared/lib/ui.js'

function FilterChip({ label, count, active, varActive, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex items-center gap-1.5 rounded-xl border px-2.5 py-1 text-[11px] font-semibold transition-all"
      style={active
        ? { borderColor: varActive, backgroundColor: `color-mix(in srgb, ${varActive} 12%, var(--surface))`, color: varActive }
        : { borderColor: 'var(--border)', backgroundColor: 'var(--surface)', color: 'var(--text-muted)' }
      }
    >
      {label}
      <span className="rounded-md px-1.5 py-0.5 font-mono tabular-nums text-[10px]"
        style={{ backgroundColor: 'color-mix(in srgb, currentColor 10%, var(--surface))', opacity: 0.9 }}>
        {count}
      </span>
    </button>
  )
}

export function Feed({ operations, loading, filter, onFilterChange }) {
  const counts = useMemo(() => ({
    all:    operations.length,
    high:   operations.filter((o) => o?.risk?.level === 'high').length,
    medium: operations.filter((o) => o?.risk?.level === 'medium').length,
    low:    operations.filter((o) => o?.risk?.level === 'low').length,
  }), [operations])

  const displayed = useMemo(() => {
    if (!filter || filter === 'all') return operations
    return operations.filter((o) => o?.risk?.level === filter)
  }, [operations, filter])

  if (loading && operations.length === 0) {
    return (
      <div className="space-y-3">
        {[0, 1, 2].map((i) => (
          <div key={i} className="h-24 rounded-2xl border t-border t-surface animate-pulse" />
        ))}
      </div>
    )
  }

  if (operations.length === 0) {
    return (
      <div className="rounded-2xl border t-border t-surface p-10 text-center t-shadow">
        <Inbox className="size-8 t-soft mx-auto" />
        <p className="text-sm font-semibold t-text mt-3">Sin actividad todavía</p>
        <p className="text-xs t-muted mt-1">
          Pulsa "Simular escenario de estafa" para ver a Guardián en acción.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 flex-wrap">
        <FilterChip label="Todas"   count={counts.all}    varActive="var(--primary)" active={!filter || filter === 'all'}    onClick={() => onFilterChange('all')} />
        <FilterChip label="⚠ Alto"  count={counts.high}   varActive="var(--high)"    active={filter === 'high'}   onClick={() => onFilterChange('high')} />
        <FilterChip label="Revisar" count={counts.medium} varActive="var(--alert)"   active={filter === 'medium'} onClick={() => onFilterChange('medium')} />
        <FilterChip label="Normal"  count={counts.low}    varActive="var(--safe)"    active={filter === 'low'}    onClick={() => onFilterChange('low')} />
      </div>

      {displayed.length === 0 ? (
        <div className="rounded-2xl border t-border t-surface p-6 text-center t-shadow">
          <p className="text-xs t-muted">Sin operaciones en este filtro.</p>
        </div>
      ) : (
        <div className="space-y-2.5">
          {displayed.map((op) => (
            <AlertCard key={op.id} operation={op} />
          ))}
        </div>
      )}
    </div>
  )
}
