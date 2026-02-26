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
import LIS from './LIS'
import Payments from './Payments'
import Accounting from './Accounting'
import HR from './HR'
import PatientPortal from './PatientPortal'
import DoctorDashboard from './DoctorDashboard'

type ActiveTab = 'overview' | 'patients' | 'daily-entry' | 'staff' | 'inventory' | 'analytics' | 'reports' | 'lis' | 'payments' | 'accounting' | 'hr' | 'doctor-portal' | 'patient-portal'

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
      case 'lis':
        return <LIS activeTab={activeTab} />
      case 'payments':
        return <Payments activeTab={activeTab} />
      case 'accounting':
        return <Accounting activeTab={activeTab} />
      case 'hr':
        return <HR activeTab={activeTab} />
      case 'doctor-portal':
        return <DoctorDashboard doctorId={1} />
      case 'patient-portal':
        return <PatientPortal activeTab={activeTab} />
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
