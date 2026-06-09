const CELL_PAD = '16px 24px'

export function Table({ children }) {
  return (
    <div style={{ overflowX: 'auto', width: '100%' }}>
      <table style={{ width: '100%', tableLayout: 'fixed', borderCollapse: 'collapse', fontSize: '14px' }}>
        {children}
      </table>
    </div>
  )
}

export function Thead({ children }) {
  return <thead>{children}</thead>
}

export function Th({ children, width }) {
  return (
    <th style={{
      width,
      padding: '14px 24px',
      textAlign: 'left',
      fontSize: '11px',
      fontWeight: '700',
      color: '#94a3b8',
      textTransform: 'uppercase',
      letterSpacing: '0.07em',
      whiteSpace: 'nowrap',
      background: '#f8fafc',
      borderBottom: '1px solid #e8ecf2',
    }}>
      {children}
    </th>
  )
}

export function Tbody({ children }) {
  return <tbody>{children}</tbody>
}

export function Tr({ children, onClick, header }) {
  return (
    <tr
      onClick={onClick}
      style={{
        borderBottom: header ? 'none' : '1px solid #f1f5f9',
        cursor: onClick ? 'pointer' : undefined,
        transition: onClick ? 'background 0.1s' : undefined,
      }}
      onMouseEnter={onClick ? e => { e.currentTarget.style.background = '#fafbff' } : undefined}
      onMouseLeave={onClick ? e => { e.currentTarget.style.background = '' } : undefined}
    >
      {children}
    </tr>
  )
}

export function Td({ children, muted = false, mono = false, truncate = false }) {
  const isEmpty = children === null || children === undefined || children === ''
  return (
    <td style={{
      padding: CELL_PAD,
      textAlign: 'left',
      color: muted ? '#94a3b8' : '#1e293b',
      fontSize: mono ? '12px' : '14px',
      fontFamily: mono ? 'ui-monospace, SFMono-Regular, monospace' : undefined,
      overflow: truncate ? 'hidden' : undefined,
      textOverflow: truncate ? 'ellipsis' : undefined,
      whiteSpace: truncate ? 'nowrap' : undefined,
      height: '64px',
      verticalAlign: 'middle',
    }}>
      {isEmpty ? <span style={{ color: '#cbd5e1' }}>—</span> : children}
    </td>
  )
}
