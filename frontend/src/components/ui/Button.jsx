const base = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '6px',
  borderRadius: '10px',
  fontWeight: '600',
  cursor: 'pointer',
  border: 'none',
  transition: 'all 0.15s',
  whiteSpace: 'nowrap',
}

const variants = {
  primary:   { background: '#4f46e5', color: '#fff', boxShadow: '0 1px 3px rgba(79,70,229,0.3)' },
  secondary: { background: '#fff', color: '#374151', border: '1px solid #d1d5db', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' },
  danger:    { background: '#ef4444', color: '#fff', boxShadow: '0 1px 3px rgba(239,68,68,0.3)' },
  ghost:     { background: 'transparent', color: '#6b7280', boxShadow: 'none' },
}

const sizes = {
  sm: { height: '32px', padding: '0 12px', fontSize: '13px' },
  md: { height: '40px', padding: '0 16px', fontSize: '14px' },
  lg: { height: '48px', padding: '0 20px', fontSize: '15px' },
}

export default function Button({
  children, variant = 'primary', size = 'md',
  style: extraStyle = {}, loading = false, ...props
}) {
  return (
    <button
      {...props}
      disabled={loading || props.disabled}
      style={{
        ...base,
        ...variants[variant],
        ...sizes[size],
        opacity: (loading || props.disabled) ? 0.55 : 1,
        cursor: (loading || props.disabled) ? 'not-allowed' : 'pointer',
        ...extraStyle,
      }}
    >
      {loading && (
        <svg style={{ animation: 'spin 1s linear infinite', width: '14px', height: '14px' }} fill="none" viewBox="0 0 24 24">
          <circle style={{ opacity: 0.25 }} cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
          <path style={{ opacity: 0.75 }} fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
        </svg>
      )}
      {children}
    </button>
  )
}
