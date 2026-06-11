import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Download, CreditCard, Package, CheckCircle } from 'lucide-react'
import api from '../api/client'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import { Table, Thead, Th, Tbody, Tr, Td } from '../components/ui/Table'

function fmt(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
function cents(v) {
  if (v == null) return '—'
  return '$' + (v / 100).toLocaleString('en-US', { minimumFractionDigits: 2 })
}

export default function InvoiceDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [invoice, setInvoice] = useState(null)
  const [logoUrl, setLogoUrl] = useState(null)
  const [payments, setPayments] = useState([])
  const [lineItems, setLineItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)
  // Mark as Paid state — tracks the in-flight request and inline feedback
  const [markingPaid, setMarkingPaid] = useState(false)
  const [paidResult, setPaidResult] = useState(null)   // null | 'success' | 'error'
  const [paidError, setPaidError] = useState('')

  useEffect(() => {
    Promise.all([
      api.get(`/invoices/${id}`),
      api.get(`/payments/invoice/${id}`).catch(() => ({ data: [] })),
      api.get(`/line-items/invoice/${id}`).catch(() => ({ data: [] })),
    ]).then(([inv, pay, items]) => {
      setInvoice(inv.data)
      setPayments(pay.data)
      setLineItems(items.data)
      // Fetch tenant settings using the customer_id from the invoice to get their logo
      api.get(`/tenant-settings/${inv.data.customer_id}`)
        .then(s => setLogoUrl(s.data.logo_url ?? null))
        .catch(() => {})  // no settings = no logo, keep null fallback
    }).catch(() => navigate('/app/invoices'))
    .finally(() => setLoading(false))
  }, [id])

  async function handleMarkPaid() {
    if (!confirm('Mark this invoice as paid? This will record the payment manually.')) return
    setMarkingPaid(true)
    setPaidResult(null)
    setPaidError('')
    try {
      // Send status + paid_at timestamp; backend PATCH /invoices/{id} accepts both fields
      const updated = await api.patch(`/invoices/${id}`, {
        status: 'paid',
        paid_at: new Date().toISOString(),  // current UTC timestamp in ISO 8601 format
      })
      // Update local invoice state so the Status and Paid At cards reflect the change immediately
      setInvoice(updated.data)
      setPaidResult('success')
    } catch (err) {
      setPaidError(err.response?.data?.detail ?? 'Failed to mark invoice as paid.')
      setPaidResult('error')
    } finally {
      setMarkingPaid(false)
    }
  }

  async function handleDownload() {
    if (!invoice) return
    setDownloading(true)
    try {
      const res = await api.get(`/invoices/${id}/pdf?customer_id=${invoice.customer_id}`, { responseType: 'blob' })
      const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
      const a = document.createElement('a'); a.href = url; a.download = `invoice_${id}.pdf`; a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      // C5: surface PDF download errors to the user instead of swallowing them silently
      alert(err.response?.data?.detail ?? 'Failed to download PDF. Please try again.')
    } finally { setDownloading(false) }
  }

  if (loading) return <div className="p-8 text-slate-400 text-sm">Loading…</div>
  if (!invoice) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate('/app/invoices')} className="text-slate-400 hover:text-slate-600 transition-colors cursor-pointer p-1.5 rounded-lg hover:bg-white border border-transparent hover:border-[#e3e8ef]">
          <ArrowLeft size={16} />
        </button>
        <div className="flex items-center gap-3 flex-1">
          {logoUrl && (
            <img src={logoUrl} alt="Customer logo" style={{ maxHeight: '40px', maxWidth: '100px', objectFit: 'contain', borderRadius: '6px', border: '1px solid #e8ecf2', background: '#fff', padding: '3px', flexShrink: 0 }} />
          )}
          <div>
            <h1 className="text-xl font-bold text-slate-900">Invoice #{invoice.id}</h1>
            <p className="text-sm text-slate-400">Customer #{invoice.customer_id} · Subscription #{invoice.subscription_id}</p>
          </div>
        </div>
        {/* Only show Mark as Paid when the invoice is not already paid */}
        {invoice.status !== 'paid' && (
          <Button onClick={handleMarkPaid} loading={markingPaid} variant="secondary">
            <CheckCircle size={14} /> Mark as Paid
          </Button>
        )}
        <Button onClick={handleDownload} loading={downloading} variant="secondary">
          <Download size={14} /> Download PDF
        </Button>
      </div>
      {/* Inline success/error feedback — shown directly under the header, above the stat cards */}
      {paidResult === 'success' && (
        <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#15803d', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle size={14} /> Invoice marked as paid successfully.
        </div>
      )}
      {paidResult === 'error' && (
        <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '12px 16px', fontSize: '14px', color: '#dc2626' }}>
          {paidError}
        </div>
      )}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          ['Amount Due', <span className="text-xl font-bold text-slate-800">{cents(invoice.amount_cents)}</span>],
          ['Status', <Badge status={invoice.status} />],
          ['Due Date', <span className="text-sm text-slate-600">{fmt(invoice.due_date)}</span>],
          ['Paid At', <span className="text-sm text-slate-600">{fmt(invoice.paid_at)}</span>],
        ].map(([label, val]) => (
          <Card key={label} className="p-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">{label}</p>
            {val}
          </Card>
        ))}
      </div>

      {/* I2: line items card — shows the description/quantity/price breakdown for the invoice */}
      <Card>
        <div className="flex items-center gap-2 px-5 py-4 border-b border-[#e3e8ef]">
          <Package size={14} className="text-slate-400" />
          <h2 className="text-sm font-semibold text-slate-700">Line Items</h2>
        </div>
        {lineItems.length === 0 ? (
          // I2: empty state when no line items exist for this invoice
          <div className="px-5 py-5 text-sm text-slate-400">No line items recorded.</div>
        ) : (
          <Table>
            <Thead>
              <Tr header>
                {/* I2: columns match the LineItem schema fields */}
                <Th width="50%">Description</Th>
                <Th width="15%">Qty</Th>
                <Th width="20%">Amount</Th>
                <Th width="15%">Total</Th>
              </Tr>
            </Thead>
            <Tbody>
              {lineItems.map(item => (
                // I2: render each line item row; fields from LineItemResponse schema
                <Tr key={item.id}>
                  <Td>{item.description}</Td>
                  <Td mono muted>{item.quantity}</Td>
                  {/* I2: amount_cents is the per-unit price from LineItemResponse */}
                  <Td><span style={{ fontWeight: '600', color: '#0f172a' }}>{cents(item.amount_cents)}</span></Td>
                  {/* I2: total = unit price × quantity, computed client-side */}
                  <Td><span style={{ fontWeight: '600', color: '#0f172a' }}>{cents(item.amount_cents * item.quantity)}</span></Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        )}
      </Card>

      <Card>
        <div className="flex items-center gap-2 px-5 py-4 border-b border-[#e3e8ef]">
          <CreditCard size={14} className="text-slate-400" />
          <h2 className="text-sm font-semibold text-slate-700">Payment Attempts</h2>
        </div>
        {payments.length === 0 ? (
          <div className="px-5 py-5 text-sm text-slate-400">No payment attempts recorded.</div>
        ) : (
          <Table>
            <Thead>
              <Tr header>
                <Th width="7%">ID</Th>
                <Th width="20%">Attempted At</Th>
                <Th width="13%">Status</Th>
                <Th width="35%">Failure Reason</Th>
                <Th width="25%">Stripe Intent</Th>
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
    </div>
  )
}
