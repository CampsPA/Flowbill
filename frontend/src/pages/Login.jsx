import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Zap, ArrowLeft } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

// N7: removed dual mode (login/register) — Login is login-only; registration lives at /register
export default function Login() {
  const { login } = useAuth()  // N7: no longer need register from context here
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })  // N7: removed name field
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function set(k, v) { setForm(f => ({ ...f, [k]: v })) }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      // N7: only login path remains — register is handled by /register page
      await login(form.email, form.password)
      navigate('/app')
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#f6f9fc] flex">
      {/* Left panel — gradient branding */}
      <div style={{ display: 'flex', flexDirection: 'column', width: '480px', flexShrink: 0, background: 'linear-gradient(135deg, #60a5fa 0%, #4f46e5 50%, #a855f7 100%)', alignItems: 'center', justifyContent: 'center' }}>
        <Link to="/" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px', textDecoration: 'none' }}>
          <div style={{ width: '52px', height: '52px', borderRadius: '14px', background: '#4f46e5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Zap size={24} color="#fff" />
          </div>
          <span style={{ fontWeight: '700', color: '#fff', fontSize: '22px', letterSpacing: '-0.5px' }}>FlowBill</span>
          <span style={{ color: 'rgba(255,255,255,0.35)', fontSize: '14px', marginTop: '-8px' }}>Billing infrastructure for modern teams.</span>
        </Link>
      </div>

      {/* Right panel — login form */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: '#f6f9fc', padding: '64px 32px' }}>
        <div style={{ width: '100%', maxWidth: '400px' }}>

          <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: '#94a3b8', textDecoration: 'none', marginBottom: '40px' }}>
            <ArrowLeft size={13} /> Back to home
          </Link>

          {/* N7: hardcoded to "Welcome back" — no more toggling heading */}
          <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#0f172a', marginBottom: '8px', letterSpacing: '-0.5px' }}>Welcome back</h1>
          <p style={{ fontSize: '15px', color: '#64748b', marginBottom: '40px' }}>Sign in to your FlowBill dashboard</p>

          {error && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#dc2626', marginBottom: '24px' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '13px', fontWeight: '600', color: '#374151' }}>Email address</label>
              <input
                type="email" placeholder="you@company.com" value={form.email} onChange={e => set('email', e.target.value)} required
                style={{ height: '48px', padding: '0 16px', border: '1px solid #d1d5db', borderRadius: '10px', fontSize: '15px', color: '#0f172a', background: '#fff', outline: 'none', boxShadow: '0 1px 3px rgba(0,0,0,0.06)', width: '100%', boxSizing: 'border-box' }}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <label style={{ fontSize: '13px', fontWeight: '600', color: '#374151' }}>Password</label>
                {/* N7: Forgot password link stays — it's login-specific, not register UI */}
                <a href="#" style={{ fontSize: '13px', color: '#4f46e5', textDecoration: 'none' }}>Forgot password?</a>
              </div>
              <input
                type="password" placeholder="••••••••" value={form.password} onChange={e => set('password', e.target.value)} required
                style={{ height: '48px', padding: '0 16px', border: '1px solid #d1d5db', borderRadius: '10px', fontSize: '15px', color: '#0f172a', background: '#fff', outline: 'none', boxShadow: '0 1px 3px rgba(0,0,0,0.06)', width: '100%', boxSizing: 'border-box' }}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{ height: '48px', width: '100%', background: '#4f46e5', color: '#fff', fontWeight: '600', fontSize: '15px', border: 'none', borderRadius: '10px', cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1, marginTop: '4px' }}
            >
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          {/* N7: link to /register instead of toggling mode inline */}
          <p style={{ textAlign: 'center', fontSize: '14px', color: '#64748b', marginTop: '32px' }}>
            Don't have an account?{' '}
            <Link to="/register" style={{ fontWeight: '600', color: '#4f46e5', textDecoration: 'none' }}>
              Sign up
            </Link>
          </p>

        </div>
      </div>
    </div>
  )
}
