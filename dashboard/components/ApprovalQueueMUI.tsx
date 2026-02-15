import React, { useState } from 'react'
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Card,
  CardContent,
  Typography,
  Rating,
  LinearProgress,
} from '@mui/material'
import { CheckCircle, Cancel, Edit } from '@mui/icons-material'
import { format } from 'date-fns'

interface Article {
  id: string
  title: string
  category: string
  status: 'pending' | 'approved' | 'rejected'
  score: number
  createdAt: string
  author?: string
  preview?: string
}

interface ApprovalQueueMUIProps {
  articles: Article[]
  onApprove?: (id: string, notes?: string) => void
  onReject?: (id: string, reason?: string) => void
  onRefresh?: () => void
}

export default function ApprovalQueueMUI({ 
  articles, 
  onApprove, 
  onReject, 
  onRefresh 
}: ApprovalQueueMUIProps) {
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [notes, setNotes] = useState('')
  const [dialogMode, setDialogMode] = useState<'approve' | 'reject'>('approve')

  const handleOpenDialog = (article: Article, mode: 'approve' | 'reject') => {
    setSelectedArticle(article)
    setDialogMode(mode)
    setNotes('')
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setSelectedArticle(null)
  }

  const handleConfirm = () => {
    if (!selectedArticle) return

    if (dialogMode === 'approve') {
      onApprove?.(selectedArticle.id, notes)
    } else {
      onReject?.(selectedArticle.id, notes)
    }

    handleCloseDialog()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'success'
      case 'rejected':
        return 'error'
      default:
        return 'warning'
    }
  }

  const getStatusLabel = (status: string) => {
    return status.charAt(0).toUpperCase() + status.slice(1)
  }

  const pendingArticles = articles.filter((a) => a.status === 'pending')

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5" component="h2">
          Approval Queue ({pendingArticles.length} pending)
        </Typography>
        <Button 
          variant="outlined" 
          onClick={onRefresh}
        >
          Refresh
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Title</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Category</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }} align="center">Score</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Date</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }} align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {articles.map((article) => (
              <TableRow 
                key={article.id}
                sx={{
                  '&:hover': { backgroundColor: '#fafafa' },
                  opacity: article.status === 'pending' ? 1 : 0.7,
                }}
              >
                <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {article.title}
                  </Typography>
                  {article.preview && (
                    <Typography variant="caption" color="textSecondary">
                      {article.preview.substring(0, 80)}...
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Chip label={article.category} size="small" variant="outlined" />
                </TableCell>
                <TableCell align="center">
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                    <Rating value={Math.round(article.score / 20)} readOnly size="small" />
                    <Typography variant="caption">{article.score}%</Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={getStatusLabel(article.status)}
                    color={getStatusColor(article.status) as any}
                    size="small"
                    variant="filled"
                  />
                </TableCell>
                <TableCell>
                  {format(new Date(article.createdAt), 'MMM dd, yyyy')}
                </TableCell>
                <TableCell align="center">
                  {article.status === 'pending' && (
                    <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                      <Button
                        size="small"
                        variant="contained"
                        color="success"
                        startIcon={<CheckCircle />}
                        onClick={() => handleOpenDialog(article, 'approve')}
                      >
                        Approve
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        color="error"
                        startIcon={<Cancel />}
                        onClick={() => handleOpenDialog(article, 'reject')}
                      >
                        Reject
                      </Button>
                    </Box>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {articles.length === 0 && (
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="textSecondary">No articles in queue</Typography>
        </Box>
      )}

      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogMode === 'approve' ? 'Approve Article' : 'Reject Article'}
        </DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          {selectedArticle && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                {selectedArticle.title}
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={4}
                label={dialogMode === 'approve' ? 'Notes (optional)' : 'Rejection reason'}
                placeholder={dialogMode === 'approve' ? 'Add any notes...' : 'Why is this being rejected?'}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                variant="outlined"
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleConfirm}
            variant="contained"
            color={dialogMode === 'approve' ? 'success' : 'error'}
          >
            {dialogMode === 'approve' ? 'Approve' : 'Reject'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
