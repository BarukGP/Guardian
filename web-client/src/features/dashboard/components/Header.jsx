import { useEffect, useState } from 'react'
import { ChevronDown, LogOut, Moon, ShieldCheck, Sun, UserCircle2, WifiOff } from 'lucide-react'
import { checkBackend } from '../../../shared/api/client.js'
import { cn, formatTimeShort } from '../../../shared/lib/ui.js'

export function Header({ lastSync, user, onLogout, dark, onToggleTheme }) {
  const [online, setOnline] = useState(null)
  const [showMenu, setShowMenu] = useState(false)

  useEffect(() => {
    let alive = true
    const ping = async () => {
      try {
        await checkBackend()
        if (alive) setOnline(true)
      } catch {
        if (alive) setOnline(false)
      }
    }
    ping()
    const t = setInterval(ping, 10000)
    return () => { alive = false; clearInterval(t) }
  }, [])

  return (
    <header className="flex items-center justify-between gap-4 px-1">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <span
          className="grid size-9 shrink-0 place-items-center rounded-xl t-primary-bg"
          style={{ boxShadow: '0 2px 8px color-mix(in srgb, var(--primary) 30%, transparent)' }}
        >
          <ShieldCheck className="size-4.5 text-white" />
        </span>
        <div>
          <h1 className="text-base font-bold t-text leading-none">Guardián</h1>
          <p className="text-[11px] t-soft mt-0.5">
            {user?.role === 'analyst' ? 'Vista analista' : 'Protección en tiempo real'}
          </p>
        </div>
      </div>

      {/* Right */}
      <div className="flex items-center gap-2">

        {/* Connection chip */}
        <div
          className="hidden sm:flex items-center gap-1.5 rounded-full px-2.5 py-1 border text-[11px] font-medium"
          style={online === true
            ? { borderColor: 'var(--safe-border)', backgroundColor: 'var(--safe-light)', color: 'var(--safe)' }
            : online === false
            ? { borderColor: 'var(--alert-border)', backgroundColor: 'var(--alert-light)', color: 'var(--alert)' }
            : { borderColor: 'var(--border)', backgroundColor: 'var(--surface-2)', color: 'var(--text-soft)' }
          }
        >
          {online === false ? (
            <><WifiOff className="size-3" /> Sin conexión</>
          ) : (
            <>
              <span
                className={cn('size-1.5 rounded-full', online === true && 'animate-pulse')}
                style={{ backgroundColor: online === true ? 'var(--safe)' : 'var(--text-soft)' }}
              />
              {online === true ? 'En línea' : 'Conectando…'}
            </>
          )}
          {lastSync && online === true && (
            <span className="t-soft font-mono tabular-nums">· {formatTimeShort(lastSync)}</span>
          )}
        </div>

        {/* ── Theme toggle button ── */}
        <button
          type="button"
          onClick={onToggleTheme}
          aria-label={dark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
          className="relative grid size-8 place-items-center rounded-xl border t-border t-surface t-shadow transition-all hover:t-surface-2 active:scale-95 no-theme-transition"
          title={dark ? 'Modo claro' : 'Modo oscuro'}
        >
          {/* Sun — visible en dark */}
          <Sun
            className={cn(
              'absolute size-3.5 transition-all duration-300',
              dark ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 rotate-90 scale-50',
            )}
            style={{ color: 'var(--alert)' }}
          />
          {/* Moon — visible en light */}
          <Moon
            className={cn(
              'absolute size-3.5 transition-all duration-300',
              dark ? 'opacity-0 -rotate-90 scale-50' : 'opacity-100 rotate-0 scale-100',
            )}
            style={{ color: 'var(--primary)' }}
          />
        </button>

        {/* User menu */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowMenu((v) => !v)}
            className="flex items-center gap-2 rounded-xl border t-border t-surface px-2.5 py-1.5 text-xs t-text hover:t-surface-2 transition-all t-shadow"
          >
            <UserCircle2 className="size-3.5 t-muted" />
            <span className="hidden sm:inline font-medium">{user?.display_name ?? 'Usuario'}</span>
            <ChevronDown className={cn('size-3 t-soft transition-transform', showMenu && 'rotate-180')} />
          </button>

          {showMenu && (
            <div className="absolute right-0 top-full mt-1.5 z-50 w-44 rounded-2xl border t-border t-surface py-1.5 overflow-hidden"
              style={{ boxShadow: 'var(--shadow-lg)' }}>
              <div className="px-3 py-2 border-b t-border">
                <p className="text-xs font-bold t-text">{user?.display_name}</p>
                <p className="text-[10px] t-soft mt-0.5">{user?.role === 'analyst' ? 'Analista' : 'Cliente'}</p>
              </div>
              <button
                type="button"
                onClick={() => { setShowMenu(false); onLogout() }}
                className="flex w-full items-center gap-2 px-3 py-2 text-xs t-high-text hover:t-high-bg transition-colors mt-0.5"
              >
                <LogOut className="size-3.5" />
                Cerrar sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
