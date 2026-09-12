import { useState } from 'react'
import { LockKeyhole, ShieldCheck } from 'lucide-react'
import { login } from '../../../shared/api/client.js'

export function LoginScreen({ onLogin }) {
  const [userId, setUserId] = useState('rosa-elena')
  const [password, setPassword] = useState('')
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
      setError(detail === 'Credenciales inválidas.' ? 'Usuario o contraseña incorrectos.' : detail || 'No se pudo iniciar sesión.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="min-h-screen bg-[#0a0f1d] px-4 grid place-items-center font-sans text-slate-200">
      <section className="w-full max-w-md rounded-3xl border border-slate-800/70 bg-slate-900/55 p-7 shadow-2xl shadow-slate-950/40">
        <span className="grid size-12 place-items-center rounded-2xl border border-emerald-800/50 bg-emerald-950/40">
          <ShieldCheck className="size-6 text-emerald-400" />
        </span>
        <h1 className="mt-5 text-2xl font-bold text-slate-100">Guardián</h1>
        <p className="mt-1 text-sm text-slate-400">Piloto local de protección contra fraude por ingeniería social.</p>

        <form className="mt-7 space-y-4" onSubmit={submit}>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-400">
            Perfil demo
            <select value={userId} onChange={(event) => setUserId(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-3 text-sm text-slate-100 outline-none focus:border-emerald-500">
              <option value="rosa-elena">Rosa Elena · Cliente</option>
              <option value="analyst-demo">Analista Guardián · Analista</option>
            </select>
          </label>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-400">
            Contraseña local
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength="8" required className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-3 text-sm text-slate-100 outline-none focus:border-emerald-500" />
          </label>
          <button type="submit" disabled={busy} className="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-400 px-4 py-3 font-bold text-slate-950 transition hover:bg-emerald-300 disabled:opacity-60">
            <LockKeyhole className="size-4" />
            {busy ? 'Validando sesión…' : 'Entrar al piloto'}
          </button>
          {error && <p className="text-center text-xs text-rose-300">{error}</p>}
        </form>
        <p className="mt-5 text-xs leading-relaxed text-slate-500">La contraseña se valida en el servidor. Guardián no expone una clave de servidor dentro del navegador.</p>
      </section>
    </main>
  )
}
