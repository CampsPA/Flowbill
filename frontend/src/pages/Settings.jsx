import { useEffect, useState } from 'react'
import { Save, Settings as SettingsIcon } from 'lucide-react'
import api from '../api/client'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input, { Select } from '../components/ui/Input'
import LogoUpload from '../components/ui/LogoUpload'
import ColorPicker from '../components/ui/ColorPicker'

export default function Settings() {
  const [customers, setCustomers] = useState([])
  const [customerId, setCustomerId] = useState('')
  const [settings, setSettings] = useState(null)
  const [form, setForm] = useState({ company_name: '', logo_url: '', address: '', brand_color: '', email_footer: '' })
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  // I6: track the moment of the last successful save so we show a live "Last updated" time
  const [lastSaved, setLastSaved] = useState(null)

  useEffect(() => { api.get('/customers/').then(r => setCustomers(r.data)).catch(() => {}) }, [])

  useEffect(() => {
    if (!customerId) return
    api.get(`/tenant-settings/${customerId}`)
      .then(r => {
        setSettings(r.data)
        setForm({
          company_name: r.data.company_name ?? '',
          logo_url: r.data.logo_url ?? '',
          address: r.data.address ?? '',
          brand_color: r.data.brand_color ?? '',
          email_footer: r.data.email_footer ?? '',
        })
      })
      .catch(() => {
        setSettings(null)
        setForm({ company_name: '', logo_url: '', address: '', brand_color: '', email_footer: '' })
      })
  }, [customerId])

  function set(k, v) { setForm(f => ({ ...f, [k]: v })) }

  async function handleSave(e) {
    e.preventDefault(); setSaving(true); setError(''); setSuccess(false)
    try {
      const payload = {}
      Object.entries(form).forEach(([k, v]) => { if (v !== '') payload[k] = v })
      await api.put(`/tenant-settings/${customerId}`, payload)
      setSuccess(true); setTimeout(() => setSuccess(false), 3000)
      setLastSaved(new Date())  // I6: stamp the exact moment of successful save
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Error saving settings')
    } finally { setSaving(false) }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#0f172a', letterSpacing: '-0.5px', marginBottom: '6px' }}>Tenant Settings</h1>
        <p style={{ fontSize: '14px', color: '#94a3b8' }}>Configure branding and preferences per customer</p>
      </div>

      {/* Customer selector */}
      <Card style={{ padding: '20px 24px' }}>
        <Select label="Select Customer" value={customerId} onChange={e => setCustomerId(e.target.value)}>
          <option value="">— Select a customer —</option>
          {customers.map(c => <option key={c.id} value={c.id}>{c.name} ({c.email})</option>)}
        </Select>
      </Card>

      {/* Settings form */}
      {customerId && (
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '20px 24px', borderBottom: '1px solid #e8ecf2' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <SettingsIcon size={15} color="#94a3b8" />
              <h2 style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Branding Configuration</h2>
            </div>
            {/* I6: show lastSaved timestamp if we've saved this session, else fall back to created_at from the API */}
            {(lastSaved || settings) && (
              <span style={{ fontSize: '13px', color: '#94a3b8' }}>
                Last updated: {lastSaved
                  ? lastSaved.toLocaleString()          // I6: live timestamp from this session's save
                  : new Date(settings.created_at).toLocaleDateString()}  {/* I6: server timestamp before first save */}
              </span>
            )}
          </div>

          <div style={{ padding: '32px' }}>
            {success && (
              <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '10px', padding: '14px 16px', fontSize: '14px', color: '#15803d', marginBottom: '28px' }}>
                Settings saved successfully.
              </div>
            )}
            {error && (
              <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '14px 16px', fontSize: '14px', color: '#dc2626', marginBottom: '28px' }}>{error}</div>
            )}

            <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '520px' }}>
              <Input label="Company Name" placeholder="Acme Corp" value={form.company_name} onChange={e => set('company_name', e.target.value)} />
              <LogoUpload value={form.logo_url} onChange={v => set('logo_url', v)} />
              <Input label="Business Address" placeholder="123 Main St, New York, NY 10001" value={form.address} onChange={e => set('address', e.target.value)} />

              <ColorPicker label="Brand Color" value={form.brand_color} onChange={v => set('brand_color', v)} />

              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <label style={{ fontSize: '13px', fontWeight: '600', color: '#374151' }}>Email Footer</label>
                <textarea
                  value={form.email_footer}
                  onChange={e => set('email_footer', e.target.value)}
                  rows={3}
                  placeholder="© 2025 Acme Corp. All rights reserved."
                  style={{ border: '1px solid #d1d5db', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#1e293b', background: '#fff', outline: 'none', resize: 'none', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', fontFamily: 'inherit' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '8px' }}>
                <Button type="submit" loading={saving}><Save size={14} /> Save Settings</Button>
              </div>
            </form>
          </div>
        </Card>
      )}
    </div>
  )
}
