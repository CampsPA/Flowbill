import { createContext, useContext, useState } from 'react'
import api from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('fb_user')) } catch { return null }
  })

  async function login(email, password) {
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)
    const { data } = await api.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    localStorage.setItem('fb_token', data.access_token)
    const payload = JSON.parse(atob(data.access_token.split('.')[1]))
    const userData = { email: payload.sub }
    localStorage.setItem('fb_user', JSON.stringify(userData))
    setUser(userData)
    return userData
  }

  async function register(email, name, password) {
    const { data } = await api.post('/auth/register', { email, name, password })
    return data
  }

  function logout() {
    localStorage.removeItem('fb_token')
    localStorage.removeItem('fb_user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
