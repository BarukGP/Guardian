import { useState } from 'react'
import { Eye, EyeOff, LockKeyhole, ShieldCheck, UserCircle2 } from 'lucide-react'
import { login } from '../../../shared/api/client.js'
import { cn } from '../../../shared/lib/ui.js'

const PROFILES = [
  {
    id: 'rosa-elena',
    name: 'Rosa Elena',
    role: 'Cliente',
    desc: 'Simula el punto de vista de un usuario protegido',
    accent: 'primary',
  },
  {
    id: 'analyst-demo',
    name: 'Analista Guardián',
    role: 'Analista',
    desc: 'Audita actividad y revisa casos sin tomar decisiones',
    accent: 'safe',
  },
]

export function LoginScreen({ onLogin }) {
  const [userId, setUserId] = useState('rosa-elena')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const submit = async (event) => {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const session = await login(userId, password)
      onLogin(session.user)
    } catch (requestError) {
      const detail = requestError?.response?.data?.detail
      setError(
        detail === 'Credenciales inválidas.'
          ? 'Usuario o contraseña incorrectos.'
          : detail || 'No se pudo iniciar sesión.',
      )
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="min-h-screen t-bg px-4 flex flex-col items-center justify-center font-sans">

      {/* Brand */}
      <div className="flex items-center gap-3 mb-8">
        <span className="grid size-12 place-items-center rounded-2xl t-primary-bg shadow-lg"
          style={{ boxShadow: '0 8px 24px color-mix(in srgb, var(--primary) 25%, transparent)' }}>
          <ShieldCheck className="size-6 text-white" />
        </span>
        <div>
          <h1 className="text-2xl font-bold t-text leading-none">Guardián</h1>
          <p className="text-xs t-soft mt-0.5">Protección antifraude en tiempo real</p>
        </div>
      </div>

      <section className="w-full max-w-sm rounded-3xl border t-border t-surface p-7 t-shadow-lg">
        <p className="text-sm font-semibold t-text mb-5">Selecciona un perfil para entrar</p>

        {/* Profile cards */}
        <div className="space-y-2.5 mb-6">
          {PROFILES.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => setUserId(p.id)}
              className={cn(
                'w-full rounded-2xl border p-3.5 text-left transition-all duration-200',
                userId === p.id
                  ? p.accent === 'primary'
                    ? 't-primary-light border-[color-mix(in_srgb,var(--primary)_40%,transparent)]'
                    : 't-safe-bg t-safe-border'
                  : 't-surface border t-border hover:t-surface-2',
              )}
            >
              <div className="flex items-center gap-3">
                <span className={cn(
                  'grid size-9 shrink-0 place-items-center rounded-xl border',
                  userId === p.id
                    ? p.accent === 'primary' ? 't-primary-light t-primary-text' : 't-safe-bg t-safe-accent'
                    : 't-surface-2 t-border t-muted',
                )}>
                  <UserCircle2 className="size-4" />
                </span>
                <div className="min-w-0 flex-1">
                  <p className={cn(
                    'text-sm font-bold leading-none',
                    userId === p.id
                      ? p.accent === 'primary' ? 't-primary-text' : 't-safe-accent'
                      : 't-text',
                  )}>
                    {p.name}
                    <span className="ml-2 text-[10px] font-normal t-soft">{p.role}</span>
                  </p>
                  <p className="text-[11px] t-muted mt-0.5 leading-snug">{p.desc}</p>
                </div>
                <span
                  style={{
                    borderColor: userId === p.id
                      ? (p.accent === 'primary' ? 'var(--primary)' : 'var(--safe)')
                      : 'var(--border-strong)',
                    backgroundColor: userId === p.id
                      ? (p.accent === 'primary' ? 'var(--primary)' : 'var(--safe)')
                      : 'transparent',
                  }}
                  className="ml-auto size-4 rounded-full border-2 shrink-0 transition-all"
                />
              </div>
            </button>
          ))}
        </div>

        {/* Password */}
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider t-muted mb-1.5">
              Contraseña
            </label>
            <div className="relative">
              <input
                type={showPass ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength="8"
                required
                placeholder="••••••••"
                className="w-full rounded-xl border t-border t-surface-2 px-3 py-3 pr-10 text-sm t-text outline-none transition-all placeholder:t-soft"
                style={{ '--tw-ring-color': 'var(--primary)' }}
                onFocus={(e) => { e.target.style.borderColor = 'var(--primary)'; e.target.style.boxShadow = '0 0 0 3px color-mix(in srgb, var(--primary) 12%, transparent)' }}
                onBlur={(e) => { e.target.style.borderColor = ''; e.target.style.boxShadow = '' }}
              />
              <button
                type="button"
                onClick={() => setShowPass((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 t-soft hover:t-muted transition-colors"
                aria-label={showPass ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              >
                {showPass ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
              </button>
            </div>
          </div>

          {error && (
            <div className="rounded-xl border t-high-border t-high-bg px-3 py-2.5">
              <p className="text-xs t-high-text text-center">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={busy}
            className="flex w-full items-center justify-center gap-2 rounded-xl t-primary-bg px-4 py-3.5 font-bold text-white text-sm transition-all active:scale-[0.98] disabled:opacity-60 disabled:cursor-wait"
            style={{ boxShadow: '0 4px 14px color-mix(in srgb, var(--primary) 25%, transparent)' }}
            onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--primary-hover)' }}
            onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--primary)' }}
          >
            <LockKeyhole className="size-4" />
            {busy ? 'Verificando…' : 'Entrar'}
          </button>
        </form>
      </section>

      <p className="mt-6 text-[11px] t-soft text-center max-w-xs">
        Demo local · Las credenciales se validan en el servidor y nunca se exponen en el navegador.
      </p>
    </main>
  )
}
