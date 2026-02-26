import React, { useState, useEffect } from 'react'

interface AccountingProps {
  activeTab: string
}

interface Expense {
  id: number
  category: string
  description: string
  amount: number
  total_amount: number
  status: string
  expense_date: string
}

interface Income {
  id: number
  category: string
  description: string
  amount: number
  income_date: string
}

interface FinancialSummary {
  total_income: number
  total_expenses: number
  net_profit: number
  profit_margin: number
  income_by_category?: Record<string, number>
  expenses_by_category?: Record<string, number>
}

export default function Accounting({ activeTab }: AccountingProps) {
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [income, setIncome] = useState<Income[]>([])
  const [summary, setSummary] = useState<FinancialSummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeView, setActiveView] = useState<'expenses' | 'income' | 'summary'>('summary')

  useEffect(() => {
    if (activeTab === 'accounting') {
      fetchExpenses()
      fetchIncome()
      fetchSummary()
    }
  }, [activeTab])

  const fetchExpenses = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/accounting/expenses?period=month')
      const data = await response.json()
      if (data.success) {
        setExpenses(data.expenses || [])
      }
    } catch (error) {
      console.error('Error fetching expenses:', error)
    }
    setLoading(false)
  }

  const fetchIncome = async () => {
    try {
      const response = await fetch('/api/accounting/income?period=month')
      const data = await response.json()
      if (data.success) {
        setIncome(data.income || [])
      }
    } catch (error) {
      console.error('Error fetching income:', error)
    }
  }

  const fetchSummary = async () => {
    try {
      const response = await fetch('/api/accounting/summary?period=month')
      const data = await response.json()
      if (data.success) {
        setSummary(data.summary)
      }
    } catch (error) {
      console.error('Error fetching summary:', error)
    }
  }

  const getCategoryIcon = (category: string) => {
    const icons: Record<string, string> = {
      laboratory: '🧪',
      salaries: '💵',
      rent: '🏢',
      utilities: '⚡',
      equipment: '🔬',
      supplies: '📦',
      marketing: '📢',
      maintenance: '🔧',
      insurance: '🛡️',
      professional_fees: '👔',
      travel: '✈️',
      communication: '📱',
      it_expenses: '💻',
      miscellaneous: '📋'
    }
    return icons[category] || '💰'
  }

  if (activeTab !== 'accounting') return null

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Accounting Module</h1>
          <p className="text-gray-600">Expense tracking and financial management</p>
        </div>
        <div className="space-x-2">
          <button
            onClick={() => setActiveView('summary')}
            className={`px-4 py-2 rounded-lg ${activeView === 'summary' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
          >
            Summary
          </button>
          <button
            onClick={() => setActiveView('expenses')}
            className={`px-4 py-2 rounded-lg ${activeView === 'expenses' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
          >
            Expenses
          </button>
          <button
            onClick={() => setActiveView('income')}
            className={`px-4 py-2 rounded-lg ${activeView === 'income' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
          >
            Income
          </button>
        </div>
      </div>

      {/* Summary View */}
      {activeView === 'summary' && summary && (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">Total Income</div>
              <div className="text-2xl font-bold text-green-600">₹{summary.total_income.toFixed(2)}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">Total Expenses</div>
              <div className="text-2xl font-bold text-red-600">₹{summary.total_expenses.toFixed(2)}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">Net Profit</div>
              <div className={`text-2xl font-bold ${summary.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ₹{summary.net_profit.toFixed(2)}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">Profit Margin</div>
              <div className="text-2xl font-bold text-blue-600">{summary.profit_margin.toFixed(1)}%</div>
            </div>
          </div>

          {/* Category Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Income by Category */}
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-semibold mb-4">Income by Category</h2>
              {summary.income_by_category && Object.keys(summary.income_by_category).length > 0 ? (
                <div className="space-y-3">
                  {Object.entries(summary.income_by_category).map(([cat, amount]) => (
                    <div key={cat} className="flex justify-between items-center">
                      <div className="flex items-center space-x-2">
                        <span>{getCategoryIcon(cat)}</span>
                        <span className="capitalize">{cat}</span>
                      </div>
                      <span className="font-semibold text-green-600">₹{(amount as number).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-gray-500 text-center py-4">No income data</div>
              )}
            </div>

            {/* Expenses by Category */}
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-semibold mb-4">Expenses by Category</h2>
              {summary.expenses_by_category && Object.keys(summary.expenses_by_category).length > 0 ? (
                <div className="space-y-3">
                  {Object.entries(summary.expenses_by_category).map(([cat, amount]) => (
                    <div key={cat} className="flex justify-between items-center">
                      <div className="flex items-center space-x-2">
                        <span>{getCategoryIcon(cat)}</span>
                        <span className="capitalize">{cat.replace('_', ' ')}</span>
                      </div>
                      <span className="font-semibold text-red-600">₹{(amount as number).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-gray-500 text-center py-4">No expense data</div>
              )}
            </div>
          </div>
        </>
      )}

      {/* Expenses View */}
      {activeView === 'expenses' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold">Recent Expenses</h2>
          </div>
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading...</div>
          ) : expenses.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No expenses found</div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Date</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Category</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Description</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Amount</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Status</th>
                </tr>
              </thead>
              <tbody>
                {expenses.slice(0, 10).map(expense => (
                  <tr key={expense.id} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">{new Date(expense.expense_date).toLocaleDateString()}</td>
                    <td className="px-4 py-3">
                      <span className="flex items-center">
                        {getCategoryIcon(expense.category)} <span className="ml-2 capitalize">{expense.category.replace('_', ' ')}</span>
                      </span>
                    </td>
                    <td className="px-4 py-3">{expense.description}</td>
                    <td className="px-4 py-3 font-medium">₹{expense.total_amount.toFixed(2)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded text-xs ${
                        expense.status === 'paid' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {expense.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Income View */}
      {activeView === 'income' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold">Recent Income</h2>
          </div>
          {income.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No income found</div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Date</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Category</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Description</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Amount</th>
                </tr>
              </thead>
              <tbody>
                {income.slice(0, 10).map(inc => (
                  <tr key={inc.id} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">{new Date(inc.income_date).toLocaleDateString()}</td>
                    <td className="px-4 py-3 capitalize">{inc.category}</td>
                    <td className="px-4 py-3">{inc.description}</td>
                    <td className="px-4 py-3 font-medium text-green-600">₹{inc.amount.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}

