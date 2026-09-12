import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export const LEVEL_STYLES = {
  low: {
    text: 'text-emerald-400',
    bg: 'bg-emerald-950/40',
    border: 'border-emerald-800/40',
    dot: 'bg-emerald-400',
    label: 'Normal',
  },
  medium: {
    text: 'text-amber-400',
    bg: 'bg-amber-950/40',
    border: 'border-amber-800/40',
    dot: 'bg-amber-400',
    label: 'Revisar',
  },
  high: {
    text: 'text-rose-400',
    bg: 'bg-rose-950/40',
    border: 'border-rose-800/40',
    dot: 'bg-rose-400',
    label: '¡Cuidado!',
  },
}

export function formatMoney(amount) {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
    minimumFractionDigits: 2,
  }).format(amount)
}

export function formatTime(iso) {
  try {
    return new Intl.DateTimeFormat('es-MX', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}
