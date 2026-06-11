// Shared color picker component.
// Renders a native <input type="color"> alongside a read-only hex label — no text entry.
// Props:
//   label    — field label string
//   value    — current hex string (e.g. "#4f46e5"); falls back to DEFAULT if empty/undefined
//   onChange — called with the new hex string when the user picks a color

const DEFAULT = '#4f46e5'

export default function ColorPicker({ label, value, onChange }) {
  const hex = value && /^#[0-9A-Fa-f]{6}$/.test(value) ? value : DEFAULT

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
      {label && <label style={{ fontSize: '13px', fontWeight: '600', color: '#374151' }}>{label}</label>}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', height: '44px', padding: '0 12px', border: '1px solid #d1d5db', borderRadius: '10px', background: '#fff', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', cursor: 'pointer' }}>
        {/* Native color swatch — clicking opens the OS color picker */}
        <input
          type="color"
          value={hex}
          onChange={e => onChange(e.target.value)}
          style={{ width: '28px', height: '28px', border: 'none', padding: 0, borderRadius: '6px', cursor: 'pointer', background: 'none', flexShrink: 0 }}
        />
        {/* Read-only hex display — reference only, not editable */}
        <span style={{ fontSize: '14px', fontFamily: 'monospace', color: '#1e293b', userSelect: 'all' }}>
          {hex}
        </span>
      </div>
    </div>
  )
}
