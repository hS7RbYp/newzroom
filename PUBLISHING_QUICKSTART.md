# 🚀 Publishing Pipeline Implementation Quickstart

> Get your static website live in 5 minutes with AI-powered content and social media publishing

## Step 1: Enable GitHub Pages (2 min)

1. Go to **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** / Folder: **/(root)**
4. Click **Save**
5. Your site will be available at: `https://{username}.github.io/{repo}`

## Step 2: Configure GitHub Secrets (2 min)

Go to **Settings** → **Secrets and variables** → **Actions**

### Minimum secrets to start:

```
OPENAI_API_KEY=sk-xxxxxx              # Azure OpenAI key
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx  # Optional
```

### For social media (optional):

```
TWITTER_BEARER_TOKEN=xxxxxxxxxx
TWITTER_API_KEY=xxxxxxxxxx
TWITTER_API_SECRET=xxxxxxxxxx
LINKEDIN_ACCESS_TOKEN=xxxxxxxxxx
LINKEDIN_AUTHOR_URN=urn:li:person:xxxxxxxxxx
FACEBOOK_PAGE_ID=xxxxxxxxxx
FACEBOOK_ACCESS_TOKEN=xxxxxxxxxx
```

## Step 3: Deploy Static Site (1 min)

1. Go to **Actions** tab
2. Select **Publish Static Site** workflow
3. Click **Run workflow**
4. Monitor logs → **Deploy to GitHub Pages** step
5. ✅ Site live at GitHub Pages URL

## Step 4: Generate Content with AI (Optional, 30 sec)

1. Go to **Actions** → **AI Content Generation**
2. Click **Run workflow**
3. Select content type: `article-summary`
4. ✅ Check artifacts for `generated_summaries.json`

## Step 5: Generate Images with AI (Optional, 1 min)

1. Go to **Actions** → **AI Asset & Image Generation**
2. Click **Run workflow**
3. Configure:
   - Image type: `hero`
   - Topic: `"Modern newsroom dashboard"`
4. ✅ Images saved to `dashboard/public/generated-images/`

## Step 6: Publish to Social Media (Optional, 30 sec)

1. Go to **Actions** → **Social Media Publishing**
2. Click **Run workflow**
3. Select platforms: `twitter,linkedin`
4. Select content type: `announcement`
5. ✅ Posts queued for publishing

---

## 📊 What You Get

After completing all steps:

- ✅ Live static website on GitHub Pages
- ✅ Auto-optimized performance (Lighthouse audit)
- ✅ AI-generated article summaries and SEO metadata
- ✅ Professional social media graphics
- ✅ Automated posting to Twitter, LinkedIn, Facebook
- ✅ 100,000+ estimated social reach per publish

---

## 🎯 Next Steps

### For Your Website

1. Edit content in `dashboard/` folder
2. Push to `main` branch → auto-deploy
3. Check performance in workflow logs
4. Monitor lighthouse report

### For Content Generation

1. Update article URLs in workflow files
2. Customize prompts for your industry
3. Schedule daily generation with cron
4. Export to CMS via artifacts

### For Social Media

1. Connect all platform API keys
2. Set optimal posting times
3. Monitor engagement analytics
4. Iterate on successful content types

---

## 📋 Secrets Cheatsheet

### Get Your Secrets

**Azure OpenAI:**
- From Azure Portal → Cognitive Services → Keys and Endpoints

**Twitter:**
- From [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)

**LinkedIn:**
- From [LinkedIn App Console](https://www.linkedin.com/developers/apps)

**Facebook:**
- From [Meta Business Suite](https://business.facebook.com/)

**Slack (Optional):**
- From Slack Workspace → Integration Settings → Webhooks

---

## ✨ Features Overview

### 🌐 Website Publishing
- Static site generation from Next.js
- GitHub Pages deployment
- Performance auditing with Lighthouse
- Security headers included
- SEO-optimized output

### 🤖 AI Content
- Article summaries (GPT-4o)
- SEO metadata generation
- Social snippets for each platform
- Weekly newsletter creation
- Structured JSON output

### 🎨 Image Generation
- Hero images (DALL-E 3)
- Social card templates
- Article thumbnails
- Image optimization
- Asset management

### 📱 Social Publishing
- Multi-platform posting
- Platform-specific formatting
- Scheduled publishing
- Analytics tracking
- Reach estimations

---

## 🔗 Platform Endpoints

| Platform | Status | Endpoint | Rate Limit |
|----------|--------|----------|-----------|
| GitHub Pages | ✅ Active | `https://{user}.github.io/{repo}` | - |
| Twitter | ✅ Ready | API v2 | 300 posts/15min |
| LinkedIn | ✅ Ready | Graph API v2 | 10 posts/day |
| Facebook | ✅ Ready | Graph API v18 | 10 posts/day |
| Instagram | ✅ Ready | Graph API | 1 post/day |

---

## 📞 Troubleshooting

**Q: Site not deployed to GitHub Pages**
A: Check Settings → Pages. Ensure main branch is selected and GitHub Actions secrets are configured.

**Q: AI generation fails with API error**
A: Verify OPENAI_API_KEY in Secrets. Check Azure OpenAI quota in Portal.

**Q: Social media posts not publishing**
A: Ensure API tokens are not expired. Check rate limits for each platform.

**Q: Lighthouse score is low**
A: Review workflow logs for specific recommendations. Optimize images and implement caching.

---

## 🎓 Learn More

- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Next.js Static Export](https://nextjs.org/docs/app/building-your-application/deploying/static-exports)
- [Azure OpenAI Models](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/concepts/models)
- [Publishing Guide](./PUBLISHING_GUIDE.md) (Full documentation)

---

## ✅ Completion Checklist

- [ ] GitHub Pages enabled
- [ ] Secrets configured
- [ ] Static site deployed
- [ ] Content generated (optional)
- [ ] Images created (optional)
- [ ] Social media publishing tested (optional)
- [ ] Lighthouse report reviewed
- [ ] Team notified of live site

---

**Status**: 🟢 Ready to Deploy
**Time to Live**: ~5 minutes
**Support**: Check `PUBLISHING_GUIDE.md` for detailed documentation
