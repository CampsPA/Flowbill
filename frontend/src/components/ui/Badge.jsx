const variants = {
  active:        { background: '#ecfdf5', color: '#059669', border: '1px solid #a7f3d0' },
  cancelled:     { background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca' },
  paused:        { background: '#fffbeb', color: '#d97706', border: '1px solid #fde68a' },
  past_due:      { background: '#fff7ed', color: '#ea580c', border: '1px solid #fed7aa' },
  paid:          { background: '#ecfdf5', color: '#059669', border: '1px solid #a7f3d0' },
  open:          { background: '#eff6ff', color: '#2563eb', border: '1px solid #bfdbfe' },
  draft:         { background: '#f8fafc', color: '#64748b', border: '1px solid #e2e8f0' },
  void:          { background: '#f8fafc', color: '#94a3b8', border: '1px solid #e2e8f0' },
  uncollectible: { background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca' },
  succeeded:     { background: '#ecfdf5', color: '#059669', border: '1px solid #a7f3d0' },
  failed:        { background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca' },
  delivered:     { background: '#ecfdf5', color: '#059669', border: '1px solid #a7f3d0' },
  pending:       { background: '#fffbeb', color: '#d97706', border: '1px solid #fde68a' },
  monthly:       { background: '#eef2ff', color: '#4f46e5', border: '1px solid #c7d2fe' },
  annual:        { background: '#faf5ff', color: '#7c3aed', border: '1px solid #ddd6fe' },
  default:       { background: '#f8fafc', color: '#64748b', border: '1px solid #e2e8f0' },
}

export default function Badge({ status, label }) {
  const style = variants[status?.toLowerCase()] ?? variants.default
  return (
    <span style={{
      ...style,
      display: 'inline-flex',
      alignItems: 'center',
      padding: '4px 10px',
      borderRadius: '999px',
      fontSize: '12px',
      fontWeight: '600',
      whiteSpace: 'nowrap',
      letterSpacing: '0.01em',
    }}>
      {label ?? status}
    </span>
  )
}
