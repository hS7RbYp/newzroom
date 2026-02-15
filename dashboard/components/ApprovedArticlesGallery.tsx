import React, { useState } from 'react'
import {
  Box,
  Grid,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Rating,
  LinearProgress,
} from '@mui/material'
import { Search, OpenInNew, Share } from '@mui/icons-material'
import { format } from 'date-fns'

interface ApprovedArticle {
  id: string
  title: string
  category: string
  excerpt: string
  image?: string
  author?: string
  publishedAt: string
  score?: number
  engagementMetrics?: {
    views: number
    shares: number
    likes: number
  }
  url?: string
}

interface ApprovedArticlesGalleryProps {
  articles: ApprovedArticle[]
  onShare?: (id: string) => void
}

export default function ApprovedArticlesGallery({ 
  articles, 
  onShare 
}: ApprovedArticlesGalleryProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedArticle, setSelectedArticle] = useState<ApprovedArticle | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)

  const handleOpenDialog = (article: ApprovedArticle) => {
    setSelectedArticle(article)
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setSelectedArticle(null)
  }

  const filteredArticles = articles.filter(
    (article) =>
      article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      article.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      article.excerpt.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Approved Articles Gallery
        </Typography>
        <TextField
          fullWidth
          placeholder="Search articles..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          variant="outlined"
          size="small"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {filteredArticles.length === 0 ? (
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="textSecondary">
            {articles.length === 0 ? 'No approved articles yet' : 'No articles match your search'}
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {filteredArticles.map((article) => (
            <Grid item xs={12} sm={6} md={4} key={article.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  '&:hover': {
                    boxShadow: 3,
                    transform: 'translateY(-4px)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                {article.image && (
                  <CardMedia
                    component="img"
                    height="200"
                    image={article.image}
                    alt={article.title}
                    sx={{ objectFit: 'cover' }}
                  />
                )}
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ mb: 1 }}>
                    <Chip 
                      label={article.category} 
                      size="small" 
                      variant="outlined"
                      sx={{ mr: 1 }}
                    />
                    {article.score && (
                      <Chip
                        label={`${article.score}% Quality`}
                        size="small"
                        color="success"
                        variant="outlined"
                      />
                    )}
                  </Box>
                  <Typography variant="h6" component="h3" gutterBottom sx={{ lineHeight: 1.3 }}>
                    {article.title}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" paragraph>
                    {article.excerpt}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    {article.author && (
                      <Typography variant="caption" color="textSecondary">
                        By {article.author}
                      </Typography>
                    )}
                  </Box>
                  <Typography variant="caption" color="textSecondary">
                    {format(new Date(article.publishedAt), 'MMM dd, yyyy')}
                  </Typography>

                  {article.engagementMetrics && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" sx={{ display: 'block', mb: 1 }}>
                        Engagement
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                        <Typography variant="caption">
                          📊 {article.engagementMetrics.views.toLocaleString()} views
                        </Typography>
                        <Typography variant="caption">
                          ❤️ {article.engagementMetrics.likes.toLocaleString()} likes
                        </Typography>
                        <Typography variant="caption">
                          🔄 {article.engagementMetrics.shares.toLocaleString()} shares
                        </Typography>
                      </Box>
                    </Box>
                  )}
                </CardContent>
                <CardActions>
                  <Button 
                    size="small" 
                    onClick={() => handleOpenDialog(article)}
                  >
                    View Details
                  </Button>
                  {article.url && (
                    <Button 
                      size="small"
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      endIcon={<OpenInNew />}
                    >
                      Read
                    </Button>
                  )}
                  <Button
                    size="small"
                    startIcon={<Share />}
                    onClick={() => onShare?.(article.id)}
                  >
                    Share
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{selectedArticle?.title}</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          {selectedArticle && (
            <Box>
              {selectedArticle.image && (
                <CardMedia
                  component="img"
                  image={selectedArticle.image}
                  alt={selectedArticle.title}
                  sx={{ mb: 2, borderRadius: 1 }}
                />
              )}
              <Box sx={{ mb: 2 }}>
                <Chip 
                  label={selectedArticle.category} 
                  size="small"
                  sx={{ mr: 1 }}
                />
                {selectedArticle.score && (
                  <Chip
                    label={`${selectedArticle.score}% Quality`}
                    size="small"
                    color="success"
                  />
                )}
              </Box>
              <Typography variant="body1" paragraph>
                {selectedArticle.excerpt}
              </Typography>
              {selectedArticle.author && (
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Author: {selectedArticle.author}
                </Typography>
              )}
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Published: {format(new Date(selectedArticle.publishedAt), 'PPP')}
              </Typography>
              {selectedArticle.engagementMetrics && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Engagement Metrics
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box>
                      <Typography variant="caption">Views</Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={Math.min((selectedArticle.engagementMetrics.views / 10000) * 100, 100)} 
                      />
                      <Typography variant="caption">
                        {selectedArticle.engagementMetrics.views.toLocaleString()}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption">Likes</Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={Math.min((selectedArticle.engagementMetrics.likes / 1000) * 100, 100)} 
                      />
                      <Typography variant="caption">
                        {selectedArticle.engagementMetrics.likes.toLocaleString()}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption">Shares</Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={Math.min((selectedArticle.engagementMetrics.shares / 500) * 100, 100)} 
                      />
                      <Typography variant="caption">
                        {selectedArticle.engagementMetrics.shares.toLocaleString()}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          {selectedArticle?.url && (
            <Button 
              href={selectedArticle.url}
              target="_blank"
              rel="noopener noreferrer"
              endIcon={<OpenInNew />}
            >
              Read Full Article
            </Button>
          )}
          <Button onClick={handleCloseDialog}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
