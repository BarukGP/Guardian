import { useCallback, useEffect, useRef, useState } from 'react'
import { fetchTimeline } from '../../../shared/api/client.js'

export function useTimeline({ intervalMs = 2500, limit = 50 } = {}) {
  const [operations, setOperations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastSync, setLastSync] = useState(null)
  const inFlight = useRef(false)

  const refresh = useCallback(async () => {
    if (inFlight.current) return
    inFlight.current = true
    try {
      const data = await fetchTimeline(limit)
      setOperations(Array.isArray(data) ? data : [])
      setError(null)
      setLastSync(new Date())
    } catch (err) {
      const status = err?.response?.status
      setError(
        status === 401
          ? 'Sesión expirada. Vuelve a iniciar sesión.'
          : 'No se pudo contactar al backend. Verifica que corre en el puerto 8000.',
      )
    } finally {
      inFlight.current = false
      setLoading(false)
    }
  }, [limit])

  useEffect(() => {
    refresh()
    const timer = setInterval(refresh, intervalMs)
    return () => clearInterval(timer)
  }, [refresh, intervalMs])

  return { operations, loading, error, lastSync, refresh }
}
