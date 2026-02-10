import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import Sidebar from './Sidebar'
import Header from './Header'
import Overview from './Overview'
import PatientManagement from './PatientManagement'
import DailyEntry from './DailyEntry'
import StaffManagement from './StaffManagement'
import InventoryManagement from './InventoryManagement'
import Analytics from './Analytics'
import Reports from './Reports'

type ActiveTab = 'overview' | 'patients' | 'daily-entry' | 'staff' | 'inventory' | 'analytics' | 'reports'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview')
  const { user, logout } = useAuth()

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <Overview />
      case 'patients':
        return <PatientManagement />
      case 'daily-entry':
        return <DailyEntry />
      case 'staff':
        return <StaffManagement />
      case 'inventory':
        return <InventoryManagement />
      case 'analytics':
        return <Analytics />
      case 'reports':
        return <Reports />
      default:
        return <Overview />
    }
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header user={user} onLogout={logout} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
          {renderContent()}
        </main>
      </div>
    </div>
  )
}
