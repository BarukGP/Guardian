import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

// LEVEL_STYLES usa variables CSS de tema → funciona en light y dark automáticamente
export const LEVEL_STYLES = {
  low: {
    text:   't-safe-accent',
    bg:     't-safe-bg',
    border: 't-safe-border',
    dot:    'bg-[var(--safe)]',
    label:  'Normal',
    pill:   't-safe-bg t-safe-border t-safe-accent',
  },
  medium: {
    text:   't-alert-accent',
    bg:     't-alert-bg',
    border: 't-alert-border',
    dot:    'bg-[var(--alert)]',
    label:  'Revisar',
    pill:   't-alert-bg t-alert-border t-alert-accent',
  },
  high: {
    text:   't-high-accent',
    bg:     't-high-bg',
    border: 't-high-border',
    dot:    'bg-[var(--high)]',
    label:  '¡Alerta!',
    pill:   't-high-bg t-high-border t-high-accent',
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

export function formatTimeShort(iso) {
  try {
    return new Intl.DateTimeFormat('es-MX', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}
