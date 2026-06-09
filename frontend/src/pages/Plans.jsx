import { useEffect, useState } from 'react'
// Plans Delete: added Trash2 icon for delete button
import { Plus, Package, Trash2 } from 'lucide-react'
import api from '../api/client'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Modal from '../components/ui/Modal'
import Input, { Select } from '../components/ui/Input'
import EmptyState from '../components/ui/EmptyState'
import { Table, Thead, Th, Tbody, Tr, Td } from '../components/ui/Table'

function cents(v) {
  if (v == null) return '—'
  return '$' + (v / 100).toLocaleString('en-US', { minimumFractionDigits: 2 })
}
function fmt(dt) {
  return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export default function Plans() {
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(false)
  const [form, setForm] = useState({ name: '', price_dollars: '', interval: 'monthly', trial_days: '' })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  function load() {
    api.get('/plans/').then(r => setPlans(r.data)).catch(() => {}).finally(() => setLoading(false))
  }
  useEffect(load, [])

  function set(k, v) { setForm(f => ({ ...f, [k]: v })) }

  async function handleCreate(e) {
    e.preventDefault(); setSaving(true); setError('')
    try {
      await api.post('/plans/', {
        name: form.name,
        price_cents: Math.round(parseFloat(form.price_dollars) * 100),
        interval: form.interval,
        trial_days: form.trial_days ? parseInt(form.trial_days) : null,
      })
      setModal(false); setForm({ name: '', price_dollars: '', interval: 'monthly', trial_days: '' }); load()
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Error creating plan')
    } finally { setSaving(false) }
  }

  async function handleToggle(plan) {
    // N10: ask for confirmation before deactivating an active plan (no confirmation needed to re-activate)
    if (plan.is_active && !confirm(`Deactivate "${plan.name}"? Customers on this plan will keep their subscriptions but no new subscriptions can be created.`)) return
    try {
      await api.patch(`/plans/${plan.id}`, { is_active: !plan.is_active })
      load()
    } catch (err) {
      // N10: surface server errors (e.g. active subscriber check from backend)
      alert(err.response?.data?.detail ?? 'Failed to update plan status.')
    }
  }

  // Plans Delete: handler that confirms then calls DELETE /plans/{id}
  async function handleDelete(plan) {
    if (!confirm(`Permanently delete "${plan.name}"? This cannot be undone.`)) return
    try {
      await api.delete(`/plans/${plan.id}`)  // Plans Delete: calls the deactivate_plan endpoint (sets is_active=false)
      load()
    } catch (err) {
      // Plans Delete: show backend error (e.g. active subscriber check blocks the delete)
      alert(err.response?.data?.detail ?? 'Failed to delete plan.')
    }
  }

  const activePlans = plans.filter(p => p.is_active).length

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#0f172a', letterSpacing: '-0.5px', marginBottom: '6px' }}>Plans</h1>
          <p style={{ fontSize: '14px', color: '#94a3b8' }}>{activePlans} active plan{activePlans !== 1 ? 's' : ''}</p>
        </div>
        <Button onClick={() => setModal(true)}><Plus size={15} /> New Plan</Button>
      </div>

      {/* Table */}
      <Card>
        {loading ? (
          <div style={{ padding: '80px', textAlign: 'center', color: '#94a3b8', fontSize: '14px' }}>Loading…</div>
        ) : plans.length === 0 ? (
          <EmptyState icon={Package} title="No plans yet" description="Create your first billing plan to start accepting subscriptions." />
        ) : (
          <Table>
            <Thead>
              <Tr header>
                {/* Plans Delete: reduced Plan/Price/Created widths slightly to make room for 2 buttons */}
                <Th width="22%">Plan</Th>
                <Th width="12%">Price</Th>
                <Th width="12%">Interval</Th>
                <Th width="10%">Trial</Th>
                <Th width="11%">Status</Th>
                <Th width="13%">Created</Th>
                <Th width="20%"></Th>
              </Tr>
            </Thead>
            <Tbody>
              {plans.map(p => (
                <Tr key={p.id}>
                  <Td><span style={{ fontWeight: '600', color: '#0f172a' }}>{p.name}</span></Td>
                  <Td><span style={{ fontWeight: '600', color: '#1e293b' }}>{cents(p.price_cents)}</span></Td>
                  <Td><Badge status={p.interval} /></Td>
                  <Td muted>{p.trial_days ? `${p.trial_days}d` : null}</Td>
                  <Td><Badge status={p.is_active ? 'active' : 'cancelled'} label={p.is_active ? 'Active' : 'Inactive'} /></Td>
                  <Td muted>{fmt(p.created_at)}</Td>
                  <Td>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      <Button variant="ghost" size="sm" onClick={() => handleToggle(p)}>
                        {p.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
                      {/* Plans Delete: delete button — backend blocks if active subscribers exist */}
                      <Button variant="danger" size="sm" onClick={() => handleDelete(p)}>
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
      <Modal open={modal} onClose={() => { setModal(false); setError('') }} title="New Plan">
        <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {error && <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#dc2626' }}>{error}</div>}
          <Input label="Plan Name" placeholder="Pro Monthly" value={form.name} onChange={e => set('name', e.target.value)} required />
          <Input label="Price (USD)" type="number" step="0.01" min="0" placeholder="49.00" value={form.price_dollars} onChange={e => set('price_dollars', e.target.value)} required />
          <Select label="Billing Interval" value={form.interval} onChange={e => set('interval', e.target.value)}>
            <option value="monthly">Monthly</option>
            <option value="annual">Annual</option>
          </Select>
          <Input label="Trial Days (optional)" type="number" placeholder="14" value={form.trial_days} onChange={e => set('trial_days', e.target.value)} />
          <div style={{ display: 'flex', gap: '12px', paddingTop: '4px' }}>
            <Button type="button" variant="secondary" onClick={() => setModal(false)} style={{ flex: 1, justifyContent: 'center' }}>Cancel</Button>
            <Button type="submit" loading={saving} style={{ flex: 1, justifyContent: 'center' }}>Create Plan</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
