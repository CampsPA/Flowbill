import { useEffect, useState } from 'react'
import { CreditCard, ChevronRight } from 'lucide-react'
import api from '../api/client'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import EmptyState from '../components/ui/EmptyState'
import { Select } from '../components/ui/Input'
import { Table, Thead, Th, Tbody, Tr, Td } from '../components/ui/Table'

function fmt(dt) {
  if (!dt) return null
  return new Date(dt).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
function fmtDate(dt) {
  if (!dt) return null
  return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
function cents(v) {
  if (v == null) return '—'
  return '$' + (v / 100).toLocaleString('en-US', { minimumFractionDigits: 2 })
}

export default function Payments() {
  const [customers, setCustomers] = useState([])
  const [customerId, setCustomerId] = useState('')
  const [invoices, setInvoices] = useState([])
  const [invoiceId, setInvoiceId] = useState('')
  const [payments, setPayments] = useState([])
  const [loadingInvoices, setLoadingInvoices] = useState(false)
  const [loadingPayments, setLoadingPayments] = useState(false)

  useEffect(() => { api.get('/customers/').then(r => setCustomers(r.data)).catch(() => {}) }, [])

  useEffect(() => {
    if (!customerId) { setInvoices([]); setInvoiceId(''); setPayments([]); return }
    setLoadingInvoices(true)
    api.get(`/invoices/?customer_id=${customerId}`)
      .then(r => setInvoices(r.data)).catch(() => setInvoices([]))
      .finally(() => setLoadingInvoices(false))
    setInvoiceId(''); setPayments([])
  }, [customerId])

  useEffect(() => {
    if (!invoiceId) { setPayments([]); return }
    setLoadingPayments(true)
    api.get(`/payments/invoice/${invoiceId}`)
      .then(r => setPayments(r.data)).catch(() => setPayments([]))
      .finally(() => setLoadingPayments(false))
  }, [invoiceId])

  const selectedInvoice = invoices.find(inv => String(inv.id) === String(invoiceId))

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#0f172a', letterSpacing: '-0.5px', marginBottom: '6px' }}>Payments</h1>
        <p style={{ fontSize: '14px', color: '#94a3b8' }}>View payment attempt history for any invoice</p>
      </div>

      {/* Step 1 */}
      <Card style={{ padding: '20px 24px' }}>
        <Select label="1. Select Customer" value={customerId} onChange={e => setCustomerId(e.target.value)}>
          <option value="">— Select a customer —</option>
          {customers.map(c => <option key={c.id} value={c.id}>{c.name} ({c.email})</option>)}
        </Select>
      </Card>

      {/* Step 2 */}
      {customerId && (
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '20px 24px', borderBottom: '1px solid #e8ecf2' }}>
            <ChevronRight size={14} color="#94a3b8" />
            <h2 style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>2. Select Invoice</h2>
          </div>
          {loadingInvoices ? (
            <div style={{ padding: '60px', textAlign: 'center', color: '#94a3b8', fontSize: '14px' }}>Loading…</div>
          ) : invoices.length === 0 ? (
            <EmptyState icon={CreditCard} title="No invoices" description="This customer has no invoices yet." />
          ) : (
            <div>
              {invoices.map(inv => (
                <button
                  key={inv.id}
                  onClick={() => setInvoiceId(String(inv.id))}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '18px 24px',
                    borderBottom: '1px solid #f1f5f9',
                    textAlign: 'left',
                    cursor: 'pointer',
                    background: String(invoiceId) === String(inv.id) ? '#f5f3ff' : '#fff',
                    borderLeft: String(invoiceId) === String(inv.id) ? '3px solid #6366f1' : '3px solid transparent',
                    transition: 'background 0.1s',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <CreditCard size={14} color="#94a3b8" />
                    <div>
                      <p style={{ fontSize: '14px', fontWeight: '600', color: '#0f172a' }}>Invoice #{inv.id}</p>
                      <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>Due {fmtDate(inv.due_date)}</p>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ fontSize: '14px', fontWeight: '600', color: '#1e293b' }}>{cents(inv.amount_cents)}</span>
                    <Badge status={inv.status} />
                  </div>
                </button>
              ))}
            </div>
          )}
        </Card>
      )}

      {/* Step 3 */}
      {invoiceId && (
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '20px 24px', borderBottom: '1px solid #e8ecf2' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CreditCard size={14} color="#94a3b8" />
              <h2 style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Payment Attempts — Invoice #{invoiceId}</h2>
            </div>
            {selectedInvoice && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '14px', fontWeight: '600', color: '#1e293b' }}>{cents(selectedInvoice.amount_cents)}</span>
                <Badge status={selectedInvoice.status} />
              </div>
            )}
          </div>
          {loadingPayments ? (
            <div style={{ padding: '80px', textAlign: 'center', color: '#94a3b8', fontSize: '14px' }}>Loading…</div>
          ) : payments.length === 0 ? (
            <EmptyState icon={CreditCard} title="No payment attempts" description="No payment records found for this invoice." />
          ) : (
            <Table>
              <Thead>
                <Tr header>
                  <Th width="7%">ID</Th>
                  <Th width="22%">Attempted At</Th>
                  <Th width="13%">Status</Th>
                  <Th width="33%">Failure Reason</Th>
                  <Th width="25%">Stripe Intent ID</Th>
                </Tr>
              </Thead>
              <Tbody>
                {payments.map(p => (
                  <Tr key={p.id}>
                    <Td mono muted>#{p.id}</Td>
                    <Td muted>{fmt(p.attempted_at)}</Td>
                    <Td><Badge status={p.status} /></Td>
                    <Td muted>{p.failure_reason ?? null}</Td>
                    <Td mono muted truncate>{p.stripe_payment_intent_id ?? null}</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          )}
        </Card>
      )}
    </div>
  )
}
