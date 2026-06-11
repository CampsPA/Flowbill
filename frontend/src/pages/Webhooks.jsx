import { useEffect, useState } from 'react'
// I5: added Edit2 icon for edit button
import { Plus, Webhook, Trash2, Send, Copy, Check, Edit2 } from 'lucide-react'
import api from '../api/client'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Modal from '../components/ui/Modal'
import Input, { Select } from '../components/ui/Input'
import EmptyState from '../components/ui/EmptyState'
import { Table, Thead, Th, Tbody, Tr, Td } from '../components/ui/Table'

const EVENT_OPTIONS = [
  'subscription.created', 'subscription.cancelled', 'subscription.paused',
  'invoice.created', 'invoice.paid', 'invoice.past_due',
  'payment.succeeded', 'payment.failed',
]

function fmt(dt) {
  return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export default function Webhooks() {
  const [endpoints, setEndpoints] = useState([])
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(false)
  const [deliverModal, setDeliverModal] = useState(null)
  const [form, setForm] = useState({ url: '', events: [], customer_id: '' })
  const [deliverForm, setDeliverForm] = useState({ event_type: '', payload: '{}' })
  const [saving, setSaving] = useState(false)
  const [delivering, setDelivering] = useState(false)
  const [error, setError] = useState('')
  const [secret, setSecret] = useState('')
  const [copied, setCopied] = useState(false)
  // I5: state for edit modal — editModal holds the endpoint object being edited
  const [editModal, setEditModal] = useState(null)
  const [editForm, setEditForm] = useState({ url: '', events: [] })
  const [editSaving, setEditSaving] = useState(false)
  const [editError, setEditError] = useState('')

  function load() {
    api.get('/webhooks/').then(r => setEndpoints(r.data)).catch(() => {}).finally(() => setLoading(false))
  }
  useEffect(() => {
    load()
    api.get('/customers/').then(r => setCustomers(r.data.filter(c => c.is_active))).catch(() => {})
  }, [])

  function toggleEvent(evt) {
    setForm(f => ({
      ...f,
      events: f.events.includes(evt) ? f.events.filter(e => e !== evt) : [...f.events, evt],
    }))
  }

  function copySecret() {
    navigator.clipboard.writeText(secret)
    setCopied(true); setTimeout(() => setCopied(false), 2000)
  }

  async function handleCreate(e) {
    e.preventDefault(); setSaving(true); setError('')
    console.log('[Webhooks] form state at submit:', form)
    try {
      const { data } = await api.post('/webhooks/', {
        url: form.url,
        events: form.events,
        customer_id: parseInt(form.customer_id),
      })
      setSecret(data.secret); setModal(false); setForm({ url: '', events: [], customer_id: '' }); load()
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Error registering endpoint')
    } finally { setSaving(false) }
  }

  async function handleDelete(id) {
    if (!confirm('Deactivate this endpoint?')) return
    await api.delete(`/webhooks/${id}`); load()
  }

  // I5: toggle an event in the edit form's events array
  function toggleEditEvent(evt) {
    setEditForm(f => ({
      ...f,
      events: f.events.includes(evt) ? f.events.filter(e => e !== evt) : [...f.events, evt],
    }))
  }

  // I5: submit PATCH to update the endpoint's url and/or events
  async function handleEdit(e) {
    e.preventDefault(); setEditSaving(true); setEditError('')
    try {
      await api.patch(`/webhooks/${editModal.id}`, { url: editForm.url, events: editForm.events })
      setEditModal(null); load()  // I5: refresh list after saving
    } catch (err) {
      setEditError(err.response?.data?.detail ?? 'Error updating endpoint')
    } finally { setEditSaving(false) }
  }

  async function handleDeliver(e) {
    e.preventDefault(); setDelivering(true)
    try {
      let payload; try { payload = JSON.parse(deliverForm.payload) } catch { payload = {} }
      await api.post(`/webhooks/${deliverModal}/deliver`, { event_type: deliverForm.event_type, payload })
      setDeliverModal(null); alert('Webhook delivered successfully!')
    } catch (err) { alert(err.response?.data?.detail ?? 'Delivery failed') }
    finally { setDelivering(false) }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#0f172a', letterSpacing: '-0.5px', marginBottom: '6px' }}>Webhooks</h1>
          <p style={{ fontSize: '14px', color: '#94a3b8' }}>Manage event endpoints and test deliveries</p>
        </div>
        <Button onClick={() => { setSecret(''); setModal(true) }}><Plus size={15} /> Add Endpoint</Button>
      </div>

      {/* Signing secret banner */}
      {secret && (
        <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '14px', padding: '20px 24px' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '12px' }}>
            <div>
              <p style={{ fontSize: '14px', fontWeight: '600', color: '#15803d', marginBottom: '4px' }}>Signing Secret — save this now</p>
              <p style={{ fontSize: '13px', color: '#16a34a' }}>Shown only once. Use it to verify webhook signatures.</p>
            </div>
            <button onClick={copySecret} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: '600', color: '#15803d', background: '#dcfce7', border: 'none', borderRadius: '8px', padding: '6px 12px', cursor: 'pointer' }}>
              {copied ? <><Check size={12} /> Copied</> : <><Copy size={12} /> Copy</>}
            </button>
          </div>
          <code style={{ display: 'block', background: '#fff', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '12px 16px', fontSize: '12px', fontFamily: 'ui-monospace, monospace', color: '#1e293b', wordBreak: 'break-all' }}>{secret}</code>
        </div>
      )}

      {/* Table */}
      <Card>
        {loading ? (
          <div style={{ padding: '80px', textAlign: 'center', color: '#94a3b8', fontSize: '14px' }}>Loading…</div>
        ) : endpoints.length === 0 ? (
          <EmptyState icon={Webhook} title="No webhook endpoints" description="Register an endpoint to receive event notifications." />
        ) : (
          <Table>
            <Thead>
              <Tr header>
                <Th width="30%">URL</Th>
                <Th width="32%">Events</Th>
                <Th width="12%">Status</Th>
                <Th width="14%">Created</Th>
                <Th width="12%">Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {endpoints.map(ep => (
                <Tr key={ep.id}>
                  <Td mono truncate>{ep.url}</Td>
                  <Td>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                      {ep.events.slice(0, 3).map(ev => (
                        <span key={ev} style={{ background: '#eef2ff', color: '#4f46e5', fontSize: '11px', fontWeight: '600', padding: '2px 8px', borderRadius: '999px', border: '1px solid #c7d2fe' }}>{ev}</span>
                      ))}
                      {ep.events.length > 3 && <span style={{ fontSize: '12px', color: '#94a3b8' }}>+{ep.events.length - 3}</span>}
                    </div>
                  </Td>
                  <Td><Badge status={ep.is_active ? 'active' : 'cancelled'} label={ep.is_active ? 'Active' : 'Inactive'} /></Td>
                  <Td muted>{fmt(ep.created_at)}</Td>
                  <Td>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      {/* I5: Edit button opens the edit modal pre-populated with current values */}
                      <Button variant="ghost" size="sm" onClick={() => { setEditForm({ url: ep.url, events: [...ep.events] }); setEditError(''); setEditModal(ep) }}>
                        <Edit2 size={12} /> Edit
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => { setDeliverForm({ event_type: '', payload: '{}' }); setDeliverModal(ep.id) }}>
                        <Send size={12} /> Test
                      </Button>
                      <Button variant="danger" size="sm" onClick={() => handleDelete(ep.id)}>
                        <Trash2 size={12} />
                      </Button>
                    </div>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        )}
      </Card>

      {/* Create modal */}
      <Modal open={modal} onClose={() => { setModal(false); setError('') }} title="Register Webhook Endpoint" size="lg">
        <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {error && <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#dc2626' }}>{error}</div>}
          <Select label="Customer" value={form.customer_id} onChange={e => setForm(f => ({ ...f, customer_id: e.target.value }))} required>
            <option value="">— Select a customer —</option>
            {customers.map(c => <option key={c.id} value={c.id}>{c.name} ({c.email})</option>)}
          </Select>
          <Input label="Endpoint URL" type="url" placeholder="https://example.com/webhooks" value={form.url} onChange={e => setForm(f => ({ ...f, url: e.target.value }))} required />
          <div>
            <p style={{ fontSize: '13px', fontWeight: '600', color: '#374151', marginBottom: '12px' }}>Events to subscribe</p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              {EVENT_OPTIONS.map(ev => (
                <label key={ev} style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', padding: '10px 12px', borderRadius: '8px', background: form.events.includes(ev) ? '#f5f3ff' : '#f8fafc', border: `1px solid ${form.events.includes(ev) ? '#c7d2fe' : '#e8ecf2'}` }}>
                  <input type="checkbox" checked={form.events.includes(ev)} onChange={() => toggleEvent(ev)} style={{ width: '14px', height: '14px', accentColor: '#6366f1' }} />
                  <span style={{ fontSize: '12px', fontWeight: '500', color: '#374151' }}>{ev}</span>
                </label>
              ))}
            </div>
          </div>
          <div style={{ display: 'flex', gap: '12px', paddingTop: '4px' }}>
            <Button type="button" variant="secondary" onClick={() => setModal(false)} style={{ flex: 1, justifyContent: 'center' }}>Cancel</Button>
            <Button type="submit" loading={saving} disabled={form.events.length === 0} style={{ flex: 1, justifyContent: 'center' }}>Register Endpoint</Button>
          </div>
        </form>
      </Modal>

      {/* I5: Edit endpoint modal — pre-populated with existing URL and events */}
      <Modal open={!!editModal} onClose={() => { setEditModal(null); setEditError('') }} title="Edit Webhook Endpoint" size="lg">
        <form onSubmit={handleEdit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {editError && <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#dc2626' }}>{editError}</div>}
          {/* I5: URL field pre-populated from editForm state */}
          <Input label="Endpoint URL" type="url" placeholder="https://example.com/webhooks" value={editForm.url} onChange={e => setEditForm(f => ({ ...f, url: e.target.value }))} required />
          <div>
            <p style={{ fontSize: '13px', fontWeight: '600', color: '#374151', marginBottom: '12px' }}>Events to subscribe</p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              {/* I5: same event checkboxes as create modal, reflecting editForm.events */}
              {EVENT_OPTIONS.map(ev => (
                <label key={ev} style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', padding: '10px 12px', borderRadius: '8px', background: editForm.events.includes(ev) ? '#f5f3ff' : '#f8fafc', border: `1px solid ${editForm.events.includes(ev) ? '#c7d2fe' : '#e8ecf2'}` }}>
                  <input type="checkbox" checked={editForm.events.includes(ev)} onChange={() => toggleEditEvent(ev)} style={{ width: '14px', height: '14px', accentColor: '#6366f1' }} />
                  <span style={{ fontSize: '12px', fontWeight: '500', color: '#374151' }}>{ev}</span>
                </label>
              ))}
            </div>
          </div>
          <div style={{ display: 'flex', gap: '12px', paddingTop: '4px' }}>
            <Button type="button" variant="secondary" onClick={() => setEditModal(null)} style={{ flex: 1, justifyContent: 'center' }}>Cancel</Button>
            {/* I5: disabled if no events selected */}
            <Button type="submit" loading={editSaving} disabled={editForm.events.length === 0} style={{ flex: 1, justifyContent: 'center' }}>Save Changes</Button>
          </div>
        </form>
      </Modal>

      {/* Test delivery modal */}
      <Modal open={!!deliverModal} onClose={() => setDeliverModal(null)} title="Test Webhook Delivery">
        <form onSubmit={handleDeliver} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* N2: replaced free-text input with a dropdown so users can only pick valid event types */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '13px', fontWeight: '600', color: '#374151' }}>Event Type</label>
            <select
              value={deliverForm.event_type}
              onChange={e => setDeliverForm(f => ({ ...f, event_type: e.target.value }))}
              required
              style={{ height: '48px', padding: '0 16px', border: '1px solid #d1d5db', borderRadius: '10px', fontSize: '14px', color: '#1e293b', background: '#fff', outline: 'none', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}
            >
              <option value="">— Select event type —</option>
              {/* N2: EVENT_OPTIONS is already defined at the top of this file */}
              {EVENT_OPTIONS.map(ev => <option key={ev} value={ev}>{ev}</option>)}
            </select>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '13px', fontWeight: '600', color: '#374151' }}>Payload (JSON)</label>
            <textarea
              value={deliverForm.payload}
              onChange={e => setDeliverForm(f => ({ ...f, payload: e.target.value }))}
              rows={6}
              style={{ border: '1px solid #d1d5db', borderRadius: '10px', padding: '12px 16px', fontSize: '13px', fontFamily: 'ui-monospace, monospace', color: '#1e293b', background: '#fff', outline: 'none', resize: 'none', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}
            />
          </div>
          <div style={{ display: 'flex', gap: '12px', paddingTop: '4px' }}>
            <Button type="button" variant="secondary" onClick={() => setDeliverModal(null)} style={{ flex: 1, justifyContent: 'center' }}>Cancel</Button>
            <Button type="submit" loading={delivering} style={{ flex: 1, justifyContent: 'center' }}><Send size={14} /> Send Test</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
