import { useEffect, useState } from 'react'
import { Plus, Package, Trash2, Edit2, Check } from 'lucide-react'
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

  // ── Create modal state ────────────────────────────────────────────────────
  const [createModal, setCreateModal] = useState(false)
  const [createForm, setCreateForm] = useState({ name: '', price_dollars: '', interval: 'monthly', trial_days: '' })
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState('')

  // ── Edit modal state ──────────────────────────────────────────────────────
  // editPlan holds the full plan object being edited; null when modal is closed
  const [editPlan, setEditPlan] = useState(null)
  const [editForm, setEditForm] = useState({ name: '', price_dollars: '', interval: 'monthly', trial_days: '' })
  const [editSaving, setEditSaving] = useState(false)
  const [editError, setEditError] = useState('')
  const [editSuccess, setEditSuccess] = useState(false)

  function load() {
    api.get('/plans/').then(r => setPlans(r.data)).catch(() => {}).finally(() => setLoading(false))
  }
  useEffect(load, [])

  // ── Create handlers ───────────────────────────────────────────────────────
  function setCreate(k, v) { setCreateForm(f => ({ ...f, [k]: v })) }

  async function handleCreate(e) {
    e.preventDefault(); setCreating(true); setCreateError('')
    try {
      await api.post('/plans/', {
        name: createForm.name,
        price_cents: Math.round(parseFloat(createForm.price_dollars) * 100),
        interval: createForm.interval,
        trial_days: createForm.trial_days ? parseInt(createForm.trial_days) : null,
      })
      setCreateModal(false)
      setCreateForm({ name: '', price_dollars: '', interval: 'monthly', trial_days: '' })
      load()
    } catch (err) {
      setCreateError(err.response?.data?.detail ?? 'Error creating plan')
    } finally { setCreating(false) }
  }

  // ── Edit handlers ─────────────────────────────────────────────────────────
  // Opens the edit modal pre-populated with the selected plan's current values
  function openEdit(plan) {
    setEditPlan(plan)
    setEditForm({
      name: plan.name,
      price_dollars: (plan.price_cents / 100).toFixed(2),
      interval: plan.interval,
      trial_days: plan.trial_days != null ? String(plan.trial_days) : '',
    })
    setEditError('')
    setEditSuccess(false)
  }

  function setEdit(k, v) { setEditForm(f => ({ ...f, [k]: v })) }

  async function handleEdit(e) {
    e.preventDefault(); setEditSaving(true); setEditError(''); setEditSuccess(false)
    try {
      await api.patch(`/plans/${editPlan.id}`, {
        name: editForm.name,
        price_cents: Math.round(parseFloat(editForm.price_dollars) * 100),
        interval: editForm.interval,
        trial_days: editForm.trial_days ? parseInt(editForm.trial_days) : null,
      })
      setEditSuccess(true)
      load() // refresh the table so the new values appear immediately
      setTimeout(() => {
        // Auto-close after a brief success flash so the user sees it
        setEditPlan(null)
        setEditSuccess(false)
      }, 1200)
    } catch (err) {
      setEditError(err.response?.data?.detail ?? 'Error updating plan')
    } finally { setEditSaving(false) }
  }

  // ── Activate / Deactivate toggle ──────────────────────────────────────────
  async function handleToggle(plan) {
    if (plan.is_active && !confirm(`Deactivate "${plan.name}"? Customers on this plan will keep their subscriptions but no new subscriptions can be created.`)) return
    try {
      await api.patch(`/plans/${plan.id}`, { is_active: !plan.is_active })
      load()
    } catch (err) {
      alert(err.response?.data?.detail ?? 'Failed to update plan status.')
    }
  }

  // ── Delete handler ────────────────────────────────────────────────────────
  async function handleDelete(plan) {
    if (!confirm('Are you sure you want to delete this plan? This cannot be undone.')) return
    try {
      await api.delete(`/plans/${plan.id}`)
      load()
    } catch (err) {
      // Backend returns "Cannot delete a plan with active subscribers. Deactivate it instead."
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
        <Button onClick={() => { setCreateModal(true); setCreateError('') }}>
          <Plus size={15} /> New Plan
        </Button>
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
                <Th width="20%">Plan</Th>
                <Th width="11%">Price</Th>
                <Th width="11%">Interval</Th>
                <Th width="9%">Trial</Th>
                <Th width="10%">Status</Th>
                <Th width="13%">Created</Th>
                {/* Actions column — wide enough for Edit + Deactivate + Delete */}
                <Th width="26%"></Th>
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
                      {/* Edit button — opens the edit modal for this plan */}
                      <Button variant="ghost" size="sm" onClick={() => openEdit(p)}>
                        <Edit2 size={12} /> Edit
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleToggle(p)}>
                        {p.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
                      {/* Delete button — backend blocks this if active subscribers exist */}
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

      {/* ── Create modal ─────────────────────────────────────────────────── */}
      <Modal open={createModal} onClose={() => { setCreateModal(false); setCreateError('') }} title="New Plan">
        <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {createError && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#dc2626' }}>
              {createError}
            </div>
          )}
          <Input label="Plan Name" placeholder="Pro Monthly" value={createForm.name} onChange={e => setCreate('name', e.target.value)} required />
          <Input label="Price (USD)" type="number" step="0.01" min="0" placeholder="49.00" value={createForm.price_dollars} onChange={e => setCreate('price_dollars', e.target.value)} required />
          <Select label="Billing Interval" value={createForm.interval} onChange={e => setCreate('interval', e.target.value)}>
            <option value="monthly">Monthly</option>
            <option value="annual">Annual</option>
          </Select>
          <Input label="Trial Days (optional)" type="number" placeholder="14" value={createForm.trial_days} onChange={e => setCreate('trial_days', e.target.value)} />
          <div style={{ display: 'flex', gap: '12px', paddingTop: '4px' }}>
            <Button type="button" variant="secondary" onClick={() => setCreateModal(false)} style={{ flex: 1, justifyContent: 'center' }}>Cancel</Button>
            <Button type="submit" loading={creating} style={{ flex: 1, justifyContent: 'center' }}>Create Plan</Button>
          </div>
        </form>
      </Modal>

      {/* ── Edit modal ───────────────────────────────────────────────────── */}
      <Modal open={!!editPlan} onClose={() => { setEditPlan(null); setEditError(''); setEditSuccess(false) }} title={`Edit Plan — ${editPlan?.name ?? ''}`}>
        <form onSubmit={handleEdit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Success banner */}
          {editSuccess && (
            <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#15803d', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Check size={14} /> Plan updated successfully.
            </div>
          )}
          {/* Error banner */}
          {editError && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#dc2626' }}>
              {editError}
            </div>
          )}
          <Input label="Plan Name" placeholder="Pro Monthly" value={editForm.name} onChange={e => setEdit('name', e.target.value)} required />
          <Input label="Price (USD)" type="number" step="0.01" min="0" placeholder="49.00" value={editForm.price_dollars} onChange={e => setEdit('price_dollars', e.target.value)} required />
          <Select label="Billing Interval" value={editForm.interval} onChange={e => setEdit('interval', e.target.value)}>
            <option value="monthly">Monthly</option>
            <option value="annual">Annual</option>
          </Select>
          <Input label="Trial Days (optional)" type="number" placeholder="14" value={editForm.trial_days} onChange={e => setEdit('trial_days', e.target.value)} />
          <div style={{ display: 'flex', gap: '12px', paddingTop: '4px' }}>
            <Button type="button" variant="secondary" onClick={() => setEditPlan(null)} style={{ flex: 1, justifyContent: 'center' }}>Cancel</Button>
            <Button type="submit" loading={editSaving} style={{ flex: 1, justifyContent: 'center' }}>Save Changes</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
