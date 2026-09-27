import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'
import client from '../api/client'
import type { AuthResponse, Role, User } from '../api/types'

interface AuthContextValue {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<User>
  register: (data: {
    name: string
    email: string
    password: string
    role: Role
    department?: string
  }) => Promise<User>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

function loadStoredUser(): User | null {
  const raw = localStorage.getItem('udyogsetu_user')
  if (!raw) return null
  try {
    return JSON.parse(raw) as User
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(loadStoredUser())
  const [token, setToken] = useState<string | null>(localStorage.getItem('udyogsetu_token'))

  const persist = (data: AuthResponse) => {
    localStorage.setItem('udyogsetu_token', data.access_token)
    localStorage.setItem('udyogsetu_user', JSON.stringify(data.user))
    setToken(data.access_token)
    setUser(data.user)
  }

  const login = async (email: string, password: string) => {
    const { data } = await client.post<AuthResponse>('/auth/login', { email, password })
    persist(data)
    return data.user
  }

  const register = async (payload: {
    name: string
    email: string
    password: string
    role: Role
    department?: string
  }) => {
    const { data } = await client.post<AuthResponse>('/auth/register', payload)
    persist(data)
    return data.user
  }

  const logout = () => {
    localStorage.removeItem('udyogsetu_token')
    localStorage.removeItem('udyogsetu_user')
    setToken(null)
    setUser(null)
  }

  const value = useMemo(
    () => ({ user, token, isAuthenticated: Boolean(token && user), login, register, logout }),
    [user, token],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
