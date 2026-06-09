import axios from 'axios'

// Use VITE_API_URL directly so production builds hit the backend without a proxy
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('fb_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    // I11: clear auth and redirect on 401 Unauthorized so stale sessions don't hang
    if (err.response?.status === 401) {
      localStorage.removeItem('fb_token')
      localStorage.removeItem('fb_user')
      window.location.href = '/login'
    }
    // I11: log 5xx server errors to the console for easier debugging in production
    if (err.response?.status >= 500) {
      console.error('[FlowBill] Server error', err.response.status, err.response.data)
    }
    return Promise.reject(err)
  }
)

export default api
