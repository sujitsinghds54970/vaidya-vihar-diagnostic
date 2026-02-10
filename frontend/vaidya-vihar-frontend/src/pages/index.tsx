


import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import Login from '../components/auth/Login'
import Registration from '../components/auth/Registration'
import Dashboard from '../components/dashboard/Dashboard'

export default function Home() {
  const { user, loading } = useAuth()
  const [showRegistration, setShowRegistration] = useState(false)

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!user) {
    return showRegistration ? (
      <Registration onSwitchToLogin={() => setShowRegistration(false)} />
    ) : (
      <Login onSwitchToRegistration={() => setShowRegistration(true)} />
    )
  }

  return <Dashboard />
}
