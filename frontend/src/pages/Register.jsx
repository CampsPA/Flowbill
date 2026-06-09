import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Zap, ArrowLeft } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function set(k, v) { setForm(f => ({ ...f, [k]: v })) }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirm) {
      setError('Passwords do not match.')
      return
    }
    setLoading(true)
    try {
      await register(form.email, form.name, form.password)
      navigate('/login')
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const inputStyle = {
    height: '48px',
    padding: '0 16px',
    border: '1px solid #d1d5db',
    borderRadius: '10px',
    fontSize: '15px',
    color: '#0f172a',
    background: '#fff',
    outline: 'none',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
    width: '100%',
    boxSizing: 'border-box',
  }

  const labelStyle = { fontSize: '13px', fontWeight: '600', color: '#374151' }

  return (
    <div style={{ minHeight: '100vh', display: 'flex' }}>

      {/* Left panel — gradient branding */}
      <div style={{ display: 'flex', flexDirection: 'column', width: '480px', flexShrink: 0, background: 'linear-gradient(135deg, #60a5fa 0%, #4f46e5 50%, #a855f7 100%)', alignItems: 'center', justifyContent: 'center' }}>
        <Link to="/" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px', textDecoration: 'none' }}>
          <div style={{ width: '52px', height: '52px', borderRadius: '14px', background: 'rgba(255,255,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Zap size={24} color="#fff" />
          </div>
          <span style={{ fontWeight: '700', color: '#fff', fontSize: '22px', letterSpacing: '-0.5px' }}>FlowBill</span>
          <span style={{ color: 'rgba(255,255,255,0.65)', fontSize: '14px', marginTop: '-8px' }}>Billing infrastructure for modern teams.</span>
        </Link>
      </div>

      {/* Right panel — form */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: '#f6f9fc', padding: '64px 32px' }}>
        <div style={{ width: '100%', maxWidth: '400px' }}>

          <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: '#94a3b8', textDecoration: 'none', marginBottom: '40px' }}>
            <ArrowLeft size={13} /> Back to home
          </Link>

          <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#0f172a', marginBottom: '8px', letterSpacing: '-0.5px' }}>
            Create an account
          </h1>
          <p style={{ fontSize: '15px', color: '#64748b', marginBottom: '40px' }}>
            Get started with FlowBill for free.
          </p>

          {error && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#dc2626', marginBottom: '24px' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={labelStyle}>Full Name</label>
              <input type="text" placeholder="Jane Smith" value={form.name} onChange={e => set('name', e.target.value)} required style={inputStyle} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={labelStyle}>Email address</label>
              <input type="email" placeholder="you@company.com" value={form.email} onChange={e => set('email', e.target.value)} required style={inputStyle} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={labelStyle}>Password</label>
              <input type="password" placeholder="••••••••" value={form.password} onChange={e => set('password', e.target.value)} required style={inputStyle} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={labelStyle}>Confirm Password</label>
              <input type="password" placeholder="••••••••" value={form.confirm} onChange={e => set('confirm', e.target.value)} required style={inputStyle} />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{ height: '48px', width: '100%', background: '#4f46e5', color: '#fff', fontWeight: '600', fontSize: '15px', border: 'none', borderRadius: '10px', cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1, marginTop: '4px' }}
            >
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <p style={{ textAlign: 'center', fontSize: '14px', color: '#64748b', marginTop: '32px' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ fontWeight: '600', color: '#4f46e5', textDecoration: 'none' }}>Sign in</Link>
          </p>

        </div>
      </div>
    </div>
  )
}
