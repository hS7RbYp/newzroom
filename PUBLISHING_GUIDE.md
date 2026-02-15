# 📱 Static Website & Social Media Publishing Guide

## Overview

This guide covers the complete publishing pipeline for the Autonomous Newsroom, including:

- 🏗️ **Static Website Build & Deployment**
- 🤖 **AI-Powered Content Generation**
- 🎨 **Automated Asset & Image Creation**
- 📱 **Social Media Publishing Across Multiple Platforms**

---

## 🚀 Quick Start

### Prerequisites

Before getting started, ensure you have:

1. **GitHub Repository** with the newsroom code
2. **GitHub Secrets** configured (see [Secrets Configuration](#secrets-configuration))
3. **Azure Resources** provisioned:
   - Azure OpenAI (GPT-4o, GPT-4o-mini, DALL-E)
   - Static Web Apps (optional)
4. **Social Media API Keys** (Twitter, LinkedIn, Facebook)

---

## 📦 Publishing Workflows

### 1️⃣ Static Website Publishing

**Workflow**: `.github/workflows/publish-static-site.yml`

#### Triggers

- Push to `main` or `production` branches
- Changes in `dashboard/` folder
- Manual dispatch via GitHub UI

#### Features

✅ **Build Optimization**
- Node.js 18 with caching
- ESLint code quality checks
- Next.js static export

✅ **Deployment Targets**
- GitHub Pages (automatic)
- Azure Static Web Apps (optional)

✅ **Performance Auditing**
- Lighthouse performance metrics
- Security headers validation
- SEO optimization checks

✅ **Notifications**
- Slack integration for success/failure
- Build version tracking
- Deployment metrics

#### Running Manually

1. Go to **Actions** → **Publish Static Site**
2. Click **Run workflow**
3. Select environment: `staging` or `production`
4. View build logs and deployment status

#### Files Generated

```
.next/              # Next.js build output
out/                # Static export (HTML/CSS/JS)
lighthouse-report/  # Performance audit results
```

---

### 2️⃣ AI Content Generation

**Workflow**: `.github/workflows/ai-content-generation.yml`

#### Features

🤖 **Article Summaries**
- GPT-4o powered summarization
- JSON structured output
- 2-3 sentence executive summary
- Key takeaways extraction
- SEO keyword generation

📝 **SEO Metadata Generation**
- Meta titles (60 chars max)
- Meta descriptions (160 chars max)
- Open Graph tags
- Twitter Card tags
- Keyword optimization

📱 **Social Media Snippets**
- Platform-specific formatting
- Twitter (3 variations, 280 chars)
- LinkedIn (professional, up to 3000 chars)
- Facebook (engaging, conversational)
- Instagram (with hashtags)

📰 **Newsletter Content**
- Weekly digest generation
- Featured stories compilation
- Call-to-action optimization
- HTML and text versions

#### Running Manually

1. Go to **Actions** → **AI Content Generation**
2. Click **Run workflow**
3. Select content type:
   - `article-summary`
   - `seo-metadata`
   - `social-snippets`
   - `newsletter`
4. Optional: Enter article topic for custom generation

#### Schedule

```
Daily: 6 AM UTC
```

#### Output Artifacts

All generated content saved as GitHub artifacts:

```json
{
  "generated_summaries.json": "Article summaries",
  "seo_metadata.json": "SEO metadata",
  "social_snippets.json": "Social platform snippets",
  "newsletter.json": "Weekly newsletter"
}
```

---

### 3️⃣ AI Asset & Image Generation

**Workflow**: `.github/workflows/ai-asset-generation.yml`

#### Features

🖼️ **Hero Images (DALL-E 3)**
- 1024x1024px, high-quality
- Professional photography style
- Customizable topics
- Multiple variations

📱 **Social Card Templates**
- Twitter Card (1024×512)
- LinkedIn Card (1200×627)
- Facebook Card (1200×630)
- Instagram Square (1080×1080)

🖻️ **Article Thumbnails**
- Standard (620×360)
- Mobile (480×280)
- Compact (300×200)

⚡ **Asset Optimization**
- ImageMagick compression
- 85% quality JPEG
- PNG optimization
- File size reduction

#### Running

1. Go to **Actions** → **AI Asset & Image Generation**
2. Click **Run workflow**
3. Select:
   - Image type: `hero`, `thumbnail`, `social-card`, etc.
   - Topic for image generation
   - Quantity: number of variations (default: 3)

#### Output Locations

```
dashboard/public/generated-images/     # Hero images
dashboard/public/social-cards/         # Social templates
dashboard/public/thumbnails/           # Article thumbnails
```

---

### 4️⃣ Social Media Publishing

**Workflow**: `.github/workflows/social-media-publish.yml`

#### Supported Platforms

| Platform | Status | Features |
|----------|--------|----------|
| 𝕏 Twitter | ✅ Active | Threaded tweets, scheduled posting |
| 💼 LinkedIn | ✅ Active | Professional content, article promotion |
| 👍 Facebook | ✅ Active | Page posts, engagement targeting |
| 📸 Instagram | ✅ Active | Story posting, carousel support |

#### Content Types

- **announcement**: Product/milestone announcements
- **article-promotion**: Featured article highlights
- **milestone**: Achievement celebrations
- **educational**: Tips, tutorials, insights
- **community-engagement**: Q&A, feedback requests

#### Running

1. Go to **Actions** → **Social Media Publishing**
2. Click **Run workflow**
3. Configure:
   - **platforms**: `twitter`, `linkedin`, `facebook`, `instagram`, or `all`
   - **content_type**: Select from list
   - **schedule_time**: (Optional) HH:MM UTC format

#### Auto-Scheduling

```
Weekdays (Mon-Fri)
- 9 AM UTC
- 2 PM UTC (14:00)
- 7 PM UTC (19:00)
```

#### Generated Content

Each platform receives optimized content:

**Twitter** (3 posts)
```
🚀 Exciting news! Our autonomous newsroom is now live...
```

**LinkedIn** (1 post)
```
We're thrilled to announce the launch of our Azure Autonomous Newsroom...
```

**Facebook** (1 post)
```
Our new Autonomous Newsroom system is transforming how content...
```

#### Analytics Generated

```json
{
  "twitter": {
    "posts_scheduled": 3,
    "estimated_reach": 50000
  },
  "linkedin": {
    "posts_scheduled": 1,
    "estimated_reach": 25000
  },
  "facebook": {
    "posts_scheduled": 1,
    "estimated_reach": 15000
  }
}
```

---

## 🔐 Secrets Configuration

### Required Secrets

Create these GitHub Secrets in your repository settings.

#### Azure OpenAI

```
OPENAI_API_KEY              # Azure OpenAI API key
AZURE_OPENAI_ENDPOINT       # Azure OpenAI endpoint URL
```

#### GitHub Pages

```
GITHUB_TOKEN                # Auto-provided, no setup needed
```

#### Azure Static Web Apps

```
AZURE_STATIC_WEB_APPS_TOKEN # SWA deployment token (optional)
```

#### Social Media

**Twitter/X**
```
TWITTER_BEARER_TOKEN            # Bearer token for API v2
TWITTER_API_KEY                 # API key
TWITTER_API_SECRET              # API secret
TWITTER_ACCESS_TOKEN            # Access token
TWITTER_ACCESS_TOKEN_SECRET     # Access token secret
```

**LinkedIn**
```
LINKEDIN_ACCESS_TOKEN   # OAuth access token
LINKEDIN_AUTHOR_URN     # Your LinkedIn author URN
```

**Facebook**
```
FACEBOOK_PAGE_ID        # Your Facebook page ID
FACEBOOK_ACCESS_TOKEN   # Page access token
```

**Instagram** (via Facebook)
```
INSTAGRAM_BUSINESS_ACCOUNT_ID   # Business account ID
INSTAGRAM_ACCESS_TOKEN          # Access token
```

#### Features

```
SLACK_WEBHOOK_URL       # Slack webhook for notifications
API_URL                 # Production API URL
```

### Setting Up Secrets

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Enter secret name and value
4. Click **Add secret**

---

## 📊 Monitoring & Analytics

### Workflow Status Dashboard

**View Status**: GitHub Actions tab shows all workflow runs

Columns:
- ✅ Success - All steps completed
- ⏳ In Progress - Currently running
- ❌ Failed - Check logs for errors
- ⏭️ Skipped - Conditions not met

### Performance Metrics

Lighthouse audit results available in each build:

```
First Contentful Paint (FCP): < 1.8s ✅
Largest Contentful Paint (LCP): < 2.5s ✅
Speed Index: < 3.4s ✅
Cumulative Layout Shift (CLS): < 0.1 ✅
```

### Social Media Reach

Analytics collected automatically:

```
Twitter:    50,000+ estimated reach
LinkedIn:   25,000+ estimated reach
Facebook:   15,000+ estimated reach
Instagram:  10,000+ estimated reach
────────────────────────────────────
TOTAL:      100,000+ estimated reach
```

---

## 🔧 Configuration Files

### Next.js Config

**File**: `dashboard/next.config.js`

Key settings:
```javascript
output: 'export'                    // Static export
trailingSlash: true                // SEO URLs
images: { unoptimized: true }      // Static images
```

### Lighthouse Config

**File**: `.github/lighthouse-config.json`

Performance thresholds:
```json
{
  "first-contentful-paint": 1800,
  "speed-index": 3400,
  "largest-contentful-paint": 2500,
  "cumulative-layout-shift": 0.1
}
```

---

## 📚 Advanced Usage

### Custom Content Generation

Modify the content dictionary in workflow files:

**File**: `.github/workflows/ai-content-generation.yml`

```python
articles = [
    {
        "title": "Your Article Title",
        "content": "Full article content here...",
        "url": "https://example.com/article"
    }
]
```

### Custom Image Prompts

Edit DALL-E prompts in asset generation workflow:

**File**: `.github/workflows/ai-asset-generation.yml`

```python
prompts = [
    "Your custom image description here",
    "Another style variation",
    "Third variation..."
]
```

### Social Media Scheduling

Modify cron schedule for auto-publishing:

```yaml
schedule:
  - cron: '0 9,14,19 * * 1-5'  # Custom times
```

---

## 🐛 Troubleshooting

### Build Fails

1. **Check Node.js version**: Must be 18+
2. **Clear cache**: Re-run with `--no-cache` flag
3. **Check dependencies**: `npm ci` in dashboard folder

### Deployment Fails

1. **GitHub Pages not enabled**: Settings → Pages
2. **Branch permissions**: Ensure main branch protection allows deployments
3. **Token expired**: Refresh secrets if using OAuth tokens

### AI Generation Fails

1. **API key invalid**: Verify OPENAI_API_KEY secret
2. **Rate limited**: Check Azure OpenAI quota
3. **Model names wrong**: Update model names in workflow

### Social Media Fails

1. **API key expired**: Refresh tokens in GitHub Secrets
2. **Rate limited**: Social platforms have posting limits
3. **Account not verified**: Ensure business accounts for Instagram

---

## 📋 Checklist for First-Time Publishing

- [ ] Create GitHub Secrets (see section above)
- [ ] Enable GitHub Pages in Settings → Pages
- [ ] Configure branch protection rules if needed
- [ ] Create content in dashboard
- [ ] Run "Publish Static Site" workflow manually
- [ ] Verify site deployed at `https://{username}.github.io/{repo}`
- [ ] Generate content with "AI Content Generation"
- [ ] Generate assets with "AI Asset & Image Generation"
- [ ] Publish to social media with "Social Media Publishing"
- [ ] Check analytics and notifications

---

## 📞 Support & Resources

### Documentation

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Next.js Export Guide](https://nextjs.org/docs/app/building-your-application/deploying/static-exports)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Lighthouse Guide](https://developers.google.com/web/tools/lighthouse)

### API Documentation

- [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api)
- [LinkedIn API](https://docs.microsoft.com/en-us/linkedin/marketing/)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)

---

## 🎯 Best Practices

### Content Quality

✅ Always review generated content before publishing
✅ Test articles on multiple devices
✅ Verify SEO metadata before deployment
✅ Check social media content for brand voice alignment

### Performance

✅ Monitor Lighthouse scores in CI/CD
✅ Optimize images before upload
✅ Use semantic HTML for SEO
✅ Implement proper caching headers

### Security

✅ Never commit API keys (use GitHub Secrets)
✅ Keep dependencies updated
✅ Run security scans in main workflow
✅ Validate user input for custom content

### Analytics

✅ Track social media engagement
✅ Monitor page performance metrics
✅ Review user feedback
✅ Iterate on successful content types

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-15 | Initial publishing pipeline setup |

---

**Last Updated**: 2026-02-15
**Maintained By**: Newsroom DevOps Team
