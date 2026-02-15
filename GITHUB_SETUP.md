# 🚀 GitHub Setup & Deployment Guide

## Step 1: Create GitHub Repository

If you don't have a GitHub repository yet:

1. Go to [github.com/new](https://github.com/new)
2. Enter repository name: `newsroom`
3. Enter description: `Azure Autonomous Newsroom with AI-powered publishing pipeline`
4. Choose visibility: **Public** (recommended) or **Private**
5. **Do NOT** initialize with README (we have our own)
6. Click **Create repository**

## Step 2: Connect Local Repository to GitHub

After creating the repository, you'll see a setup screen with your repository URL. Run these commands:

### Using HTTPS (Easier, no SSH key setup):

```powershell
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/newsroom.git

# Rename main branch (if still on master)
git branch -M main

# Push code to GitHub
git push -u origin main
```

### Using SSH (Secure, requires SSH key):

```powershell
# Add GitHub as remote (SSH)
git remote add origin git@github.com:YOUR_USERNAME/newsroom.git

# Rename main branch
git branch -M main

# Push code
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

## Step 3: Verify Upload

Check your repository on GitHub:
- Go to `https://github.com/YOUR_USERNAME/newsroom`
- Verify all files are there
- Check commit history

## Step 4: Enable GitHub Pages

1. Go to **Settings** → **Pages** (on the left sidebar)
2. Under "Source":
   - Select **Deploy from a branch**
   - Branch: **main**
   - Folder: **/(root)**
3. Click **Save**
4. Your site will be available at: `https://YOUR_USERNAME.github.io/newsroom/`

## Step 5: Configure GitHub Secrets

This is **CRITICAL** for the publishing pipeline to work!

### Get Your API Keys

**Azure OpenAI**:
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your OpenAI resource
3. Go to **Keys and Endpoints**
4. Copy your API key and endpoint URL

**Social Media API Keys** (Optional):
- [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
- [LinkedIn App Console](https://www.linkedin.com/developers/apps)
- [Meta Business Suite](https://business.facebook.com/)

**Slack** (Optional for notifications):
- [Create Slack Webhook](https://api.slack.com/apps/)

### Add Secrets to GitHub

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter each secret below:

#### Required Secrets:

```
Name: OPENAI_API_KEY
Value: sk-xxxxxxxxxxxxx (Your Azure OpenAI API key)

Name: AZURE_OPENAI_ENDPOINT
Value: https://xxxxx.openai.azure.com/ (Your Azure OpenAI endpoint)
```

#### Optional - Social Media Secrets:

**Twitter**:
```
TWITTER_BEARER_TOKEN
TWITTER_API_KEY
TWITTER_API_SECRET
TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET
```

**LinkedIn**:
```
LINKEDIN_ACCESS_TOKEN
LINKEDIN_AUTHOR_URN (format: urn:li:person:xxxxxxxxxx)
```

**Facebook**:
```
FACEBOOK_PAGE_ID
FACEBOOK_ACCESS_TOKEN
```

**Slack**:
```
SLACK_WEBHOOK_URL (https://hooks.slack.com/services/...)
```

### PowerShell Automation (Optional)

Or use the automated setup script:

```powershell
.\setup-publishing-pipeline.ps1 `
    -RepoOwner "your-username" `
    -RepoName "newsroom" `
    -GitHubToken "ghp_xxxxxxxxxxxx" `
    -OpenAIKey "sk-xxxxx" `
    -OpenAIEndpoint "https://xxxxx.openai.azure.com/"
```

**Get GitHub Token**:
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token** → **Generate new token (classic)**
3. Scopes: Check `repo`, `admin:repo_hook`
4. Click **Generate token**
5. Copy immediately (won't show again!)

## Step 6: Test Publishing Pipeline

### Trigger First Build

1. Go to **Actions** tab on GitHub
2. Select **Publish Static Site** workflow
3. Click **Run workflow** dropdown
4. Click **Run workflow** button
5. Monitor the build:
   - Blue circle = In progress
   - Green checkmark = Success ✅
   - Red X = Failed ❌

### Check Build Output

Click on the workflow run to see:
- Build logs
- Deployment status
- Performance audit results

### View Deployed Site

After successful deployment:
- Your site is live at: `https://YOUR_USERNAME.github.io/newsroom/`
- Test by visiting the URL in your browser

## Step 7: Test AI Generation (Optional)

After secrets are configured:

1. Go to **Actions** → **AI Content Generation**
2. Click **Run workflow**
3. Select content type: `article-summary`
4. Click **Run workflow**
5. Wait for completion
6. Download artifacts to see generated content

## Step 8: Test Social Media (Optional)

Requires social media API tokens:

1. Go to **Actions** → **Social Media Publishing**
2. Click **Run workflow**
3. Configure:
   - Platforms: `twitter,linkedin`
   - Content type: `announcement`
4. Click **Run workflow**
5. Monitor logs for posting status

## Troubleshooting

### "Push rejected"

**Error**: `fatal: 'origin' does not appear to be a git repository`

**Solution**: Make sure you ran `git remote add origin https://...`

### "Remote rejected"

**Error**: `updates were rejected because the remote contains work`

**Solution**: 
```powershell
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### GitHub Pages not showing site

**Causes**:
1. Pages not enabled in Settings
2. Site is private (make it public or enable Pages for private repos via GitHub Pro)
3. Branch is not set to `main`
4. All files got pushed

**Fix**:
- Go to Settings → Pages
- Ensure branch is `main` and folder is `/(root)`
- Wait 2-3 minutes
- Force refresh browser (Ctrl+F5)

### Secrets not working in workflows

**Causes**:
1. Secret name typo in workflow vs GitHub
2. Secret not created yet
3. Secret is empty

**Fix**:
- Verify secret exists: Settings → Secrets and variables → Actions
- Check spelling matches workflow exactly
- Verify value is not empty

### Build fails with "Dependencies not found"

**Error**: `npm: not found` or similar

**Solution**: Workflows install dependencies automatically, this shouldn't happen. Check:
- Node version in workflow (should be 18+)
- package.json syntax is valid
- No circular dependencies

## Advanced: Continuous Integration

Pipeline automatically runs on:

| Trigger | Workflow |
|---------|----------|
| `git push` to `main` | Publish Static Site |
| Daily 6 AM UTC | AI Content Generation |
| Weekdays 9 AM/2 PM/7 PM UTC | Social Media Publishing |
| Weekly Sunday noon UTC | AI Asset Generation |

These are automatic and require no manual intervention!

## Next Steps

1. ✅ Create GitHub repository
2. ✅ Push code to GitHub
3. ✅ Enable GitHub Pages
4. ✅ Configure GitHub Secrets
5. ✅ Test publishing pipeline
6. ✅ Monitor first deployment
7. 📊 Review performance metrics
8. 🔧 Customize for your brand

## Quick Reference

| What | Where | Time |
|------|-------|------|
| Create repo | github.com/new | 2 min |
| Push code | `git push -u origin main` | 1 min |
| Enable Pages | Settings → Pages | 1 min |
| Add secrets | Settings → Secrets | 5 min |
| Test build | Actions → Run workflow | 5-10 min |
| View site | yourusername.github.io/newsroom | Instant |

**Total Setup Time: ~20 minutes**

## Support

- [GitHub Docs](https://docs.github.com)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [PUBLISHING_GUIDE.md](./PUBLISHING_GUIDE.md) - Full documentation
- [PUBLISHING_QUICKSTART.md](./PUBLISHING_QUICKSTART.md) - 5-minute setup

---

**Ready?** Let's get your newsroom live! 🚀
