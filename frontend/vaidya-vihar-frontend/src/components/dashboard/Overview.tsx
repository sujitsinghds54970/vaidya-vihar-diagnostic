import React, { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'

export default function Overview() {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    totalPatients: 0,
    todayVisits: 0,
    totalStaff: 0,
    revenue: 0
  })

  useEffect(() => {
    // Fetch dashboard statistics
    const fetchStats = async () => {
      try {
        // This would typically call your API
        // const response = await fetch('/api/dashboard/stats')
        // const data = await response.json()
        
        // For now, using mock data
        setStats({
          totalPatients: 1247,
          todayVisits: 23,
          totalStaff: 15,
          revenue: 45680
        })
      } catch (error) {
        console.error('Error fetching stats:', error)
      }
    }

    fetchStats()
  }, [])

  const statCards = [
    { title: 'Total Patients', value: stats.totalPatients, icon: '👥', color: 'bg-blue-500' },
    { title: "Today's Visits", value: stats.todayVisits, icon: '📅', color: 'bg-green-500' },
    { title: 'Total Staff', value: stats.totalStaff, icon: '👨‍⚕️', color: 'bg-purple-500' },
    { title: 'Monthly Revenue', value: `₹${stats.revenue.toLocaleString()}`, icon: '💰', color: 'bg-yellow-500' },
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {user?.first_name}!
            </h1>
            <p className="text-gray-600 mt-1">
              Here's what's happening at VaidyaVihar Diagnostic today.
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Current Branch</p>
            <p className="text-lg font-semibold text-blue-600">
              {user?.branch_id ? `Branch #${user.branch_id}` : 'Main Branch'}
            </p>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
              </div>
              <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center`}>
                <span className="text-white text-xl">{stat.icon}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
            <span className="text-2xl">📝</span>
            <div className="text-left">
              <p className="font-medium text-blue-900">Daily Entry</p>
              <p className="text-sm text-blue-600">Record patient visits</p>
            </div>
          </button>
          
          <button className="flex items-center space-x-3 p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
            <span className="text-2xl">👥</span>
            <div className="text-left">
              <p className="font-medium text-green-900">Add Patient</p>
              <p className="text-sm text-green-600">Register new patient</p>
            </div>
          </button>
          
          <button className="flex items-center space-x-3 p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
            <span className="text-2xl">📊</span>
            <div className="text-left">
              <p className="font-medium text-purple-900">View Reports</p>
              <p className="text-sm text-purple-600">Export monthly data</p>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-4">
          <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm text-gray-900">New patient registered: John Doe</p>
              <p className="text-xs text-gray-500">2 minutes ago</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm text-gray-900">Daily entry completed for 15 patients</p>
              <p className="text-xs text-gray-500">1 hour ago</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm text-gray-900">Monthly report generated</p>
              <p className="text-xs text-gray-500">3 hours ago</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
