import { useEffect, useState } from 'react'
// N9: added useSearchParams to pick up ?customer_id from CustomerDetail link
import { useNavigate, useSearchParams } from 'react-router-dom'
import { FileText } from 'lucide-react'
import api from '../api/client'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import EmptyState from '../components/ui/EmptyState'
import { Select } from '../components/ui/Input'
import { Table, Thead, Th, Tbody, Tr, Td } from '../components/ui/Table'

function fmt(dt) {
  if (!dt) return null
  return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
function cents(v) {
  if (v == null) return '—'
  return '$' + (v / 100).toLocaleString('en-US', { minimumFractionDigits: 2 })
}

export default function Invoices() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [customers, setCustomers] = useState([])
  // N9: pre-select customer from URL param so the "View all invoices" link from CustomerDetail works
  const [customerId, setCustomerId] = useState(searchParams.get('customer_id') ?? '')
  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => { api.get('/customers/').then(r => setCustomers(r.data)).catch(() => {}) }, [])

  useEffect(() => {
    if (!customerId) return
    setLoading(true)
    api.get(`/invoices/?customer_id=${customerId}`)
      .then(r => setInvoices(r.data))
      .catch(() => setInvoices([]))
      .finally(() => setLoading(false))
  }, [customerId])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#0f172a', letterSpacing: '-0.5px', marginBottom: '6px' }}>Invoices</h1>
        <p style={{ fontSize: '14px', color: '#94a3b8' }}>View and manage customer invoices</p>
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
          <EmptyState icon={FileText} title="Select a customer" description="Choose a customer above to view their invoices." />
        ) : loading ? (
          <div style={{ padding: '80px', textAlign: 'center', color: '#94a3b8', fontSize: '14px' }}>Loading…</div>
        ) : invoices.length === 0 ? (
          <EmptyState icon={FileText} title="No invoices" description="No invoices found for this customer." />
        ) : (
          <Table>
            <Thead>
              <Tr header>
                <Th width="10%">Invoice</Th>
                <Th width="18%">Subscription</Th>
                <Th width="17%">Amount</Th>
                <Th width="15%">Status</Th>
                <Th width="20%">Due Date</Th>
                <Th width="20%">Paid At</Th>
              </Tr>
            </Thead>
            <Tbody>
              {invoices.map(inv => (
                <Tr key={inv.id} onClick={() => navigate(`/app/invoices/${inv.id}`)}>
                  <Td mono muted>#{inv.id}</Td>
                  <Td mono muted>Sub #{inv.subscription_id}</Td>
                  <Td><span style={{ fontWeight: '600', color: '#0f172a' }}>{cents(inv.amount_cents)}</span></Td>
                  <Td><Badge status={inv.status} /></Td>
                  <Td muted>{fmt(inv.due_date)}</Td>
                  <Td muted>{fmt(inv.paid_at)}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        )}
      </Card>
    </div>
  )
}
