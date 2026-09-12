import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('guardian_session')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export async function login(user_id, password) {
  const { data } = await api.post('/auth/login', { user_id, password })
  localStorage.setItem('guardian_session', data.access_token)
  return data
}

export async function logout() {
  try {
    await api.post('/auth/logout')
  } finally {
    localStorage.removeItem('guardian_session')
  }
}

export async function fetchMe() {
  const { data } = await api.get('/auth/me')
  return data
}

export async function fetchAlerts(limit = 50) {
  const { data } = await api.get('/simulate/alerts', { params: { limit } })
  return data
}

export async function fetchTimeline(limit = 50) {
  const { data } = await api.get('/simulate/timeline', { params: { limit } })
  return data
}

export async function runSimulation(accountId) {
  const { data } = await api.post(
    '/simulate/run',
    null,
    accountId ? { params: { account_id: accountId } } : undefined,
  )
  return data
}

export async function decideOperation(operationId, decision) {
  const { data } = await api.post(`/simulate/operations/${operationId}/decision`, { decision })
  return data
}

export async function resetDemo(accountId) {
  const { data } = await api.delete('/simulate/demo', {
    params: accountId ? { account_id: accountId } : undefined,
  })
  return data
}

export async function fetchCases() {
  const { data } = await api.get('/simulate/cases')
  return data
}

export async function checkBackend() {
  return fetchMe()
}
