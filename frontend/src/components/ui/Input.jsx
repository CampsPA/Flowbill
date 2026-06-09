const inputStyle = {
  height: '48px',
  padding: '0 16px',
  border: '1px solid #d1d5db',
  borderRadius: '10px',
  fontSize: '14px',
  color: '#1e293b',
  background: '#fff',
  outline: 'none',
  boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
  width: '100%',
  boxSizing: 'border-box',
  transition: 'border-color 0.15s, box-shadow 0.15s',
}

const labelStyle = {
  fontSize: '13px',
  fontWeight: '600',
  color: '#374151',
  marginBottom: '6px',
  display: 'block',
}

export default function Input({ label, error, style: extraStyle = {}, ...props }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {label && <label style={labelStyle}>{label}</label>}
      <input
        {...props}
        style={{
          ...inputStyle,
          ...(error ? { borderColor: '#f87171' } : {}),
          ...extraStyle,
        }}
        onFocus={e => { e.target.style.borderColor = '#6366f1'; e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.15)' }}
        onBlur={e => { e.target.style.borderColor = error ? '#f87171' : '#d1d5db'; e.target.style.boxShadow = '0 1px 3px rgba(0,0,0,0.05)' }}
      />
      {error && <p style={{ fontSize: '12px', color: '#ef4444', marginTop: '4px' }}>{error}</p>}
    </div>
  )
}

export function Select({ label, error, children, style: extraStyle = {}, ...props }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {label && <label style={labelStyle}>{label}</label>}
      <select
        {...props}
        style={{
          ...inputStyle,
          paddingRight: '36px',
          appearance: 'none',
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'right 14px center',
          cursor: 'pointer',
          ...(error ? { borderColor: '#f87171' } : {}),
          ...extraStyle,
        }}
      >
        {children}
      </select>
      {error && <p style={{ fontSize: '12px', color: '#ef4444', marginTop: '4px' }}>{error}</p>}
    </div>
  )
}
