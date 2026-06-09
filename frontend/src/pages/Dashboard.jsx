import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Users, RefreshCw, FileText, DollarSign, ArrowRight, Zap } from 'lucide-react'
import api from '../api/client'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'

function cents(v) {
  if (v == null) return '—'
  return '$' + (v / 100).toLocaleString('en-US', { minimumFractionDigits: 2 })
}

function StatCard({ icon: Icon, label, value, sub, color }) {
  return (
    <Card style={{ padding: '24px', minHeight: '150px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <p style={{ fontSize: '13px', fontWeight: '600', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</p>
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${color}`} style={{ flexShrink: 0 }}>
          <Icon size={18} className="text-white" />
        </div>
      </div>
      <div>
        <p style={{ fontSize: '36px', fontWeight: '700', color: '#0f172a', lineHeight: 1, marginBottom: '6px' }} className="tabular-nums">{value}</p>
        {sub && <p style={{ fontSize: '12px', color: '#94a3b8' }}>{sub}</p>}
      </div>
    </Card>
  )
}

export default function Dashboard() {
  const [customers, setCustomers] = useState([])
  const [plans, setPlans] = useState([])
  const [activeSubs, setActiveSubs] = useState(0)
  const [mrr, setMrr] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [{ data: cList }, { data: pList }] = await Promise.all([
          api.get('/customers/').catch(() => ({ data: [] })),
          api.get('/plans/').catch(() => ({ data: [] })),
        ])
        setCustomers(cList)
        setPlans(pList)

        // Build plan price map
        const planMap = {}
        pList.forEach(p => { planMap[p.id] = p.price_cents })

        // Fetch subscriptions for all active customers in parallel
        const activeCustomers = cList.filter(c => c.is_active)
        const subResults = await Promise.all(
          activeCustomers.map(c =>
            api.get(`/subscriptions/?customer_id=${c.id}`).then(r => r.data).catch(() => [])
          )
        )
        const allSubs = subResults.flat()
        const active = allSubs.filter(s => s.status === 'active')
        setActiveSubs(active.length)

        // Compute MRR — sum plan prices for active subs (annual / 12)
        let mrrCents = 0
        active.forEach(s => {
          const price = planMap[s.plan_id] ?? 0
          const plan = pList.find(p => p.id === s.plan_id)
          mrrCents += plan?.interval === 'annual' ? Math.round(price / 12) : price
        })
        setMrr(mrrCents)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const activeCustomers = customers.filter(c => c.is_active)
  const activePlans = plans.filter(p => p.is_active).length

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '48px' }}>
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-slate-500 text-sm mt-0.5">Your billing overview.</p>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '24px' }}>
        <StatCard
          icon={Users}
          label="Active Customers"
          value={loading ? '…' : activeCustomers.length}
          color="bg-indigo-600"
        />
        <StatCard
          icon={RefreshCw}
          label="Active Subscriptions"
          value={loading ? '…' : activeSubs}
          color="bg-violet-600"
        />
        <StatCard
          icon={DollarSign}
          label="MRR"
          value={loading ? '…' : mrr != null ? cents(mrr) : '—'}
          sub={activeSubs > 0 ? `across ${activeSubs} active sub${activeSubs !== 1 ? 's' : ''}` : undefined}
          color="bg-emerald-600"
        />
        <StatCard
          icon={Zap}
          label="Billing Plans"
          value={loading ? '…' : activePlans}
          sub="active"
          color="bg-amber-500"
        />
      </div>

      {/* Recent panels */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '32px' }}>
        {/* Recent customers */}
        <Card>
          <div className="flex items-center justify-between border-b border-[#e3e8ef]" style={{ padding: '20px 24px' }}>
            <div className="flex items-center gap-2">
              <Users size={14} className="text-slate-400" />
              <h2 className="text-sm font-semibold text-slate-700">Customers</h2>
            </div>
            <Link to="/app/customers" className="text-xs text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1 transition-colors">
              View all <ArrowRight size={11} />
            </Link>
          </div>
          {loading ? (
            <div className="px-5 py-8 text-center text-sm text-slate-400">Loading…</div>
          ) : customers.length === 0 ? (
            <div className="px-5 py-10 text-center text-sm text-slate-400">No customers yet.</div>
          ) : (
            <div className="divide-y divide-[#f0f2f7]">
              {customers.slice(0, 6).map(c => (
                <Link
                  key={c.id}
                  to={`/app/customers/${c.id}`}
                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 24px', textDecoration: 'none' }}
                  className="hover:bg-slate-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 text-xs font-bold flex-shrink-0">
                      {c.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-800">{c.name}</p>
                      <p className="text-xs text-slate-400">{c.email}</p>
                    </div>
                  </div>
                  <Badge status={c.is_active ? 'active' : 'cancelled'} label={c.is_active ? 'Active' : 'Inactive'} />
                </Link>
              ))}
            </div>
          )}
        </Card>

        {/* Plans */}
        <Card>
          <div className="flex items-center justify-between border-b border-[#e3e8ef]" style={{ padding: '20px 24px' }}>
            <div className="flex items-center gap-2">
              <FileText size={14} className="text-slate-400" />
              <h2 className="text-sm font-semibold text-slate-700">Billing Plans</h2>
            </div>
            <Link to="/app/plans" className="text-xs text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1 transition-colors">
              View all <ArrowRight size={11} />
            </Link>
          </div>
          {loading ? (
            <div className="px-5 py-8 text-center text-sm text-slate-400">Loading…</div>
          ) : plans.length === 0 ? (
            <div className="px-5 py-10 text-center text-sm text-slate-400">No plans yet.</div>
          ) : (
            <div className="divide-y divide-[#f0f2f7]">
              {plans.slice(0, 6).map(p => (
                <div key={p.id} className="flex items-center justify-between" style={{ padding: '16px 24px' }}>
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-lg bg-violet-100 flex items-center justify-center">
                      <RefreshCw size={13} className="text-violet-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-800">{p.name}</p>
                      <p className="text-xs text-slate-400">{cents(p.price_cents)} / {p.interval}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge status={p.interval} />
                    <Badge status={p.is_active ? 'active' : 'cancelled'} label={p.is_active ? 'Active' : 'Off'} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Quick links */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
        {[
          { to: '/app/subscriptions', label: 'Subscriptions', icon: RefreshCw, color: 'text-indigo-600 bg-indigo-50' },
          { to: '/app/invoices',      label: 'Invoices',      icon: FileText,   color: 'text-violet-600 bg-violet-50' },
          { to: '/app/payments',      label: 'Payments',      icon: DollarSign, color: 'text-emerald-600 bg-emerald-50' },
          { to: '/app/webhooks',      label: 'Webhooks',      icon: Zap,        color: 'text-amber-600 bg-amber-50' },
        ].map(({ to, label, icon: Icon, color }) => (
          <Link
            key={to}
            to={to}
            className="flex items-center gap-3 bg-white border border-[#e3e8ef] rounded-xl px-5 py-4 hover:border-indigo-200 hover:shadow-sm transition-all shadow-sm group"
          >
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${color} flex-shrink-0`}>
              <Icon size={15} />
            </div>
            <span className="text-sm font-medium text-slate-600 group-hover:text-slate-900 transition-colors">{label}</span>
            <ArrowRight size={13} className="ml-auto text-slate-300 group-hover:text-slate-400 transition-colors" />
          </Link>
        ))}
      </div>
    </div>
  )
}
