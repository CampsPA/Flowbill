import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Users, Search, Plus } from 'lucide-react'
import api from '../api/client'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import EmptyState from '../components/ui/EmptyState'
import Modal from '../components/ui/Modal'
import Input from '../components/ui/Input'
import { Table, Thead, Th, Tbody, Tr, Td } from '../components/ui/Table'

function fmt(dt) {
  if (!dt) return null
  return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export default function Customers() {
  const navigate = useNavigate()
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [modal, setModal] = useState(false)
  // C3: removed phone field — backend Customer model has no phone column
  const [form, setForm] = useState({ name: '', email: '' })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  function load() {
    api.get('/customers/').then(r => setCustomers(r.data)).catch(() => {}).finally(() => setLoading(false))
  }
  useEffect(load, [])

  const filtered = customers.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.email.toLowerCase().includes(search.toLowerCase())
  )

  async function handleCreate(e) {
    e.preventDefault(); setSaving(true); setError('')
    try {
      await api.post('/customers/', form)
      // C3: reset without phone field
      setModal(false); setForm({ name: '', email: '' }); load()
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Error creating customer')
    } finally { setSaving(false) }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#0f172a', letterSpacing: '-0.5px', marginBottom: '6px' }}>Customers</h1>
          <p style={{ fontSize: '14px', color: '#94a3b8' }}>{customers.length} total customers</p>
        </div>
        <Button onClick={() => setModal(true)}><Plus size={15} /> New Customer</Button>
      </div>

      {/* Search */}
      <div style={{ position: 'relative' }}>
        <Search size={16} style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8', pointerEvents: 'none' }} />
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search by name or email…"
          style={{ width: '100%', height: '48px', padding: '0 16px 0 44px', border: '1px solid #d1d5db', borderRadius: '10px', fontSize: '14px', color: '#1e293b', background: '#fff', outline: 'none', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', boxSizing: 'border-box' }}
        />
      </div>

      {/* Table */}
      <Card>
        {loading ? (
          <div style={{ padding: '80px', textAlign: 'center', color: '#94a3b8', fontSize: '14px' }}>Loading…</div>
        ) : filtered.length === 0 ? (
          <EmptyState icon={Users} title="No customers found" description={search ? 'Try a different search term.' : 'Add your first customer to get started.'} />
        ) : (
          <Table>
            <Thead>
              <Tr header>
                <Th width="38%">Customer</Th>
                <Th width="24%">Stripe ID</Th>
                <Th width="14%">Status</Th>
                <Th width="24%">Created</Th>
              </Tr>
            </Thead>
            <Tbody>
              {filtered.map(c => (
                <Tr key={c.id} onClick={() => navigate(`/app/customers/${c.id}`)}>
                  <Td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                      <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: '700', fontSize: '13px', flexShrink: 0 }}>
                        {c.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p style={{ fontWeight: '600', color: '#0f172a', fontSize: '14px' }}>{c.name}</p>
                        <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>{c.email}</p>
                      </div>
                    </div>
                  </Td>
                  {/* N6: title attribute provides a native browser tooltip showing the full Stripe ID on hover */}
                  <Td mono truncate>
                    <span title={c.stripe_customer_id || 'No Stripe ID'} style={{ cursor: c.stripe_customer_id ? 'help' : 'default' }}>
                      {c.stripe_customer_id || null}
                    </span>
                  </Td>
                  <Td><Badge status={c.is_active ? 'active' : 'cancelled'} label={c.is_active ? 'Active' : 'Inactive'} /></Td>
                  <Td muted>{fmt(c.created_at)}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        )}
      </Card>

      {/* Create modal */}
      <Modal open={modal} onClose={() => { setModal(false); setError('') }} title="New Customer">
        <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {error && <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#dc2626' }}>{error}</div>}
          <Input label="Full Name" placeholder="Acme Corp" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} required />
          <Input label="Email Address" type="email" placeholder="billing@acme.com" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} required />
          {/* C3: phone field removed — not in the Customer data model */}
          <div style={{ display: 'flex', gap: '12px', paddingTop: '4px' }}>
            <Button type="button" variant="secondary" onClick={() => setModal(false)} style={{ flex: 1, justifyContent: 'center' }}>Cancel</Button>
            <Button type="submit" loading={saving} style={{ flex: 1, justifyContent: 'center' }}>Create Customer</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
