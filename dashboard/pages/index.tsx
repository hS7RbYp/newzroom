import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { format } from 'date-fns'
import { Container, Box, Tabs, Tab, Paper } from '@mui/material'
import ApprovalQueueMUI from '../components/ApprovalQueueMUI'
import ApprovedArticlesGallery from '../components/ApprovedArticlesGallery'
import QueueStats from '../components/QueueStats'
import { api } from '../lib/api'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

export default function DashboardHome() {
  const [tabValue, setTabValue] = useState(0)
  const [stats, setStats] = useState({ pending: 0, approved: 0, rejected: 0, total: 0 })
  const [queue, setQueue] = useState([])
  const [approved, setApproved] = useState([])
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
      const [statsRes, queueRes, approvedRes] = await Promise.all([
        api.getStats().catch(() => ({ data: stats })),
        api.getQueue().catch(() => ({ data: [] })),
        api.getApproved?.().catch(() => ({ data: [] })) || Promise.resolve({ data: [] }),
      ])
      setStats(statsRes.data)
      setQueue(queueRes.data)
      setApproved(approvedRes.data)
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

  const handleApprove = async (id: string, notes?: string) => {
    try {
      await api.approveArticle?.(id, notes)
      handleRefresh()
    } catch (error) {
      console.error('Failed to approve:', error)
    }
  }

  const handleReject = async (id: string, reason?: string) => {
    try {
      await api.rejectArticle?.(id, reason)
      handleRefresh()
    } catch (error) {
      console.error('Failed to reject:', error)
    }
  }

  const handleShare = async (id: string) => {
    try {
      await api.shareArticle?.(id)
      alert('Article shared successfully!')
    } catch (error) {
      console.error('Failed to share:', error)
    }
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <QueueStats stats={stats} loading={loading} />

      <Paper sx={{ mt: 4 }}>
        <Tabs 
          value={tabValue} 
          onChange={(e, newValue) => setTabValue(newValue)}
          aria-label="dashboard tabs"
        >
          <Tab label={`Approval Queue (${queue.length})`} id="tab-0" aria-controls="tabpanel-0" />
          <Tab label={`Approved (${approved.length})`} id="tab-1" aria-controls="tabpanel-1" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <ApprovalQueueMUI 
            articles={queue}
            onApprove={handleApprove}
            onReject={handleReject}
            onRefresh={handleRefresh}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <ApprovedArticlesGallery 
            articles={approved}
            onShare={handleShare}
          />
        </TabPanel>
      </Paper>
    </Container>
  )
}
