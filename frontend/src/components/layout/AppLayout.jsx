import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-[#f6f9fc]">
      <Sidebar />
      <main className="min-h-screen" style={{ paddingLeft: '3.5rem' }}>
        <div className="max-w-6xl mx-auto" style={{ padding: '48px 48px' }}>
          <Outlet />
        </div>
      </main>
    </div>
  )
}
