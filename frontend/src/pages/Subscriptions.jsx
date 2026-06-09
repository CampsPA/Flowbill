import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Plus, RefreshCw, PauseCircle, XCircle, ArrowUpCircle, PlayCircle, Edit2, Trash2, Check } from 'lucide-react'
import api from '../api/client'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Modal from '../components/ui/Modal'
import Input, { Select } from '../components/ui/Input'
import EmptyState from '../components/ui/EmptyState'
import { Table, Thead, Th, Tbody, Tr, Td } from '../components/ui/Table'

function fmt(dt) {
  if (!dt) return null
  return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
// Convert a UTC ISO string to a YYYY-MM-DD string suitable for <input type="date">
function toDateInput(dt) {
  if (!dt) return ''
  return new Date(dt).toISOString().split('T')[0]
}
function cents(v) {
  if (v == null) return ''
  return '$' + (v / 100).toLocaleString('en-US', { minimumFractionDigits: 2 })
}

export default function Subscriptions() {
  const [searchParams] = useSearchParams()
  const defaultCustomerId = searchParams.get('customer_id') ?? ''

  const [customerId, setCustomerId] = useState(defaultCustomerId)
  const [customers, setCustomers] = useState([])
  const [plans, setPlans] = useState([])
  const [subs, setSubs] = useState([])
  const [loading, setLoading] = useState(false)

  // ── Create modal ────────────────────────────────────────────────────────────
  const [createModal, setCreateModal] = useState(false)
  const [createForm, setCreateForm] = useState({ customer_id: defaultCustomerId, plan_id: '' })
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState('')

  // ── Change-plan (upgrade) modal ─────────────────────────────────────────────
  const [upgradeModal, setUpgradeModal] = useState(null)
  const [upgradePlanId, setUpgradePlanId] = useState('')
  const [upgrading, setUpgrading] = useState(false)
  const [upgradeError, setUpgradeError] = useState('')

  // ── Edit modal state ────────────────────────────────────────────────────────
  // editSub holds the full sub object; null means modal is closed
  const [editSub, setEditSub] = useState(null)
  const [editForm, setEditForm] = useState({ status: 'active', current_period_start: '', current_period_end: '' })
  const [editSaving, setEditSaving] = useState(false)
  const [editError, setEditError] = useState('')
  const [editSuccess, setEditSuccess] = useState(false)

  // ── I4: per-row action loading ──────────────────────────────────────────────
  // stores sub.id while any action (pause/resume/cancel/delete) is in-flight
  const [actionLoading, setActionLoading] = useState(null)

  useEffect(() => {
    Promise.all([
      api.get('/customers/').catch(() => ({ data: [] })),
      api.get('/plans/').catch(() => ({ data: [] })),
    ]).then(([c, p]) => {
      setCustomers(c.data)
      setPlans(p.data.filter(p => p.is_active))
    })
  }, [])

  function loadSubs(cid) {
    if (!cid) return
    setLoading(true)
    api.get(`/subscriptions/?customer_id=${cid}`)
      .then(r => setSubs(r.data))
      .catch(() => setSubs([]))
      .finally(() => setLoading(false))
  }
  useEffect(() => { if (customerId) loadSubs(customerId) }, [customerId])

  // ── Create handler ──────────────────────────────────────────────────────────
  async function handleCreate(e) {
    e.preventDefault(); setCreating(true); setCreateError('')
    try {
      await api.post('/subscriptions/', {
        customer_id: parseInt(createForm.customer_id),
        plan_id: parseInt(createForm.plan_id),
      })
      setCreateModal(false); setCustomerId(createForm.customer_id); loadSubs(createForm.customer_id)
    } catch (err) {
      setCreateError(err.response?.data?.detail ?? 'Error creating subscription')
    } finally { setCreating(false) }
  }

  // ── Pause / Resume / Cancel handlers ────────────────────────────────────────
  async function handlePause(sub) {
    setActionLoading(sub.id)
    // I10: paused_at is set server-side; do not include it in the request body
    await api.patch(`/subscriptions/${sub.id}`, { status: 'paused' })
    loadSubs(customerId)
    setActionLoading(null)
  }
  async function handleResume(sub) {
    setActionLoading(sub.id)
    await api.patch(`/subscriptions/${sub.id}`, { status: 'active' }); loadSubs(customerId)
    setActionLoading(null)
  }
  async function handleCancel(sub) {
    if (!confirm('Cancel this subscription? This cannot be undone.')) return
    setActionLoading(sub.id)
    await api.delete(`/subscriptions/${sub.id}`); loadSubs(customerId)
    setActionLoading(null)
  }

  // ── Upgrade (change plan) handler ────────────────────────────────────────────
  async function handleUpgrade(e) {
    e.preventDefault(); setUpgrading(true); setUpgradeError('')
    try {
      await api.patch(`/subscriptions/${upgradeModal.id}`, { plan_id: parseInt(upgradePlanId) })
      setUpgradeModal(null); loadSubs(customerId)
    } catch (err) {
      setUpgradeError(err.response?.data?.detail ?? 'Error changing plan')
    } finally { setUpgrading(false) }
  }

  // ── Edit modal handlers ──────────────────────────────────────────────────────
  // Opens the edit modal pre-populated with the subscription's current values
  function openEdit(sub) {
    setEditSub(sub)
    setEditForm({
      status: sub.status,
      current_period_start: toDateInput(sub.current_period_start),
      current_period_end: toDateInput(sub.current_period_end),
    })
    setEditError('')
    setEditSuccess(false)
  }

  function setEdit(k, v) { setEditForm(f => ({ ...f, [k]: v })) }

  async function handleEdit(e) {
    e.preventDefault(); setEditSaving(true); setEditError(''); setEditSuccess(false)
    try {
      await api.patch(`/subscriptions/${editSub.id}`, {
        status: editForm.status,
        // Convert YYYY-MM-DD back to ISO 8601 for the backend
        current_period_start: editForm.current_period_start ? new Date(editForm.current_period_start).toISOString() : null,
        current_period_end: editForm.current_period_end ? new Date(editForm.current_period_end).toISOString() : null,
      })
      setEditSuccess(true)
      loadSubs(customerId) // refresh the table immediately
      setTimeout(() => {
        // Auto-close after success flash
        setEditSub(null)
        setEditSuccess(false)
      }, 1200)
    } catch (err) {
      setEditError(err.response?.data?.detail ?? 'Error updating subscription')
    } finally { setEditSaving(false) }
  }

  // ── Delete (hard-delete) handler ─────────────────────────────────────────────
  async function handleDelete(sub) {
    if (!confirm('Are you sure you want to delete this subscription? This cannot be undone.')) return
    setActionLoading(sub.id)
    try {
      // DELETE /subscriptions/{id} cancels and removes the subscription
      await api.delete(`/subscriptions/${sub.id}`)
      loadSubs(customerId)
    } catch (err) {
      alert(err.response?.data?.detail ?? 'Failed to delete subscription.')
    } finally { setActionLoading(null) }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#0f172a', letterSpacing: '-0.5px', marginBottom: '6px' }}>Subscriptions</h1>
          <p style={{ fontSize: '14px', color: '#94a3b8' }}>Manage customer subscriptions</p>
        </div>
        <Button onClick={() => { setCreateForm({ customer_id: customerId, plan_id: '' }); setCreateModal(true) }}>
          <Plus size={15} /> New Subscription
        </Button>
      </div>

      {/* Customer filter */}
      <Card style={{ padding: '20px 24px' }}>
        <Select label="Filter by Customer" value={customerId} onChange={e => setCustomerId(e.target.value)}>
          <option value="">— Select a customer —</option>
          {customers.map(c => <option key={c.id} value={c.id}>{c.name} ({c.email})</option>)}
        </Select>
      </Card>

      {/* Subscriptions table */}
      <Card>
        {!customerId ? (
          <EmptyState icon={RefreshCw} title="Select a customer" description="Choose a customer above to view their subscriptions." />
        ) : loading ? (
          <div style={{ padding: '80px', textAlign: 'center', color: '#94a3b8', fontSize: '14px' }}>Loading…</div>
        ) : subs.length === 0 ? (
          <EmptyState icon={RefreshCw} title="No subscriptions" description="This customer has no subscriptions yet." />
        ) : (
          <Table>
            <Thead>
              <Tr header>
                <Th width="6%">ID</Th>
                <Th width="22%">Plan</Th>
                <Th width="11%">Status</Th>
                <Th width="13%">Period Start</Th>
                <Th width="13%">Period End</Th>
                {/* Actions column wide enough for Edit + Pause/Resume + Change + Cancel + Delete */}
                <Th width="35%">Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {subs.map(s => {
                const plan = plans.find(p => p.id === s.plan_id)
                // isActing disables all buttons for this row while any action is in-flight
                const isActing = actionLoading === s.id
                return (
                  <Tr key={s.id}>
                    <Td mono muted>#{s.id}</Td>
                    <Td>
                      <div>
                        <p style={{ fontWeight: '600', color: '#0f172a', fontSize: '14px' }}>{plan?.name ?? `Plan #${s.plan_id}`}</p>
                        {plan && <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>{cents(plan.price_cents)} / {plan.interval}</p>}
                      </div>
                    </Td>
                    <Td><Badge status={s.status} /></Td>
                    <Td muted>{fmt(s.current_period_start)}</Td>
                    <Td muted>{fmt(s.current_period_end)}</Td>
                    <Td>
                      <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                        {/* Edit button — opens the edit modal for this subscription */}
                        <Button variant="ghost" size="sm" disabled={isActing} onClick={() => openEdit(s)}>
                          <Edit2 size={12} /> Edit
                        </Button>
                        {s.status === 'active' && (
                          <Button variant="ghost" size="sm" loading={isActing} disabled={isActing} onClick={() => handlePause(s)}>
                            <PauseCircle size={12} /> Pause
                          </Button>
                        )}
                        {s.status === 'paused' && (
                          <Button variant="ghost" size="sm" loading={isActing} disabled={isActing} onClick={() => handleResume(s)}>
                            <PlayCircle size={12} /> Resume
                          </Button>
                        )}
                        {s.status !== 'cancelled' && (
                          <Button variant="ghost" size="sm" disabled={isActing} onClick={() => { setUpgradePlanId(''); setUpgradeError(''); setUpgradeModal(s) }}>
                            <ArrowUpCircle size={12} /> Change
                          </Button>
                        )}
                        {s.status !== 'cancelled' && (
                          <Button variant="danger" size="sm" loading={isActing} disabled={isActing} onClick={() => handleCancel(s)}>
                            <XCircle size={12} /> Cancel
                          </Button>
                        )}
                        {/* Delete button — hard-deletes the subscription record */}
                        <Button variant="danger" size="sm" loading={isActing} disabled={isActing} onClick={() => handleDelete(s)}>
                          <Trash2 size={12} />
                        </Button>
                      </div>
                    </Td>
                  </Tr>
                )
              })}
            </Tbody>
          </Table>
        )}
      </Card>

      {/* ── Create modal ─────────────────────────────────────────────────────── */}
      <Modal open={createModal} onClose={() => { setCreateModal(false); setCreateError('') }} title="New Subscription">
        <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {createError && <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#dc2626' }}>{createError}</div>}
          <Select label="Customer" value={createForm.customer_id} onChange={e => setCreateForm(f => ({ ...f, customer_id: e.target.value }))} required>
            <option value="">— Select customer —</option>
            {customers.map(c => <option key={c.id} value={c.id}>{c.name} ({c.email})</option>)}
          </Select>
          <Select label="Plan" value={createForm.plan_id} onChange={e => setCreateForm(f => ({ ...f, plan_id: e.target.value }))} required>
            <option value="">— Select plan —</option>
            {plans.map(p => <option key={p.id} value={p.id}>{p.name} — {cents(p.price_cents)} / {p.interval}</option>)}
          </Select>
          <div style={{ display: 'flex', gap: '12px', paddingTop: '4px' }}>
            <Button type="button" variant="secondary" onClick={() => setCreateModal(false)} style={{ flex: 1, justifyContent: 'center' }}>Cancel</Button>
            <Button type="submit" loading={creating} style={{ flex: 1, justifyContent: 'center' }}>Create Subscription</Button>
          </div>
        </form>
      </Modal>

      {/* ── Change-plan modal ─────────────────────────────────────────────────── */}
      <Modal open={!!upgradeModal} onClose={() => setUpgradeModal(null)} title="Change Plan">
        <form onSubmit={handleUpgrade} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {upgradeError && <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#dc2626' }}>{upgradeError}</div>}
          {upgradeModal && (() => {
            const current = plans.find(p => p.id === upgradeModal.plan_id)
            return current ? (
              <div style={{ background: '#f8fafc', border: '1px solid #e8ecf2', borderRadius: '10px', padding: '14px 16px' }}>
                <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Current plan</p>
                <p style={{ fontSize: '14px', fontWeight: '600', color: '#0f172a' }}>{current.name} — {cents(current.price_cents)} / {current.interval}</p>
              </div>
            ) : null
          })()}
          <Select label="New Plan" value={upgradePlanId} onChange={e => setUpgradePlanId(e.target.value)} required>
            <option value="">— Select new plan —</option>
            {plans.filter(p => p.id !== upgradeModal?.plan_id).map(p => (
              <option key={p.id} value={p.id}>{p.name} — {cents(p.price_cents)} / {p.interval}</option>
            ))}
          </Select>
          <div style={{ display: 'flex', gap: '12px', paddingTop: '4px' }}>
            <Button type="button" variant="secondary" onClick={() => setUpgradeModal(null)} style={{ flex: 1, justifyContent: 'center' }}>Cancel</Button>
            <Button type="submit" loading={upgrading} style={{ flex: 1, justifyContent: 'center' }}>Change Plan</Button>
          </div>
        </form>
      </Modal>

      {/* ── Edit subscription modal ───────────────────────────────────────────── */}
      <Modal open={!!editSub} onClose={() => { setEditSub(null); setEditError(''); setEditSuccess(false) }} title={`Edit Subscription #${editSub?.id ?? ''}`}>
        <form onSubmit={handleEdit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Success banner */}
          {editSuccess && (
            <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#15803d', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Check size={14} /> Subscription updated successfully.
            </div>
          )}
          {/* Error banner */}
          {editError && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#dc2626' }}>
              {editError}
            </div>
          )}
          {/* Status dropdown — all four valid enum values */}
          <Select label="Status" value={editForm.status} onChange={e => setEdit('status', e.target.value)}>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="cancelled">Cancelled</option>
            <option value="past_due">Past Due</option>
          </Select>
          {/* Date inputs — pre-filled from the subscription's current period */}
          <Input
            label="Current Period Start"
            type="date"
            value={editForm.current_period_start}
            onChange={e => setEdit('current_period_start', e.target.value)}
          />
          <Input
            label="Current Period End"
            type="date"
            value={editForm.current_period_end}
            onChange={e => setEdit('current_period_end', e.target.value)}
          />
          {/* Helper note so the user knows how to trigger invoice generation */}
          <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '-8px', lineHeight: '1.5' }}>
            Set Current Period End to yesterday to trigger invoice generation on the next billing cycle run.
          </p>
          <div style={{ display: 'flex', gap: '12px', paddingTop: '4px' }}>
            <Button type="button" variant="secondary" onClick={() => setEditSub(null)} style={{ flex: 1, justifyContent: 'center' }}>Cancel</Button>
            <Button type="submit" loading={editSaving} style={{ flex: 1, justifyContent: 'center' }}>Save Changes</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
