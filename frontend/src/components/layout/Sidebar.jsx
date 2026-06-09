import { NavLink, Link, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Users, Package, RefreshCw,
  FileText, CreditCard, Webhook, Settings, LogOut, Zap
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

const nav = [
  { to: '/app',                  label: 'Dashboard',     icon: LayoutDashboard },
  { to: '/app/customers',        label: 'Customers',     icon: Users },
  { to: '/app/plans',            label: 'Plans',         icon: Package },
  { to: '/app/subscriptions',    label: 'Subscriptions', icon: RefreshCw },
  { to: '/app/invoices',         label: 'Invoices',      icon: FileText },
  { to: '/app/payments',         label: 'Payments',      icon: CreditCard },
  { to: '/app/webhooks',         label: 'Webhooks',      icon: Webhook },
  { to: '/app/settings',         label: 'Settings',      icon: Settings },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <aside className="fixed left-0 top-0 h-full bg-[#0f0f1a] flex flex-col z-40 w-14 hover:w-56 transition-[width] duration-200 overflow-hidden group">
      {/* Logo */}
      <Link
        to="/app"
        className="flex items-center gap-3 px-4 py-[18px] border-b border-white/8 hover:bg-white/5 transition-colors flex-shrink-0"
      >
        <div className="w-6 h-6 rounded-lg bg-indigo-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-indigo-600/40">
          <Zap size={13} className="text-white" />
        </div>
        <span className="font-semibold text-white text-sm tracking-tight opacity-0 group-hover:opacity-100 transition-opacity duration-150 whitespace-nowrap">
          FlowBill
        </span>
      </Link>

      {/* Nav */}
      <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto overflow-x-hidden">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/app'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-2 py-2 rounded-lg text-sm transition-all duration-150 ${
                isActive
                  ? 'bg-indigo-600/25 text-indigo-300 font-medium'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-white/6'
              }`
            }
          >
            <Icon size={16} className="flex-shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-150 whitespace-nowrap">
              {label}
            </span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-2 py-3 border-t border-white/8 space-y-0.5">
        <div className="px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150 overflow-hidden">
          <p className="text-xs text-slate-500 truncate whitespace-nowrap">{user?.email}</p>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-2 py-2 rounded-lg text-sm text-slate-400 hover:text-slate-100 hover:bg-white/6 transition-all cursor-pointer"
        >
          <LogOut size={16} className="flex-shrink-0" />
          <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-150 whitespace-nowrap">
            Sign out
          </span>
        </button>
      </div>
    </aside>
  )
}
