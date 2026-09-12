import { useEffect, useState } from 'react'
import { LogOut, ShieldCheck, Wifi, WifiOff } from 'lucide-react'
import { checkBackend } from '../../../shared/api/client.js'
import { cn } from '../../../shared/lib/ui.js'

export function Header({ lastSync, user, onLogout }) {
  const [online, setOnline] = useState(null)

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
    return () => {
      alive = false
      clearInterval(t)
    }
  }, [])

  return (
    <header className="border border-slate-800/60 bg-slate-900/40 backdrop-blur-sm rounded-2xl px-5 py-4 flex items-center justify-between gap-4 transition-all duration-300 ease-out">
      <div className="flex items-center gap-3">
        <span className="grid place-items-center size-10 rounded-xl bg-emerald-950/40 border border-emerald-800/40">
          <ShieldCheck className="size-5 text-emerald-400" />
        </span>
        <div>
          <h1 className="font-sans text-lg font-bold text-slate-100 leading-tight">
            Guardián
          </h1>
          <p className="font-sans text-xs text-slate-400">
            {user?.role === 'analyst'
              ? 'Vista de análisis y auditoría'
              : `Protegiendo a ${user?.display_name ?? 'tu cuenta'} en tiempo real`}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <span
          className={cn(
            'size-2 rounded-full transition-all duration-300 ease-out',
            online === null && 'bg-slate-500',
            online === true && 'bg-emerald-400 animate-pulse',
            online === false && 'bg-rose-400',
          )}
        />
        <span className="font-sans text-xs text-slate-300 flex items-center gap-1.5">
          {online === false ? (
            <>
              <WifiOff className="size-3.5 text-rose-400" /> Sin conexión
            </>
          ) : (
            <>
              <Wifi className="size-3.5 text-emerald-400" /> Conectado
              {lastSync && (
                <span className="font-mono tabular-nums text-slate-500">
                  · {lastSync.toLocaleTimeString('es-MX')}
                </span>
              )}
            </>
          )}
        </span>
        <span className="hidden text-xs text-slate-500 sm:inline">{user?.display_name}</span>
        <button type="button" onClick={onLogout} className="ml-1 rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-800 hover:text-slate-100" aria-label="Cerrar sesión">
          <LogOut className="size-3.5" />
        </button>
      </div>
    </header>
  )
}
