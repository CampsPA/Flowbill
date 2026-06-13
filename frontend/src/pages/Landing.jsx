import { Link } from 'react-router-dom'
import { Zap, RefreshCw, Bell, FileText } from 'lucide-react'
import heroBg from '../akif-waseem-MmPxGnlmVGA-unsplash.jpg'
import subscriptionsImg from '../subscriptions.jpg'
import dunningImg from '../dunning.jpg'
import invoicingImg from '../invoicing.jpg'

const features = [
  {
    icon: RefreshCw,
    title: 'Subscriptions',
    description: 'Automated billing cycles, upgrades, and cancellations.',
    color: 'text-indigo-600',
    image: subscriptionsImg,
  },
  {
    icon: Bell,
    title: 'Dunning',
    description: 'Smart retry logic that recovers failed payments automatically.',
    color: 'text-violet-600',
    image: dunningImg,
  },
  {
    icon: FileText,
    title: 'Invoicing',
    description: 'Professional PDF invoices generated and delivered instantly.',
    color: 'text-slate-600',
    image: invoicingImg,
  },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-white">

      {/* Nav */}
      <nav className="sticky top-0 bg-white z-50">
        <div className="max-w-5xl mx-auto px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-indigo-600 flex items-center justify-center">
              <Zap size={13} className="text-white" />
            </div>
            <span className="font-semibold text-slate-900 text-sm tracking-tight">FlowBill</span>
          </Link>
          <div className="flex items-center gap-8">
            <Link to="/login" className="text-sm text-slate-500 hover:text-slate-900 transition-colors">Sign in</Link>
            <Link
              to="/register"
              className="text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
            >
              Get started →
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section style={{
        position: 'relative',
        height: '100vh',
        backgroundImage: `url(${heroBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>

        {/* Content */}
        <div style={{ position: 'relative', zIndex: 1, textAlign: 'center', padding: '0 32px', maxWidth: '860px' }}>
          <h1 style={{ fontSize: '72px', lineHeight: '1.05', letterSpacing: '-2px', fontWeight: '700', color: '#000', marginBottom: '24px' }}>
            Billing infrastructure<br />for modern teams.
          </h1>
          <p style={{ fontSize: '20px', color: '#000', marginBottom: '40px', opacity: 0.75 }}>
            Subscriptions, invoicing, and dunning — fully automated.
          </p>
          <Link
            to="/register"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              background: '#4f46e5',
              color: '#fff',
              fontWeight: '500',
              padding: '14px 32px',
              borderRadius: '12px',
              fontSize: '14px',
              textDecoration: 'none',
            }}
          >
            Start for free
          </Link>
        </div>
      </section>

      {/* Features */}
      <section id="features" style={{ paddingTop: '120px', paddingBottom: '120px', borderTop: '1px solid #f0f0f0' }}>
        <div style={{ width: '100%', padding: '0 48px', boxSizing: 'border-box' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px', width: '100%' }}>
            {features.map(({ icon: Icon, title, description, color, image }) => (
              <div key={title} style={{ borderRadius: '16px', overflow: 'hidden', border: '1px solid #f0f0f0', display: 'flex', flexDirection: 'column' }}>
                <img src={image} alt={title} style={{ width: '100%', height: '200px', objectFit: 'cover', display: 'block' }} />
                <div style={{ padding: '28px' }}>
                  <Icon size={26} className={`${color} mb-4`} strokeWidth={1.5} />
                  <h3 style={{ fontWeight: '700', color: '#0f172a', fontSize: '20px', marginBottom: '10px' }}>{title}</h3>
                  <p style={{ fontSize: '15px', color: '#64748b', lineHeight: '1.7' }}>{description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ paddingTop: '40px', paddingBottom: '40px' }} className="border-t border-[#f0f0f0] px-8">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <span className="text-xs text-slate-400">© 2025 FlowBill</span>
          <Link to="/login" className="text-xs text-slate-400 hover:text-slate-600 transition-colors">Sign in</Link>
        </div>
      </footer>

    </div>
  )
}
