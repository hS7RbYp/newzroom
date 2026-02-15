import React from 'react'
import Link from 'next/link'
import { format, parseISO } from 'date-fns'

interface QueueItem {
  article_id: string
  title: string
  content_preview: string
  confidence_score: number
  quality_score: number
  brand_compliant: boolean
  image_url?: string
  queued_at: string
}

export default function ApprovalQueue({ items }: { items: QueueItem[] }) {
  const getConfidenceColor = (score: number) => {
    if (score > 8.5) return 'bg-green-100 text-green-800'
    if (score > 6.5) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  const getQualityColor = (score: number) => {
    if (score >= 8) return 'bg-green-100 text-green-800'
    if (score >= 6) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50">
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
              Article
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
              Confidence
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
              Quality
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
              Brand
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
              Queued
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
              Action
            </th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr
              key={item.article_id}
              className="border-b border-gray-200 hover:bg-gray-50"
            >
              <td className="px-6 py-4">
                <div>
                  <div className="text-sm font-medium text-gray-900 truncate max-w-xs">
                    {item.title}
                  </div>
                  <div className="text-xs text-gray-600 truncate max-w-xs mt-1">
                    {item.content_preview}
                  </div>
                </div>
              </td>
              <td className="px-6 py-4">
                <span
                  className={`px-3 py-1 rounded text-sm font-medium ${getConfidenceColor(
                    item.confidence_score
                  )}`}
                >
                  {item.confidence_score.toFixed(1)}/10
                </span>
              </td>
              <td className="px-6 py-4">
                <span
                  className={`px-3 py-1 rounded text-sm font-medium ${getQualityColor(
                    item.quality_score
                  )}`}
                >
                  {item.quality_score.toFixed(1)}/10
                </span>
              </td>
              <td className="px-6 py-4">
                <span
                  className={`px-3 py-1 rounded text-sm font-medium ${
                    item.brand_compliant
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {item.brand_compliant ? '✓ Yes' : '✗ No'}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                {format(parseISO(item.queued_at), 'MMM d, HH:mm')}
              </td>
              <td className="px-6 py-4">
                <Link
                  href={`/article/${item.article_id}`}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Review →
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
