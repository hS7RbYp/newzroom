import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { format, parseISO } from 'date-fns'
import { api } from '../../lib/api'

export default function ArticleReview() {
  const router = useRouter()
  const { id: articleId } = router.query
  const [article, setArticle] = useState(null)
  const [loading, setLoading] = useState(true)
  const [deciding, setDeciding] = useState(false)
  const [reviewerName, setReviewerName] = useState('')
  const [notes, setNotes] = useState('')
  const [rejectionReason, setRejectionReason] = useState('')
  const [showRejectForm, setShowRejectForm] = useState(false)

  useEffect(() => {
    if (articleId) {
      loadArticle()
    }
  }, [articleId])

  const loadArticle = async () => {
    try {
      const res = await api.getArticle(articleId as string)
      setArticle(res.data)
    } catch (error) {
      console.error('Failed to load article:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async () => {
    if (!reviewerName.trim()) {
      alert('Please enter your name')
      return
    }

    setDeciding(true)
    try {
      await api.approveArticle(articleId as string, reviewerName, notes)
      alert('✅ Article approved and published!')
      router.push('/')
    } catch (error) {
      alert('Failed to approve article: ' + error)
    } finally {
      setDeciding(false)
    }
  }

  const handleReject = async () => {
    if (!reviewerName.trim()) {
      alert('Please enter your name')
      return
    }
    if (!rejectionReason.trim()) {
      alert('Please provide a rejection reason')
      return
    }

    setDeciding(true)
    try {
      await api.rejectArticle(articleId as string, reviewerName, rejectionReason)
      alert('Article rejected')
      router.push('/')
    } catch (error) {
      alert('Failed to reject article: ' + error)
    } finally {
      setDeciding(false)
    }
  }

  if (loading || !article) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-gray-600">Loading article...</div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <Link href="/" className="text-blue-600 hover:text-blue-800 mb-4 block">
        ← Back to Queue
      </Link>

      {/* Article metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div className="bg-yellow-50 p-3 rounded border border-yellow-200">
          <div className="text-xs text-yellow-800 font-medium">Confidence</div>
          <div className="text-xl font-bold text-yellow-900">
            {article.confidence_score.toFixed(1)}
          </div>
        </div>
        <div className="bg-green-50 p-3 rounded border border-green-200">
          <div className="text-xs text-green-800 font-medium">Quality</div>
          <div className="text-xl font-bold text-green-900">
            {article.quality_score.toFixed(1)}
          </div>
        </div>
        <div className="bg-blue-50 p-3 rounded border border-blue-200">
          <div className="text-xs text-blue-800 font-medium">Brand Compliant</div>
          <div className="text-xl font-bold text-blue-900">
            {article.brand_compliant ? '✓' : '✗'}
          </div>
        </div>
        <div className="bg-gray-50 p-3 rounded border border-gray-200">
          <div className="text-xs text-gray-800 font-medium">Queued</div>
          <div className="text-xs font-bold text-gray-900">
            {format(parseISO(article.queued_at), 'MMM d')}
          </div>
        </div>
      </div>

      {/* Article content */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{article.title}</h1>
        <div className="text-sm text-gray-600 mb-6 flex gap-4">
          <span>📌 {article.created_at}</span>
          {article.seo_keywords && (
            <span>🏷️ {article.seo_keywords.join(', ')}</span>
          )}
        </div>

        {/* Image preview */}
        {article.image_url && (
          <div className="mb-6">
            <img
              src={article.image_url}
              alt="Article"
              className="w-full h-64 object-cover rounded border border-gray-300"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          </div>
        )}

        {/* Full content */}
        <div className="prose max-w-none text-gray-800 leading-relaxed">
          {article.content_preview}
        </div>

        {/* Facts and entities */}
        {article.entities && article.entities.length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">🔍 Extracted Entities</h3>
            <div className="flex flex-wrap gap-2">
              {article.entities.map((entity, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm"
                >
                  {entity}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Sentiment */}
        {article.sentiment && (
          <div className="mt-4 p-4 bg-gray-50 rounded">
            <p className="text-sm text-gray-600">
              <strong>Sentiment:</strong> {article.sentiment}
            </p>
          </div>
        )}
      </div>

      {/* Decision form */}
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Approval Decision</h2>

        {/* Reviewer info */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Name
          </label>
          <input
            type="text"
            value={reviewerName}
            onChange={(e) => setReviewerName(e.target.value)}
            placeholder="Enter your name"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Approval form */}
        {!showRejectForm && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes (Optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add notes for this approval..."
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        )}

        {/* Rejection form */}
        {showRejectForm && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reason for Rejection *
            </label>
            <textarea
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              placeholder="Explain why this article should not be published..."
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            />
          </div>
        )}

        {/* Buttons */}
        <div className="flex gap-3">
          <button
            onClick={
              showRejectForm
                ? handleReject
                : handleApprove
            }
            disabled={deciding}
            className={`flex-1 px-6 py-3 rounded-lg font-medium text-white transition ${
              showRejectForm
                ? 'bg-red-600 hover:bg-red-700 disabled:bg-red-400'
                : 'bg-green-600 hover:bg-green-700 disabled:bg-green-400'
            }`}
          >
            {deciding
              ? '...Saving...'
              : showRejectForm
              ? '❌ Reject Article'
              : '✅ Approve & Publish'}
          </button>

          {!showRejectForm && (
            <button
              onClick={() => setShowRejectForm(true)}
              className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition"
            >
              ❌ Reject
            </button>
          )}

          {showRejectForm && (
            <button
              onClick={() => setShowRejectForm(false)}
              className="flex-1 px-6 py-3 bg-gray-400 hover:bg-gray-500 text-white rounded-lg font-medium transition"
            >
              ← Back
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
