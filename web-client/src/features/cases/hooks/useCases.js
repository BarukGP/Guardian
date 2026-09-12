import { useCallback, useEffect, useState } from 'react'
import { fetchCases } from '../../../shared/api/client.js'

export function useCases(refreshKey) {
  const [cases, setCases] = useState([])

  const refresh = useCallback(async () => {
    try {
      const data = await fetchCases()
      setCases(Array.isArray(data) ? data : [])
    } catch {
      setCases([])
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh, refreshKey])

  return { cases, refresh }
}
