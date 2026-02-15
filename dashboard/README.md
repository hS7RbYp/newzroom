# 📊 Newsroom Approval Dashboard

> Next.js-powered dashboard for human approval of AI-generated content

## Overview

The Newsroom Dashboard is a responsive, modern web application built with:

- **Frontend**: Next.js 14, React 18, TypeScript
- **UI Framework**: Material-UI (MUI) 7
- **Styling**: Tailwind CSS + Emotion
- **State Management**: Zustand
- **Deployment**: GitHub Pages (static) or Azure Static Web Apps

### Features

✅ **Article Approval Queue**
- View pending articles for approval
- Real-time queue status
- Bulk approval/rejection
- Article preview

✅ **Category Management**
- Filter articles by category
- Category statistics
- Trend analysis

✅ **Dashboard Analytics**
- Queue statistics
- Approval metrics
- Performance trends
- Status indicators

✅ **Approved Articles Gallery**
- Published content showcase
- Search and filtering
- Engagement metrics

---

## Project Structure

```
dashboard/
├── package.json              # Dependencies
├── next.config.js            # Next.js configuration
├── tsconfig.json             # TypeScript configuration
├── pages/                    # Application pages (SSG/SSR)
│   ├── _app.tsx             # App wrapper
│   ├── index.tsx            # Dashboard home
│   ├── approved.tsx         # Approved articles gallery
│   ├── article/
│   │   └── [id].tsx         # Article detail page
├── components/              # Reusable React components
│   ├── ApprovalQueue.tsx    # Main queue component
│   ├── ApprovalQueueMUI.tsx # Material-UI version
│   ├── ApprovedArticlesGallery.tsx
│   └── QueueStats.tsx       # Statistics widget
├── lib/                     # Utilities and helpers
│   └── api.ts              # API client
├── styles/                 # Global styles
│   └── globals.css
└── public/                 # Static assets
    ├── generated-images/   # AI-generated hero images
    ├── social-cards/      # Social media templates
    └── thumbnails/        # Article thumbnails
```

---

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Azure OpenAI account (for full features)

### Local Development

```bash
# Install dependencies
cd dashboard
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

### Build for Production

```bash
# Build static site
npm run build

# Export to static HTML
npm run export

# Output in 'out' directory
```

---

## Component Architecture

### 1. ApprovalQueue Component

**File**: `components/ApprovalQueue.tsx`

Main component for article approval workflow.

```typescript
interface Article {
  id: string
  title: string
  summary: string
  category: string
  status: 'pending' | 'approved' | 'rejected'
  score: number
  author: string
  createdAt: string
}

interface ApprovalQueueProps {
  articles: Article[]
  onApprove: (id: string) => Promise<void>
  onReject: (id: string) => Promise<void>
  loading: boolean
}
```

**Features**:
- Article list with sorting
- Inline approve/reject actions
- Status indicators
- Score visualization

### 2. QueueStats Component

**File**: `components/QueueStats.tsx`

Displays queue statistics and metrics.

```typescript
interface QueueStats {
  total: number
  pending: number
  approved: number
  rejected: number
  averageScore: number
  pendingRate: number
}
```

### 3. ApprovedArticlesGallery Component

**File**: `components/ApprovedArticlesGallery.tsx`

Gallery view of published articles.

Features:
- Card-based layout
- Search/filter
- Engagement metrics
- Share buttons

---

## Customization Guide

### 1. Customize Layout & Branding

**Theme Colors**
Edit `styles/globals.css`:

```css
:root {
  --primary-color: #1976d2;
  --secondary-color: #dc004e;
  --success-color: #4caf50;
  --warning-color: #ff9800;
  --error-color: #f44336;
}
```

**Logo & Branding**
Edit `components/Header.tsx`:

```typescript
<img src="/logo.png" alt="Newsroom" width={40} height={40} />
<h1>Your Newsroom Name</h1>
```

### 2. Add Custom Pages

Create new page file in `pages/`:

```typescript
// pages/custom.tsx
import { Layout } from '@/components/Layout'

export default function CustomPage() {
  return (
    <Layout title="Custom Page">
      <div>Your content here</div>
    </Layout>
  )
}
```

Update navigation in `components/Navigation.tsx`:

```typescript
const links = [
  { href: '/', label: 'Dashboard' },
  { href: '/approved', label: 'Approved' },
  { href: '/custom', label: 'Custom' },
]
```

### 3. Connect to Real API

**File**: `lib/api.ts`

```typescript
export async function getArticles() {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/articles`
  )
  return response.json()
}

export async function approveArticle(id: string) {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/articles/${id}/approve`,
    { method: 'POST' }
  )
  return response.json()
}
```

Use in component:

```typescript
import { getArticles, approveArticle } from '@/lib/api'

