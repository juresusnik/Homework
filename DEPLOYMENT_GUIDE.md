# 🚀 GitHub Publishing & Deployment Guide

## Step 1: Initialize Git Repository (If Not Already)

Open PowerShell in your project folder (`C:\Python_Projects\Tecaj`) and run:

```powershell
# Navigate to your project
cd C:\Python_Projects\Tecaj

# Initialize git (if not already done)
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: Brand Sentinel 2023 - Sentiment Analysis App"
```

## Step 2: Create GitHub Repository

1. **Go to GitHub**: https://github.com
2. **Log in** to your account
3. **Click** the `+` icon (top right) → "New repository"
4. **Configure**:
   - Repository name: `brand-sentinel-2023`
   - Description: `Sentiment Analysis Dashboard using Streamlit & Hugging Face`
   - Visibility: **Public** (required for Render free tier)
   - **DO NOT** check "Initialize with README" (we already have one)
5. **Click** "Create repository"

## Step 3: Connect Local Repo to GitHub

GitHub will show you commands. Run these in PowerShell:

```powershell
# Add GitHub as remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/brand-sentinel-2023.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

**Enter credentials** when prompted (username + Personal Access Token).

### Generate Personal Access Token (if needed):
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → Select scopes: `repo` (full control)
3. Copy token and use it as password when git prompts

## Step 4: Verify Upload

1. Refresh your GitHub repository page
2. You should see:
   - ✅ `app.py`
   - ✅ `scraper.py`
   - ✅ `requirements.txt`
   - ✅ `README.md`
   - ✅ `REPORT.md`
   - ✅ `.gitignore`
   - ❌ `data.json` (excluded by .gitignore - will be generated on deployment)
   - ❌ `.venv/` (excluded)

## Step 5: Deploy to Render

### 5.1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. Authorize Render to access your repositories

### 5.2: Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. **Connect repository**: `brand-sentinel-2023`
3. **Configure**:
   - **Name**: `brand-sentinel-2023` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Build Command**: 
     ```
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```
     streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
     ```
   - **Instance Type**: **Free**

4. **Environment Variables** (Optional):
   - Add if needed later

5. **Click** "Create Web Service"

### 5.3: Wait for Deployment
- First build takes 5-10 minutes (downloading AI model)
- Watch the logs for progress
- Status will change to "Live" when ready

### 5.4: Access Your App
- Render provides URL: `https://brand-sentinel-2023.onrender.com`
- **Important**: First load may take 30-60 seconds (cold start on free tier)

## Step 6: Generate Data on Render

Since `data.json` is not in git, you need to generate it on Render:

**Option A: Auto-generate on startup**
Create `startup.sh`:
```bash
#!/bin/bash
python scraper.py
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

Then update Render start command to: `sh startup.sh`

**Option B: Commit data.json** (simpler for this project)
```powershell
# Remove data.json from .gitignore
# Edit .gitignore and remove the line: data.json

# Add and commit
git add data.json .gitignore
git commit -m "Add sample data for deployment"
git push
```

Render will auto-redeploy on push.

## Step 7: Update README Links

Edit `README.md` and add your actual links:

```markdown
## 🔗 Links

- **Live Demo**: https://brand-sentinel-2023.onrender.com
- **GitHub Repo**: https://github.com/YOUR_USERNAME/brand-sentinel-2023
- **Report**: [REPORT.md](REPORT.md)
```

Commit and push:
```powershell
git add README.md REPORT.md
git commit -m "Update deployment links"
git push
```

## Step 8: Test Everything

1. **Visit Live URL**: Open Render URL in browser
2. **Test Navigation**: Click sidebar options
3. **Test Filtering**: Change month slider
4. **Check Visualizations**: Verify bar chart and word cloud appear
5. **Test Multiple Months**: Ensure sentiment analysis works for different months

## Common Issues & Fixes

### Issue: "ModuleNotFoundError" on Render
**Fix**: Ensure all packages are in `requirements.txt`

### Issue: "Port already in use"
**Fix**: Render auto-assigns port via `$PORT` - don't hardcode

### Issue: App crashes with memory error
**Fix**: Free tier has 512MB RAM. Use DistilBERT (not full BERT)

### Issue: Cold starts are slow
**Fix**: Expected on free tier. Upgrade to paid plan or use `render-health-check` endpoint

### Issue: Changes not showing
**Fix**: 
```powershell
git add .
git commit -m "Description of changes"
git push
```
Wait for Render to auto-redeploy (~2-5 minutes)

## Future Updates

To update your app:

```powershell
# Make changes to code
# ... edit files ...

# Commit and push
git add .
git commit -m "Description of what you changed"
git push

# Render auto-deploys
# Check logs at render.com dashboard
```

## Submission Checklist

Before submitting homework:

- [ ] GitHub repo is public
- [ ] README.md has correct links
- [ ] REPORT.md is complete with Gemini prompts
- [ ] Render app is live and working
- [ ] All rubric requirements met:
  - [ ] Web scraping implemented
  - [ ] Streamlit app works
  - [ ] Sentiment analysis functional
  - [ ] Visualizations display
  - [ ] Word cloud bonus implemented
  - [ ] requirements.txt included
  - [ ] Clean git history

## Your Links (Fill In & Submit)

```
GitHub Repository: https://github.com/YOUR_USERNAME/brand-sentinel-2023
Live Render App: https://brand-sentinel-2023.onrender.com
```

## Need Help?

- **Render Docs**: https://render.com/docs/deploy-streamlit
- **Streamlit Docs**: https://docs.streamlit.io/
- **Git Basics**: https://git-scm.com/doc

Good luck! 🚀
