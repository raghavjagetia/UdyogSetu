import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const ROLE_LABEL: Record<string, string> = {
  entrepreneur: 'Entrepreneur',
  officer: 'Department Officer',
  admin: 'Administrator',
}

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `rounded-lg px-3 py-2 text-sm font-medium transition ${
      isActive ? 'bg-brand-700 text-white' : 'text-slate-600 hover:bg-brand-50 hover:text-brand-700'
    }`

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-600 to-accent-500 text-sm font-bold text-white">
              US
            </div>
            <div>
              <p className="text-base font-semibold leading-none text-brand-900">UdyogSetu</p>
              <p className="text-[11px] leading-none text-slate-400">Single Window Compliance</p>
            </div>
          </div>

          <nav className="flex items-center gap-1">
            <NavLink to="/dashboard" className={linkClass} end>
              Dashboard
            </NavLink>
            {user?.role === 'entrepreneur' && (
              <NavLink to="/applications/new" className={linkClass}>
                New Application
              </NavLink>
            )}
            <NavLink to="/schemes" className={linkClass}>
              Schemes
            </NavLink>
            {user?.role === 'admin' && (
              <NavLink to="/rules" className={linkClass}>
                Rules Engine
              </NavLink>
            )}
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm font-medium text-slate-700">{user?.name}</p>
            <p className="text-xs text-slate-400">
              {ROLE_LABEL[user?.role ?? '']}
              {user?.department ? ` · ${user.department}` : ''}
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 transition hover:border-rose-300 hover:text-rose-600"
          >
            Sign out
          </button>
        </div>
      </div>
    </header>
  )
}
