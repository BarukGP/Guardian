import { useEffect, useState } from 'react'

const KEY = 'guardian_theme'

export function useTheme() {
  const [dark, setDark] = useState(() => {
    const stored = localStorage.getItem(KEY)
    if (stored) return stored === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    const root = document.documentElement
    if (dark) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    localStorage.setItem(KEY, dark ? 'dark' : 'light')
  }, [dark])

  const toggle = () => setDark((v) => !v)

  return { dark, toggle }
}
