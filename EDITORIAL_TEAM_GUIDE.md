# Editorial Team - Quick Start Guide

## 🎯 Your Mission
Review articles submitted to the Newsroom AI system and decide whether to:
- ✅ **Approve** (publish immediately)
- ❌ **Reject** (send back for revision)

---

## 📋 Getting Started

### 1. Open the Dashboard
Go to: **http://localhost:3000**

You'll see the "Approval Queue" with pending articles.

### 2. Check Queue Statistics (Top Right)
- 🟡 **Pending:** Articles waiting for your review
- ✅ **Approved:** Articles you've approved
- ❌ **Rejected:** Articles you've rejected
- 📊 **Total:** All articles in system

---

## 👀 How to Review an Article

### Step 1: Select an Article
Click the **"Review →"** button on any article in the queue.

### Step 2: Read the Metrics (Top Cards)
```
┌─────────────────────────────────────────────────────┐
│ Confidence: 6.5  │ Quality: 7.2  │ Brand: ✓ │ Queued │
└─────────────────────────────────────────────────────┘
```

**What These Mean:**
-  **Confidence (0-10):** How confident the AI is about this article
   - 🟢 8.5+: Very confident, likely ready to publish
   - 🟡 6.5-8.5: Medium confidence, your judgment matters
   - 🔴 <6.5: Low confidence, AI recommends rejection

- **Quality (0-10):** Article quality score
   - 8+: Excellent writing and structure
   - 6-8: Good quality, minor issues possible
   - <6: Needs work or revision

- **Brand Compliant:** ✓ or ✗
   - ✓ = Matches brand guidelines
   - ✗ = May have brand compliance issues

### Step 3: Review Article Content
- Read the full article title and content
- Review the generated image (AI-generated)
- Check extracted entities (people, places, products mentioned)
- Review sentiment analysis (is tone appropriate?)

### Step 4: Make Your Decision

#### ✅ To Approve:
```
1. Enter your name in "Your Name" field
2. (Optional) Add notes explaining why you approved
3. Click "✓ Approve"
```
✨ Article is immediately published!

#### ❌ To Reject:
```
1. Enter your name in "Your Name" field
2. Enter a rejection reason explaining why
   - Examples:
     - "Fact-checking needed - claims unverified"
     - "Tone doesn't match brand guidelines"
     - "Contains sensitive information needs review"
3. Click "✗ Reject"
```
📧 Editor is notified to revise and resubmit

---

## 🎨 Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│  📰 Newsroom AI - Approval Dashboard      [Live]    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [Pending: 4] [Approved: 12] [Rejected: 2] [Total:18]
│                                                     │
│  ┌─────────────────────────────────────────────────┐ │
│  │ Article Title                    Rating Queued   │ │
│  ├─────────────────────────────────────────────────┤ │
│  │ "Stock Market Reaches Record High"  6.5  Review │ │
│  │ "New Medical Breakthrough Announced" 8.2 Review │ │
│  │ "Tech CEO Announces Acquisition"     7.1  Review│ │
│  │ "Sports Team Wins Championship"      5.8  Review│ │
│  └─────────────────────────────────────────────────┘ │
│                                                     │
│  [🔄 Refresh]                                      │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Understanding the Metrics

### AI Confidence Scoring
The AI analyzes articles on 4 dimensions:

1. **Scout Agent** (Newsworthiness)
   - Is this actually news?
   - Is it timely and relevant?

2. **Prof Agent** (Fact-Checking)
   - Can facts be verified?
   - Are sources credible?

3. **Judge Agent** (Brand Compliance)
   - Does tone match brand?
   - Are guidelines followed?

4. **Scribe Agent** (Content Quality)
   - Is writing clear and professional?
   - Is structure logical?

**Final Score = Average of all 4 + Image Quality**

### Color Coding
- 🟢 **Green (8.5+):** AI highly confident
- 🟡 **Yellow (6.5-8.5):** Medium confidence, reviewer has final say
- 🔴 **Red (<6.5):** AI recommends caution/rejection

---

## ⏰ Workflow Timeline

```
12:00 PM: Articles arrive → Dashboard shows pending
12:05 PM: You review → See metrics and full content
12:10 PM: You approve → Article published immediately
12:15 PM: Dashboard updates → Shows your approval
```

**Queue refreshes automatically every 30 seconds.**
Use the 🔄 **Refresh** button to update manually.

---

## 💡 Pro Tips

### ✅ When to Approve
- Confidence score is 8.0+
- Content is factually accurate
- Tone matches brand voice
- No brand compliance concerns
- Image looks good

### ❌ When to Reject
- Confidence score is below 6.5
- Facts seem questionable
- Tone doesn't match brand
- Claims need better sourcing
- Image is low quality

### ⚠️ When to Ask Questions
- Confidence is 6.5-7.5 (borderline)
- Story is timely but needs verification
- Content is good but needs minor edits
- **Action:** Check with editor before approving/rejecting

---

## 🚨 Escalation

If you're unsure about an article:
1. **Request review** → Add note explaining concern
2. **Contact editor** → Mention article ID and your concern
3. **Look for precedent** → Check similar approved articles

---

## 📱 What If...

### "API Error - Cannot reach backend"
→ Ask IT to verify Flask service is running  
→ Check network connection

### "Article image won't load"
→ Normal - might be upload delay  
→ Check the actual website to verify

### "Metrics look wrong"
→ Report to AI team with article ID  
→ They can retrain that specific classifier

### "Queue not updating"
→ Click 🔄 **Refresh** button  
→ Or wait 30 seconds for auto-update

---

## 📞 Support

**Questions?** Contact the AI Team:
- **Email:** ai-team@newsroom.com
- **Slack:** #approval-queue
- **Dashboard Issues:** Check browser console (F12)

---

## 🎓 Training

### Before You Start
- ✅ Understand the 4-tier confidence system
- ✅ Review 5 previously approved articles
- ✅ Review 5 previously rejected articles
- ✅ Ask questions about edge cases

### Monthly Calibration
- Review your approval/rejection rate
- Compare with team average
- Discuss divergences with editor
- Recalibrate thresholds if needed

---

## 📊 Your Performance Dashboard (Coming Soon)

Track your personal metrics:
- Articles reviewed
- Approval rate
- Average time per review
- Rejections that came back corrected
- Approved articles that had issues

---

**Ready to start reviewing? Head to http://localhost:3000! ✅**

Last Updated: February 15, 2026
