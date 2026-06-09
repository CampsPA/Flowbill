import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Plus, RefreshCw, PauseCircle, XCircle, ArrowUpCircle, PlayCircle } from 'lucide-react'
import api from '../api/client'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Modal from '../components/ui/Modal'
import { Select } from '../components/ui/Input'
import EmptyState from '../components/ui/EmptyState'
import { Table, Thead, Th, Tbody, Tr, Td } from '../components/ui/Table'

function fmt(dt) {
  if (!dt) return null
  return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
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

  const [createModal, setCreateModal] = useState(false)
  const [createForm, setCreateForm] = useState({ customer_id: defaultCustomerId, plan_id: '' })
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState('')

  const [upgradeModal, setUpgradeModal] = useState(null)
  const [upgradePlanId, setUpgradePlanId] = useState('')
  const [upgrading, setUpgrading] = useState(false)
  const [upgradeError, setUpgradeError] = useState('')
  // I4: track which subscription id is currently being acted on so action buttons show a spinner
  const [actionLoading, setActionLoading] = useState(null)  // stores sub.id while any action is in-flight

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

  async function handlePause(sub) {
    // I4: set loading on this specific sub so the Pause button shows a spinner
    setActionLoading(sub.id)
    // I10: removed paused_at from the request body — server now sets it automatically
    await api.patch(`/subscriptions/${sub.id}`, { status: 'paused' })
    loadSubs(customerId)
    setActionLoading(null)  // I4: clear loading state when done
  }
  async function handleResume(sub) {
    setActionLoading(sub.id)  // I4: spinner on Resume button
    await api.patch(`/subscriptions/${sub.id}`, { status: 'active' }); loadSubs(customerId)
    setActionLoading(null)  // I4: clear after resuming
  }
  async function handleCancel(sub) {
    if (!confirm('Cancel this subscription? This cannot be undone.')) return
    setActionLoading(sub.id)  // I4: spinner on Cancel button
    await api.delete(`/subscriptions/${sub.id}`); loadSubs(customerId)
    setActionLoading(null)  // I4: clear after cancellation
  }
  async function handleUpgrade(e) {
    e.preventDefault(); setUpgrading(true); setUpgradeError('')
    try {
      await api.patch(`/subscriptions/${upgradeModal.id}`, { plan_id: parseInt(upgradePlanId) })
      setUpgradeModal(null); loadSubs(customerId)
    } catch (err) {
      setUpgradeError(err.response?.data?.detail ?? 'Error changing plan')
    } finally { setUpgrading(false) }
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

      {/* Filter */}
      <Card style={{ padding: '20px 24px' }}>
        <Select label="Filter by Customer" value={customerId} onChange={e => setCustomerId(e.target.value)}>
          <option value="">— Select a customer —</option>
          {customers.map(c => <option key={c.id} value={c.id}>{c.name} ({c.email})</option>)}
        </Select>
      </Card>

      {/* Table */}
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
                <Th width="7%">ID</Th>
                <Th width="28%">Plan</Th>
                <Th width="12%">Status</Th>
                <Th width="16%">Period Start</Th>
                <Th width="16%">Period End</Th>
                <Th width="21%">Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {subs.map(s => {
                const plan = plans.find(p => p.id === s.plan_id)
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
                      {/* I4: isActing disables all buttons for this row while any action is in-flight */}
                      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                        {s.status === 'active' && (
                          // I4: loading prop shows spinner; disabled prevents double-clicks
                          <Button variant="ghost" size="sm" loading={actionLoading === s.id} disabled={actionLoading === s.id} onClick={() => handlePause(s)}>
                            <PauseCircle size={12} /> Pause
                          </Button>
                        )}
                        {s.status === 'paused' && (
                          // I4: same loading pattern for Resume
                          <Button variant="ghost" size="sm" loading={actionLoading === s.id} disabled={actionLoading === s.id} onClick={() => handleResume(s)}>
                            <PlayCircle size={12} /> Resume
                          </Button>
                        )}
                        {s.status !== 'cancelled' && (
                          <Button variant="ghost" size="sm" disabled={actionLoading === s.id} onClick={() => { setUpgradePlanId(''); setUpgradeError(''); setUpgradeModal(s) }}>
                            <ArrowUpCircle size={12} /> Change
                          </Button>
                        )}
                        {s.status !== 'cancelled' && (
                          // I4: Cancel button also shows loading/disabled state
                          <Button variant="danger" size="sm" loading={actionLoading === s.id} disabled={actionLoading === s.id} onClick={() => handleCancel(s)}>
                            <XCircle size={12} /> Cancel
                          </Button>
                        )}
                      </div>
                    </Td>
                  </Tr>
                )
              })}
            </Tbody>
          </Table>
        )}
      </Card>

      {/* Create modal */}
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

      {/* Change plan modal */}
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
    </div>
  )
}
