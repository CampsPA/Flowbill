export default function Card({ children, className = '', style: extraStyle = {} }) {
  return (
    <div
      className={className}
      style={{
        background: '#fff',
        border: '1px solid #e8ecf2',
        borderRadius: '14px',
        boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
        ...extraStyle,
      }}
    >
      {children}
    </div>
  )
}
