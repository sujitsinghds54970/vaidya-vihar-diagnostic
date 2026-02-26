import React, { useState, useEffect } from 'react'

interface PatientPortalProps {
  activeTab: string
}

interface Appointment {
  id: number
  appointment_number: string
  appointment_date: string
  appointment_time: string
  appointment_type: string
  status: string
  chief_complaint: string
}

interface Patient {
  id: number
  username: string
  email: string
  phone: string
  patient_id: number | null
}

export default function PatientPortal({ activeTab }: PatientPortalProps) {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(false)
  const [showRegister, setShowRegister] = useState(false)
  const [registerData, setRegisterData] = useState({
    username: '',
    email: '',
    phone: '',
    password: ''
  })

  useEffect(() => {
    if (activeTab === 'patient-portal') {
      fetchAppointments()
    }
  }, [activeTab])

  const fetchAppointments = async () => {
    setLoading(true)
    try {
      // For demo, using a sample patient_id
      const response = await fetch('/api/patient-portal/appointments?patient_id=1')
      const data = await response.json()
      if (data.success) {
        setAppointments(data.appointments || [])
      }
    } catch (error) {
      console.error('Error fetching appointments:', error)
    }
    setLoading(false)
  }

  const handleRegister = async () => {
    try {
      const response = await fetch('/api/patient-portal/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerData)
      })
      const data = await response.json()
      if (data.success) {
        alert('Registration successful! Please login.')
        setShowRegister(false)
      } else {
        alert(data.message || 'Registration failed')
      }
    } catch (error) {
      console.error('Error registering:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800'
      case 'completed': return 'bg-blue-100 text-blue-800'
      case 'cancelled': return 'bg-red-100 text-red-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (activeTab !== 'patient-portal') return null

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Patient Portal</h1>
          <p className="text-gray-600">Self-service portal for patients</p>
        </div>
        <div className="space-x-2">
          <button
            onClick={() => setShowRegister(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Register Patient
          </button>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-3xl mb-2">📋</div>
          <div className="font-semibold">View Reports</div>
          <div className="text-sm text-gray-500">Access your lab reports online</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-3xl mb-2">📅</div>
          <div className="font-semibold">Book Appointments</div>
          <div className="text-sm text-gray-500">Schedule appointments online</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-3xl mb-2">💳</div>
          <div className="font-semibold">Payment History</div>
          <div className="text-sm text-gray-500">View payment history</div>
        </div>
      </div>

      {/* Patient Registration Modal */}
      {showRegister && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Patient Registration</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Username</label>
                <input
                  type="text"
                  className="mt-1 block w-full border rounded-md px-3 py-2"
                  value={registerData.username}
                  onChange={(e) => setRegisterData({...registerData, username: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  className="mt-1 block w-full border rounded-md px-3 py-2"
                  value={registerData.email}
                  onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Phone</label>
                <input
                  type="tel"
                  className="mt-1 block w-full border rounded-md px-3 py-2"
                  value={registerData.phone}
                  onChange={(e) => setRegisterData({...registerData, phone: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Password</label>
                <input
                  type="password"
                  className="mt-1 block w-full border rounded-md px-3 py-2"
                  value={registerData.password}
                  onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                />
              </div>
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => setShowRegister(false)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleRegister}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Register
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Appointments */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold">Your Appointments</h2>
        </div>
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : appointments.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No appointments found. Book your first appointment!
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Appointment #</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Date & Time</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Type</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Status</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Reason</th>
              </tr>
            </thead>
            <tbody>
              {appointments.map(apt => (
                <tr key={apt.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{apt.appointment_number}</td>
                  <td className="px-4 py-3">
                    <div>{new Date(apt.appointment_date).toLocaleDateString()}</div>
                    <div className="text-sm text-gray-500">{apt.appointment_time}</div>
                  </td>
                  <td className="px-4 py-3 capitalize">{apt.appointment_type}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs ${getStatusColor(apt.status)}`}>
                      {apt.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">{apt.chief_complaint || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

