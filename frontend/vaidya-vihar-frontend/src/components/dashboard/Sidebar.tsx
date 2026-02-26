import React, { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'

interface SidebarProps {
  activeTab: string
  setActiveTab: (tab: any) => void
}

export default function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  const { user } = useAuth()

  const menuItems = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'patients', label: 'Patients', icon: '👥' },
    { id: 'daily-entry', label: 'Daily Entry', icon: '📝' },
    { id: 'staff', label: 'Staff', icon: '👨‍⚕️' },
    { id: 'inventory', label: 'Inventory', icon: '📦' },
    { id: 'analytics', label: 'Analytics', icon: '📈' },
    { id: 'reports', label: 'Reports', icon: '📋' },
    // New Features
    { id: 'lis', label: 'LIS Lab Tests', icon: '🧪' },
    { id: 'payments', label: 'Payments', icon: '💳' },
    { id: 'accounting', label: 'Accounting', icon: '💰' },
    { id: 'hr', label: 'HR & Leave', icon: '👔' },
    { id: 'doctor-portal', label: 'Doctor Portal', icon: '🩺' },
    { id: 'patient-portal', label: 'Patient Portal', icon: '🏥' },
  ]

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId)
  }

  return (
    <div className="bg-white w-64 min-h-screen shadow-lg border-r border-gray-200">
      {/* Logo/Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">V</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-800">VaidyaVihar</h1>
            <p className="text-sm text-gray-500">Diagnostic ERP</p>
          </div>
        </div>
      </div>

      {/* User Info */}
      {user && (
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 font-semibold">
                {user.first_name?.charAt(0)}{user.last_name?.charAt(0)}
              </span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">
                {user.first_name} {user.last_name}
              </p>
              <p className="text-xs text-gray-500 capitalize">{user.role}</p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Menu */}
      <nav className="p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => handleTabChange(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 text-left rounded-lg transition-colors duration-200 ${
                  activeTab === item.id
                    ? 'bg-blue-50 text-blue-700 border-r-4 border-blue-600'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
        <div className="text-center text-xs text-gray-400">
          <p>VaidyaVihar Diagnostic</p>
          <p>ERP System v2.0</p>
        </div>
      </div>
    </div>
  )
}
