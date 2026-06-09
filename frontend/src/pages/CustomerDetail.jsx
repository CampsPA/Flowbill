import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
// Customers Delete: added Trash2 icon
import { ArrowLeft, Edit2, UserX, RefreshCw, FileText, Trash2 } from 'lucide-react'
import api from '../api/client'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Modal from '../components/ui/Modal'
import Input from '../components/ui/Input'

function fmt(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
function cents(v) {
  if (v == null) return '—'
  return '$' + (v / 100).toLocaleString('en-US', { minimumFractionDigits: 2 })
}

export default function CustomerDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [customer, setCustomer] = useState(null)
  const [subs, setSubs] = useState([])
  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(true)
  const [editModal, setEditModal] = useState(false)
  const [form, setForm] = useState({})
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  function load() {
    Promise.all([
      api.get(`/customers/${id}`),
      api.get(`/subscriptions/?customer_id=${id}`).catch(() => ({ data: [] })),
      api.get(`/invoices/?customer_id=${id}`).catch(() => ({ data: [] })),
    ]).then(([c, s, inv]) => {
      setCustomer(c.data)
      setForm({ name: c.data.name, email: c.data.email })
      setSubs(s.data)
      setInvoices(inv.data)
    }).catch(() => navigate('/app/customers'))
    .finally(() => setLoading(false))
  }
  useEffect(load, [id])

  async function handleSave(e) {
    e.preventDefault(); setSaving(true); setError('')
    try {
      const { data } = await api.patch(`/customers/${id}`, form)
      setCustomer(data); setEditModal(false)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Error updating')
    } finally { setSaving(false) }
  }

  async function handleDeactivate() {
    if (!confirm('Deactivate this customer?')) return
    try {
      // I9: wrapped in try/catch to surface errors instead of silently failing
      await api.delete(`/customers/${id}`)
      navigate('/app/customers')
    } catch (err) {
      // I9: show the server's error message (e.g. "not found") in an alert
      alert(err.response?.data?.detail ?? 'Failed to deactivate customer. Please try again.')
    }
  }

  // Customers Delete: permanently deletes the customer and cancels all their active subscriptions
  async function handleHardDelete() {
    if (!confirm(`Permanently delete ${customer?.name}? This will cancel all their subscriptions and cannot be undone.`)) return
    try {
      // Customers Delete: calls DELETE /customers/{id}/hard on the backend
      await api.delete(`/customers/${id}/hard`)
      navigate('/app/customers')  // Customers Delete: redirect back to list after deletion
    } catch (err) {
      // Customers Delete: show backend error to the user
      alert(err.response?.data?.detail ?? 'Failed to delete customer. Please try again.')
    }
  }

  if (loading) return <div className="p-8 text-slate-400 text-sm">Loading…</div>
  if (!customer) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate('/app/customers')} className="text-slate-400 hover:text-slate-600 transition-colors cursor-pointer p-1.5 rounded-lg hover:bg-white border border-transparent hover:border-[#e3e8ef]">
          <ArrowLeft size={16} />
        </button>
        <div className="flex items-center gap-3 flex-1">
          <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-base">
            {customer.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">{customer.name}</h1>
            <p className="text-sm text-slate-400">{customer.email}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => setEditModal(true)}><Edit2 size={13} /> Edit</Button>
          <Button variant="danger" size="sm" onClick={handleDeactivate}><UserX size={13} /> Deactivate</Button>
          {/* Customers Delete: hard-delete button — cancels subs and removes the DB record */}
          <Button variant="danger" size="sm" onClick={handleHardDelete}><Trash2 size={13} /> Delete</Button>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          ['Status', <Badge status={customer.is_active ? 'active' : 'cancelled'} label={customer.is_active ? 'Active' : 'Inactive'} />],
          ['Customer ID', <span className="text-sm font-mono text-slate-600">#{customer.id}</span>],
          ['Stripe ID', <span className="text-xs font-mono text-slate-500 break-all">{customer.stripe_customer_id ?? '—'}</span>],
          ['Member Since', <span className="text-sm text-slate-600">{fmt(customer.created_at)}</span>],
        ].map(([label, val]) => (
          <Card key={label} className="p-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">{label}</p>
            {val}
          </Card>
        ))}
      </div>

      {/* Subscriptions */}
      <Card>
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#e3e8ef]">
          <div className="flex items-center gap-2">
            <RefreshCw size={14} className="text-slate-400" />
            <h2 className="text-sm font-semibold text-slate-700">Subscriptions</h2>
          </div>
          <Link to={`/app/subscriptions?customer_id=${id}`} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium transition-colors">View all</Link>
        </div>
        {subs.length === 0 ? (
          <div className="px-5 py-5 text-sm text-slate-400">No subscriptions.</div>
        ) : (
          <div className="divide-y divide-[#f0f2f7]">
            {subs.map(s => (
              <div key={s.id} className="px-5 py-3 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-700">Plan #{s.plan_id}</p>
                  <p className="text-xs text-slate-400">{fmt(s.current_period_start)} → {fmt(s.current_period_end)}</p>
                </div>
                <Badge status={s.status} />
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Invoices */}
      <Card>
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#e3e8ef]">
          <div className="flex items-center gap-2">
            <FileText size={14} className="text-slate-400" />
            <h2 className="text-sm font-semibold text-slate-700">Recent Invoices</h2>
          </div>
          {/* N9: "View all invoices" link navigates to the Invoices page pre-filtered by this customer */}
          <Link to={`/app/invoices?customer_id=${id}`} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium transition-colors">View all</Link>
        </div>
        {invoices.length === 0 ? (
          <div className="px-5 py-5 text-sm text-slate-400">No invoices.</div>
        ) : (
          <div className="divide-y divide-[#f0f2f7]">
            {invoices.slice(0, 5).map(inv => (
              <Link key={inv.id} to={`/app/invoices/${inv.id}`} className="px-5 py-3 flex items-center justify-between hover:bg-slate-50 transition-colors">
                <div>
                  <p className="text-sm font-medium text-slate-700">Invoice #{inv.id}</p>
                  <p className="text-xs text-slate-400">Due {fmt(inv.due_date)}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-semibold text-slate-700">{cents(inv.amount_cents)}</span>
                  <Badge status={inv.status} />
                </div>
              </Link>
            ))}
          </div>
        )}
      </Card>

      <Modal open={editModal} onClose={() => setEditModal(false)} title="Edit Customer">
        <form onSubmit={handleSave} className="space-y-4">
          {error && <div className="bg-red-50 border border-red-200 rounded-lg px-3 py-2.5 text-sm text-red-600">{error}</div>}
          <Input label="Name" value={form.name ?? ''} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
          <Input label="Email" type="email" value={form.email ?? ''} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
          <div className="flex gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => setEditModal(false)} className="flex-1 justify-center">Cancel</Button>
            <Button type="submit" loading={saving} className="flex-1 justify-center">Save Changes</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
