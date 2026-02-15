import React from 'react'

interface Stats {
  pending: number
  approved: number
  rejected: number
  total: number
}

export default function QueueStats({ stats }: { stats: Stats }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {/* Pending */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="text-sm font-medium text-yellow-800">Pending Review</div>
        <div className="text-3xl font-bold text-yellow-900 mt-2">{stats.pending}</div>
        <div className="text-xs text-yellow-700 mt-2">Articles awaiting approval</div>
      </div>

      {/* Approved */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="text-sm font-medium text-green-800">Approved</div>
        <div className="text-3xl font-bold text-green-900 mt-2">{stats.approved}</div>
        <div className="text-xs text-green-700 mt-2">Published stories</div>
      </div>

      {/* Rejected */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="text-sm font-medium text-red-800">Rejected</div>
        <div className="text-3xl font-bold text-red-900 mt-2">{stats.rejected}</div>
        <div className="text-xs text-red-700 mt-2">Not suitable for publication</div>
      </div>

      {/* Total */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="text-sm font-medium text-blue-800">Total</div>
        <div className="text-3xl font-bold text-blue-900 mt-2">{stats.total}</div>
        <div className="text-xs text-blue-700 mt-2">Articles processed</div>
      </div>
    </div>
  )
}
