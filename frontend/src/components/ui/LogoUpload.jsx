import { useRef, useState } from 'react'
import { Upload, X } from 'lucide-react'

// Reusable logo upload component.
// Props:
//   value      — current base64 data URL (or existing https:// URL to display as preview)
//   onChange   — called with the base64 string when a file is selected, or '' when cleared
export default function LogoUpload({ value, onChange }) {
  const inputRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)

  function readFile(file) {
    if (!file) return
    const reader = new FileReader()
    reader.onload = e => onChange(e.target.result)  // result is a base64 data URL
    reader.readAsDataURL(file)
  }

  function handleFileChange(e) {
    readFile(e.target.files[0])
    // Reset the input so the same file can be re-selected after clearing
    e.target.value = ''
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragOver(false)
    readFile(e.dataTransfer.files[0])
  }

  function handleClear(e) {
    e.stopPropagation()  // don't re-open the file picker when clicking the X
    onChange('')
  }

  const borderColor = dragOver ? '#6366f1' : '#d1d5db'
  const bgColor     = dragOver ? '#eef2ff' : '#f8fafc'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
      <label style={{ fontSize: '13px', fontWeight: '600', color: '#374151' }}>Logo</label>

      {/* Drop zone / click-to-upload area */}
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        style={{
          border: `1.5px dashed ${borderColor}`,
          borderRadius: '10px',
          background: bgColor,
          padding: '16px',
          cursor: 'pointer',
          transition: 'border-color 0.15s, background 0.15s',
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          minHeight: '72px',
        }}
      >
        {value ? (
          // Preview + clear button
          <>
            <img
              src={value}
              alt="Logo preview"
              style={{ maxHeight: '80px', maxWidth: '160px', objectFit: 'contain', borderRadius: '6px', border: '1px solid #e8ecf2', background: '#fff', padding: '4px' }}
            />
            <div style={{ flex: 1 }}>
              <p style={{ fontSize: '13px', color: '#374151', fontWeight: '500' }}>Logo uploaded</p>
              <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>Click to replace</p>
            </div>
            {/* Clear button — removes the logo without opening the file picker */}
            <button
              type="button"
              onClick={handleClear}
              style={{ padding: '4px', borderRadius: '6px', border: '1px solid #e8ecf2', background: '#fff', cursor: 'pointer', color: '#94a3b8', display: 'flex', alignItems: 'center', flexShrink: 0 }}
            >
              <X size={14} />
            </button>
          </>
        ) : (
          // Empty state
          <>
            <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: '#eef2ff', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <Upload size={18} style={{ color: '#6366f1' }} />
            </div>
            <div>
              <p style={{ fontSize: '13px', color: '#374151', fontWeight: '500' }}>Click to upload or drag & drop</p>
              <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>JPG, PNG, GIF, SVG, WEBP</p>
            </div>
          </>
        )}
      </div>

      {/* Hidden file input — only accepts image formats */}
      <input
        ref={inputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.gif,.svg,.webp,image/jpeg,image/png,image/gif,image/svg+xml,image/webp"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
    </div>
  )
}
