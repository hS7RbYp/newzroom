import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { format } from 'date-fns'
import { api } from '../lib/api'
import QueueStats from '../components/QueueStats'
import ApprovalQueue from '../components/ApprovalQueue'

export default function DashboardHome() {
  const [stats, setStats] = useState({ pending: 0, approved: 0, rejected: 0, total: 0 })
  const [queue, setQueue] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadData()
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [statsRes, queueRes] = await Promise.all([
        api.getStats(),
        api.getQueue(),
      ])
      setStats(statsRes.data)
      setQueue(queueRes.data)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRefresh = () => {
    setRefreshing(true)
    loadData()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-gray-600">Loading approval queue...</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header with refresh button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Approval Queue</h2>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          {refreshing ? 'Refreshing...' : '🔄 Refresh'}
        </button>
      </div>

      {/* Statistics Cards */}
      <QueueStats stats={stats} />

      {/* Main Queue Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Pending Review ({stats.pending})
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Articles waiting for human approval
          </p>
        </div>

        {queue.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-500">
            <p className="text-lg">✅ All caught up! No articles pending review.</p>
          </div>
        ) : (
          <ApprovalQueue items={queue} />
        )}
      </div>

      {/* Submit New Article Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Submit New Article</h3>
        <p className="text-blue-700 mb-4">
          Submit articles via API: POST /api/articles/submit
        </p>
        <pre className="bg-white p-4 rounded text-sm overflow-x-auto border border-blue-200">
          {`curl -X POST http://localhost:8000/api/articles/submit \\
  -H "Content-Type: application/json" \\
  -d '{
    "title": "Article Title",
    "content": "Full article content...",
    "source": "News Source",
    "article_url": "https://..."
  }'`}
        </pre>
      </div>
    </div>
  )
}
