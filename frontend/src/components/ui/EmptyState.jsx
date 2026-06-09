export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 32px', textAlign: 'center' }}>
      {Icon && (
        <div style={{ width: '56px', height: '56px', borderRadius: '14px', background: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
          <Icon size={24} color="#94a3b8" />
        </div>
      )}
      <p style={{ fontSize: '15px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>{title}</p>
      {description && <p style={{ fontSize: '14px', color: '#94a3b8', maxWidth: '320px', lineHeight: '1.5' }}>{description}</p>}
      {action && <div style={{ marginTop: '24px' }}>{action}</div>}
    </div>
  )
}