export default function Dashboard() {
  const [articles, setArticles] = useState([])
  
  useEffect(() => {
    getArticles().then(setArticles)
  }, [])
  
  const handleApprove = async (id: string) => {
    await approveArticle(id)
    setArticles(articles.filter(a => a.id !== id))
  }
  
  return <ApprovalQueue articles={articles} onApprove={handleApprove} />
}
```

### 4. Customize Components

**Modify Button Styles**:

```typescript
// components/ApprovalQueue.tsx
<button className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
  Approve
</button>
```

**Add New Fields to Article**:

Update both `lib/api.ts` interface and component props:

```typescript
interface Article {
  id: string
  title: string
  summary: string
  category: string
  status: 'pending' | 'approved' | 'rejected'
  score: number
  author: string
  createdAt: string
  // New fields
  tags: string[]
  imageUrl: string
  contentLength: number
}
```

---

## Styling

### Material-UI Customization

**File**: `pages/_app.tsx`

```typescript
import { ThemeProvider, createTheme } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
    background: { default: '#f5f5f5' },
  },
  typography: {
    fontFamily: 'Inter, system-ui, sans-serif',
  },
})

export default function App({ Component, pageProps }) {
  return (
    <ThemeProvider theme={theme}>
      <Component {...pageProps} />
    </ThemeProvider>
  )
}
```

### Tailwind CSS Classes

Common utility classes:

```html
<!-- Layout -->
<div class="container mx-auto px-4 py-8">
  <!-- Flexbox -->
  <div class="flex justify-between items-center">
    <!-- Grid -->
    <div class="grid grid-cols-3 gap-4">
      <!-- Spacing -->
      <div class="p-4 m-2">
        <!-- Colors -->
        <p class="text-blue-600 bg-blue-100 rounded-lg">Content</p>
      </div>
    </div>
  </div>
</div>
```

---

## Data Flow

### 1. Static Generation (SSG)

For pages that don't change frequently:

```typescript
export async function getStaticProps() {
  const articles = await getArticles()
  return { 
    props: { articles }, 
    revalidate: 3600 // ISR: revalidate every hour
  }
}

export default function Dashboard({ articles }) {
  return <ApprovalQueue articles={articles} />
}
```

### 2. Client-Side Fetching

For real-time updates:

```typescript
export default function Dashboard() {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    getArticles()
      .then(setArticles)
      .finally(() => setLoading(false))
  }, [])
  
  if (loading) return <LoadingSpinner />
  return <ApprovalQueue articles={articles} />
}
```

---

## Environment Variables

Create `.env.local`:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=your-api-key

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_SOCIAL_SHARE=true

# Build Configuration
NEXT_PUBLIC_VERSION=1.0.0
NEXT_PUBLIC_BUILD_DATE=2026-02-15
```

Use in code:

```typescript
const apiUrl = process.env.NEXT_PUBLIC_API_URL
const isAnalyticsEnabled = process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true'
```

---

## Performance Optimization

### Image Optimization

Use Next.js Image component:

```typescript
import Image from 'next/image'

<Image
  src="/article-thumbnail.png"
  alt="Article"
  width={600}
  height={400}
  priority
  loading="lazy"
/>
```

### Code Splitting

Dynamic imports for large components:

```typescript
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(
  () => import('@/components/HeavyComponent'),
  { loading: () => <p>Loading...</p> }
)
```

### Caching Strategy

```typescript
// pages/approved.tsx
export async function getStaticProps() {
  return {
    props: { /* data */ },
    revalidate: 300 // Cache for 5 minutes
  }
}

export async function getStaticPaths() {
  return {
    paths: [], // Lazy generate at request time
    fallback: 'blocking'
  }
}
```

---

## Deployment

### GitHub Pages

```bash
# Build for export
npm run build
next export -o out

# Push to main branch
git add .
git commit -m "Deploy dashboard"
git push origin main

# Automatic deployment via GitHub Actions
```

### Azure Static Web Apps

```bash
# Install SWA CLI
npm install -g @azure/static-web-apps-cli

# Deploy
swa deploy --deployment-token <token>
```

### Vercel (Alternative)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

---

## Troubleshooting

### Build Fails with Module Not Found

```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run build
```

### Images Not Loading

Ensure images are in `public/` folder:

```
public/
  ├── logo.png
  ├── generated-images/
  ├── social-cards/
  └── thumbnails/
```

### API Connection Issues

Check environment variables:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# Verify API is running
curl http://localhost:8000/api/health
```

---

## Dependencies

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@mui/material": "^7.3.8",
    "@emotion/react": "^11.14.0",
    "tailwindcss": "^3.3.0",
    "zustand": "^4.4.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^14.0.0"
  }
}
```

---

## Contributing

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and test locally: `npm run dev`
3. Commit changes: `git commit -am "Add feature"`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

---

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Material-UI Documentation](https://mui.com)
- [Tailwind CSS Documentation](https://tailwindcss.com)
- [TypeScript Documentation](https://www.typescriptlang.org)

---

## License

See [LICENSE](../LICENSE) file for details.

---

**Last Updated**: 2026-02-15
**Version**: 1.0.0
